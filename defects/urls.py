from django.urls import path
from .views import (
    DefectListView, DefectCreateView, DefectUpdateView, DefectDetailView,
    add_comment, upload_attachment, change_status, export_csv, export_excel
)
urlpatterns = [
    path("", DefectListView.as_view(), name="list"),
    path("create/", DefectCreateView.as_view(), name="create"),
    path("<int:pk>/", DefectDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", DefectUpdateView.as_view(), name="edit"),
    path("<int:pk>/comment/", add_comment, name="comment"),
    path("<int:pk>/attach/", upload_attachment, name="attach"),
    path("<int:pk>/status/", change_status, name="status"),
    path("export/csv/", export_csv, name="export_csv"),
    path("export/excel/", export_excel, name="export_excel"),
]
