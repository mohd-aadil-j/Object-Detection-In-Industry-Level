from django.http import JsonResponse
from django.http import HttpResponse
import os
from tempfile import NamedTemporaryFile
from django.utils import timezone
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import csv

from .image_processing import process_image
from .models import InspectionProcess, InspectionRecord, InspectionSettings, ProcessState
from .record_serializers import InspectionRecordSerializer
from .serializers import InspectionSettingsSerializer
from .services import classify_sequence

def health_check(request):
    return JsonResponse({"status": "ok", "service": "inspection-api"})


class InspectionSettingsView(APIView):
    def get(self, request):
        settings = InspectionSettings.objects.filter(is_active=True).first()
        if settings is None:
            return Response({"detail": "No active inspection settings found."}, status=404)
        return Response(InspectionSettingsSerializer(settings).data)

    def post(self, request):
        serializer = InspectionSettingsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        InspectionSettings.objects.filter(is_active=True).update(is_active=False)
        settings = serializer.save(is_active=True)
        return Response(
            InspectionSettingsSerializer(settings).data,
            status=status.HTTP_201_CREATED,
        )


def _active_process():
    return InspectionProcess.objects.order_by("-updated_at").first()


class ProcessControlView(APIView):
    action_states = {
        "start": ProcessState.RUNNING,
        "pause": ProcessState.PAUSED,
        "resume": ProcessState.RUNNING,
        "stop": ProcessState.STOPPED,
    }

    def post(self, request, action):
        if action not in self.action_states:
            return Response({"detail": "Unknown process action."}, status=400)
        process = _active_process()
        if action == "start" or process is None:
            process = InspectionProcess.objects.create(
                state=ProcessState.RUNNING,
                started_at=timezone.now(),
            )
        elif action == "pause" and process.state != ProcessState.RUNNING:
            return Response({"detail": "Only a running process can be paused."}, status=409)
        elif action == "resume" and process.state != ProcessState.PAUSED:
            return Response({"detail": "Only a paused process can be resumed."}, status=409)
        elif action == "stop" and process.state == ProcessState.STOPPED:
            return Response({"detail": "The process is already stopped."}, status=409)
        else:
            process.state = self.action_states[action]
            process.save(update_fields=["state", "updated_at"])
        return Response({"state": process.state, "process_id": process.id})


class ProcessInspectionView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        process = _active_process()
        if process is None or process.state != ProcessState.RUNNING:
            return Response(
                {"detail": "Start the inspection process before submitting an image."},
                status=409,
            )
        image = request.FILES.get("image")
        if image is None:
            return Response({"detail": "An image file is required."}, status=400)

        settings = InspectionSettings.objects.filter(is_active=True).first()
        if settings is None:
            return Response({"detail": "No active inspection settings found."}, status=409)

        record_data = {
            "component_serial_number": request.data.get("component_serial_number", ""),
            "component_name": settings.component_name,
            "operator_id": request.data.get("operator_id", ""),
            "operator_name": request.data.get("operator_name", ""),
            "expected_sequence": settings.expected_sequence,
            "expected_wire_count": len(settings.expected_sequence),
        }
        if not record_data["component_serial_number"] or not record_data["operator_id"]:
            return Response(
                {"detail": "Component serial number and operator ID are required."},
                status=400,
            )

        try:
            temporary_image = NamedTemporaryFile(suffix=".png", delete=False)
            try:
                for chunk in image.chunks():
                    temporary_image.write(chunk)
                temporary_image.flush()
                temporary_image.close()
                processed = process_image(
                    temporary_image.name,
                    settings.layer_distance,
                )
            finally:
                if not temporary_image.closed:
                    temporary_image.close()
                os.unlink(temporary_image.name)
        except ValueError as error:
            return Response({"detail": str(error)}, status=400)

        classification = classify_sequence(
            settings.expected_sequence,
            processed.sequence,
        )
        record = InspectionRecord.objects.create(
            **record_data,
            detected_sequence=processed.sequence,
            detected_wire_count=len(processed.wires),
            result=classification.result,
            error_details=classification.error_details,
            image=image,
        )
        return Response(InspectionRecordSerializer(record).data, status=201)


class InspectionHistoryView(APIView):
    def get(self, request):
        records = InspectionRecord.objects.order_by("-tested_at")
        if request.query_params.get("export") == "csv":
            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="inspection-history.csv"'
            writer = csv.writer(response)
            writer.writerow(
                [
                    "serial_number",
                    "component_name",
                    "operator_id",
                    "operator_name",
                    "expected_sequence",
                    "detected_sequence",
                    "result",
                    "tested_at",
                ]
            )
            for record in records:
                writer.writerow(
                    [
                        record.component_serial_number,
                        record.component_name,
                        record.operator_id,
                        record.operator_name,
                        " - ".join(record.expected_sequence),
                        " - ".join(record.detected_sequence),
                        record.result,
                        record.tested_at.isoformat(),
                    ]
                )
            return response
        return Response(InspectionRecordSerializer(records, many=True).data)
