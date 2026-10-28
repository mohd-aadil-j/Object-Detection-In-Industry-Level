from django.urls import path

from . import views

urlpatterns = [
    path("health/", views.health_check, name="health-check"),
    path("settings/", views.InspectionSettingsView.as_view(), name="inspection-settings"),
    path("process/<str:action>/", views.ProcessControlView.as_view(), name="process-control"),
    path("inspection/process/", views.ProcessInspectionView.as_view(), name="process-inspection"),
    path("inspection/history/", views.InspectionHistoryView.as_view(), name="inspection-history"),
]
