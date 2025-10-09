from django.urls import path
from .views import ProjectListView, ProjectCreateView, ProjectUpdateView
urlpatterns = [
    path("", ProjectListView.as_view(), name="list"),
    path("create/", ProjectCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", ProjectUpdateView.as_view(), name="edit"),
]
