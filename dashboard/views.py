from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db.models import Count
from defects.models import Defect, Status
from datetime import date
class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "home.html"
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        aggr = Defect.objects.values("status").annotate(cnt=Count("id")).order_by()
        status_map = dict(Status.choices)
        ctx["status_data"] = [{"status": r["status"], "status_display": status_map.get(r["status"], r["status"]), "cnt": r["cnt"]} for r in aggr]
        ctx["overdue_count"] = Defect.objects.filter(due_date__lt=date.today()).exclude(status__in=[Status.CLOSED, Status.CANCELED]).count()
        return ctx
