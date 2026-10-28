from rest_framework import serializers

from .models import InspectionRecord


class InspectionRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionRecord
        fields = [
            "id",
            "component_serial_number",
            "component_name",
            "operator_id",
            "operator_name",
            "expected_sequence",
            "detected_sequence",
            "expected_wire_count",
            "detected_wire_count",
            "result",
            "error_details",
            "image",
            "processed_image",
            "tested_at",
        ]
        read_only_fields = fields
