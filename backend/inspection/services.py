from dataclasses import dataclass

from .models import InspectionResult


@dataclass(frozen=True)
class Classification:
    result: str
    error_details: str = ""


def classify_sequence(expected_sequence, detected_sequence):
    expected_count = len(expected_sequence)
    detected_count = len(detected_sequence)

    if detected_count != expected_count:
        return Classification(
            result=InspectionResult.INSPECTION_ERROR,
            error_details=(
                f"Expected {expected_count} wires but detected {detected_count}."
            ),
        )

    normalized_expected = [color.strip().lower() for color in expected_sequence]
    normalized_detected = [color.strip().lower() for color in detected_sequence]
    if normalized_detected == normalized_expected:
        return Classification(result=InspectionResult.PASS)
    return Classification(result=InspectionResult.REWORK)
