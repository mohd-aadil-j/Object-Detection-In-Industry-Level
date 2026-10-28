from django.test import TestCase
from rest_framework.test import APIClient

from .models import InspectionResult
from .services import classify_sequence


class SequenceClassificationTests(TestCase):
    def test_matching_sequence_passes(self):
        classification = classify_sequence(["yellow", "blue"], ["YELLOW", "blue"])
        self.assertEqual(classification.result, InspectionResult.PASS)

    def test_wrong_order_is_rework(self):
        classification = classify_sequence(["yellow", "blue"], ["blue", "yellow"])
        self.assertEqual(classification.result, InspectionResult.REWORK)

    def test_wrong_wire_count_is_inspection_error(self):
        classification = classify_sequence(["yellow", "blue"], ["yellow"])
        self.assertEqual(classification.result, InspectionResult.INSPECTION_ERROR)


class InspectionSettingsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_settings_requires_at_least_two_colors(self):
        response = self.client.post(
            "/api/settings/",
            {"component_name": "Connector", "expected_sequence": ["red"]},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_settings_returns_dynamic_wire_count(self):
        response = self.client.post(
            "/api/settings/",
            {
                "component_name": "Connector",
                "expected_sequence": ["Yellow", "Blue", "Black", "Red"],
                "layer_distance": 20,
                "color_tolerance": 25,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["expected_wire_count"], 4)
        self.assertEqual(response.data["expected_sequence"], ["yellow", "blue", "black", "red"])
