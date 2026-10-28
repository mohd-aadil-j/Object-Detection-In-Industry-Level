from django.db import models


class InspectionResult(models.TextChoices):
    PASS = "PASS", "Pass"
    REWORK = "REWORK", "Rework"
    INSPECTION_ERROR = "INSPECTION_ERROR", "Inspection Error"


class ProcessState(models.TextChoices):
    RUNNING = "RUNNING", "Running"
    PAUSED = "PAUSED", "Paused"
    STOPPED = "STOPPED", "Stopped"


class InspectionSettings(models.Model):
    component_name = models.CharField(max_length=150)
    expected_sequence = models.JSONField(default=list)
    layer_distance = models.PositiveIntegerField(default=0)
    color_tolerance = models.PositiveSmallIntegerField(default=20)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)


class InspectionProcess(models.Model):
    state = models.CharField(
        max_length=20,
        choices=ProcessState.choices,
        default=ProcessState.STOPPED,
    )
    started_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)


class InspectionRecord(models.Model):
    component_serial_number = models.CharField(max_length=100)
    component_name = models.CharField(max_length=150)
    operator_id = models.CharField(max_length=100)
    operator_name = models.CharField(max_length=150)
    expected_sequence = models.JSONField(default=list)
    detected_sequence = models.JSONField(default=list)
    expected_wire_count = models.PositiveIntegerField()
    detected_wire_count = models.PositiveIntegerField(default=0)
    result = models.CharField(max_length=30, choices=InspectionResult.choices)
    error_details = models.TextField(blank=True)
    image = models.ImageField(upload_to="inspection/originals/", blank=True)
    processed_image = models.ImageField(
        upload_to="inspection/processed/", blank=True
    )
    tested_at = models.DateTimeField(auto_now_add=True)
