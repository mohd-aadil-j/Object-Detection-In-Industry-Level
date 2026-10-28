from rest_framework import serializers

from .models import InspectionSettings


class InspectionSettingsSerializer(serializers.ModelSerializer):
    expected_wire_count = serializers.SerializerMethodField()

    class Meta:
        model = InspectionSettings
        fields = [
            "id",
            "component_name",
            "expected_sequence",
            "expected_wire_count",
            "layer_distance",
            "color_tolerance",
            "is_active",
            "updated_at",
        ]
        read_only_fields = ["id", "expected_wire_count", "updated_at"]

    def get_expected_wire_count(self, obj):
        return len(obj.expected_sequence)

    def validate_expected_sequence(self, value):
        if not isinstance(value, list) or len(value) < 2:
            raise serializers.ValidationError(
                "Expected sequence must contain at least two colors."
            )
        if any(not isinstance(color, str) or not color.strip() for color in value):
            raise serializers.ValidationError(
                "Each expected color must be a non-empty string."
            )
        return [color.strip().lower() for color in value]
