from io import BytesIO

import cv2
import numpy as np
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIClient

from .models import InspectionRecord, InspectionResult


def image_file(colors):
    image = np.full((120, 120 * len(colors), 3), 255, dtype=np.uint8)
    for index, color in enumerate(colors):
        cv2.rectangle(image, (index * 120 + 20, 20), (index * 120 + 90, 100), color, -1)
    encoded, buffer = cv2.imencode(".png", image)
    return SimpleUploadedFile("inspection.png", buffer.tobytes(), content_type="image/png")


class InspectionApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.post(
            "/api/settings/",
            {
                "component_name": "Connector",
                "expected_sequence": ["yellow", "blue"],
            },
            format="json",
        )
        self.client.post("/api/process/start/")

    def test_processes_and_persists_pass(self):
        response = self.client.post(
            "/api/inspection/process/",
            {
                "component_serial_number": "C-001",
                "operator_id": "OP-1",
                "operator_name": "Operator One",
                "image": image_file([(0, 255, 255), (255, 0, 0)]),
            },
            format="multipart",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["result"], InspectionResult.PASS)
        self.assertEqual(InspectionRecord.objects.count(), 1)

    def test_wrong_count_is_persisted_as_inspection_error(self):
        response = self.client.post(
            "/api/inspection/process/",
            {
                "component_serial_number": "C-002",
                "operator_id": "OP-1",
                "operator_name": "Operator One",
                "image": image_file([(0, 255, 255)]),
            },
            format="multipart",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["result"], InspectionResult.INSPECTION_ERROR)

    def test_pause_blocks_inspection_until_resume(self):
        self.client.post("/api/process/pause/")
        paused_response = self.client.post(
            "/api/inspection/process/",
            {
                "component_serial_number": "C-003",
                "operator_id": "OP-1",
                "image": image_file([(0, 255, 255), (255, 0, 0)]),
            },
            format="multipart",
        )
        self.assertEqual(paused_response.status_code, 409)
        self.client.post("/api/process/resume/")
        resumed_response = self.client.post(
            "/api/inspection/process/",
            {
                "component_serial_number": "C-003",
                "operator_id": "OP-1",
                "image": image_file([(0, 255, 255), (255, 0, 0)]),
            },
            format="multipart",
        )
        self.assertEqual(resumed_response.status_code, 201)

    def test_history_returns_records_and_csv_export(self):
        self.client.post(
            "/api/inspection/process/",
            {
                "component_serial_number": "C-004",
                "operator_id": "OP-1",
                "image": image_file([(0, 255, 255), (255, 0, 0)]),
            },
            format="multipart",
        )
        response = self.client.get("/api/inspection/history/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        csv_response = self.client.get("/api/inspection/history/?export=csv")
        self.assertEqual(csv_response.status_code, 200)
        self.assertIn("serial_number", csv_response.content.decode())
