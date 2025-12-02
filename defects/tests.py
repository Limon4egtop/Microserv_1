from django.test import TestCase
from django.contrib.auth import get_user_model
from projects.models import Project
from .models import Defect, Status

User = get_user_model()


class WorkflowTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u1", password="pass")
        self.project = Project.objects.create(name="P1")

    def test_status_transitions(self):
        d = Defect.objects.create(project=self.project, title="T1", reporter=self.user)
        self.assertTrue(d.can_transition(Status.IN_PROGRESS))
        d.status = Status.IN_PROGRESS;
        d.save();
        d.refresh_from_db()
        self.assertFalse(d.can_transition(Status.CLOSED))  # сначала на проверку
