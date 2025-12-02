from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView
import csv
from datetime import date

try:
    import openpyxl
except Exception:
    openpyxl = None
from .models import Defect, Status, Priority, Attachment, Comment
from .forms import DefectForm, CommentForm, AttachmentForm


class DefectListView(LoginRequiredMixin, ListView):
    model = Defect
    template_name = "defects/defect_list.html"
    context_object_name = "items"
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset().select_related("project", "stage", "assignee", "reporter")
        q = self.request.GET.get("q")
        status = self.request.GET.get("status")
        priority = self.request.GET.get("priority")
        project = self.request.GET.get("project")
        assignee = self.request.GET.get("assignee")
        overdue = self.request.GET.get("overdue")

        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
        if status:
            qs = qs.filter(status=status)
        if priority:
            qs = qs.filter(priority=priority)
        if project:
            qs = qs.filter(project_id=project)
        if assignee:
            qs = qs.filter(assignee_id=assignee)
        if overdue:
            qs = qs.filter(due_date__lt=date.today()).exclude(
                status__in=[Status.CLOSED, Status.CANCELED]
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["statuses"] = Status.choices
        ctx["priorities"] = Priority.choices
        return ctx


class DefectCreateView(LoginRequiredMixin, CreateView):
    model = Defect;
    form_class = DefectForm;
    template_name = "defects/defect_form.html"

    def form_valid(self, form):
        form.instance.reporter = self.request.user;
        form.instance._changed_by = self.request.user
        messages.success(self.request, "Дефект создан.");
        return super().form_valid(form)

    def get_success_url(self): return reverse("defects:detail", args=[self.object.pk])


class DefectUpdateView(LoginRequiredMixin, UpdateView):
    model = Defect;
    form_class = DefectForm;
    template_name = "defects/defect_form.html"

    def form_valid(self, form):
        form.instance._changed_by = self.request.user;
        messages.success(self.request, "Дефект обновлён.")
        return super().form_valid(form)

    def get_success_url(self): return reverse("defects:detail", args=[self.object.pk])


class DefectDetailView(LoginRequiredMixin, DetailView):
    model = Defect
    template_name = "defects/defect_detail.html"
    context_object_name = "obj"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["comment_form"] = CommentForm()
        ctx["attach_form"] = AttachmentForm()
        # все возможные статусы по модели
        ctx["status_choices"] = Defect._meta.get_field("status").choices
        # какие переходы разрешены для конкретного дефекта
        ctx["allowed_transitions"] = [
            code for code, name in Status.choices if self.object.can_transition(code)
        ]
        return ctx


@login_required
def add_comment(request, pk):
    defect = get_object_or_404(Defect, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            Comment.objects.create(defect=defect, author=request.user, text=form.cleaned_data["text"])
            messages.success(request, "Комментарий добавлен.")
    return redirect("defects:detail", pk=pk)


@login_required
def upload_attachment(request, pk):
    defect = get_object_or_404(Defect, pk=pk)
    if request.method == "POST":
        form = AttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            Attachment.objects.create(defect=defect, uploaded_by=request.user, file=form.cleaned_data["file"])
            messages.success(request, "Файл прикреплён.")
    return redirect("defects:detail", pk=pk)


@login_required
def change_status(request, pk):
    defect = get_object_or_404(Defect, pk=pk)
    if request.method != "POST": return HttpResponseForbidden("POST only")
    new_status = request.POST.get("status")
    if not new_status or not defect.can_transition(new_status):
        messages.error(request, "Недопустимый переход статуса.");
        return redirect("defects:detail", pk=pk)
    defect.status = new_status;
    defect._changed_by = request.user;
    defect.save()
    messages.success(request, "Статус изменён.");
    return redirect("defects:detail", pk=pk)


@login_required
def export_csv(request):
    qs = Defect.objects.all()
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="defects.csv"'
    writer = csv.writer(response)
    writer.writerow(["ID", "Проект", "Этап", "Заголовок", "Приоритет", "Статус", "Исполнитель", "Срок"])
    for d in qs:
        writer.writerow([d.id, d.project.name, d.stage.name if d.stage else "", d.title, d.get_priority_display(),
                         d.get_status_display(), getattr(d.assignee, "username", ""), d.due_date or ""])
    return response


@login_required
def export_excel(request):
    if openpyxl is None:
        messages.error(request, "openpyxl не установлен. Используйте экспорт CSV.");
        return redirect("defects:list")
    qs = Defect.objects.all()
    wb = openpyxl.Workbook();
    ws = wb.active;
    ws.title = "Defects"
    ws.append(["ID", "Проект", "Этап", "Заголовок", "Приоритет", "Статус", "Исполнитель", "Срок"])
    for d in qs:
        ws.append([d.id, d.project.name, d.stage.name if d.stage else "", d.title, d.get_priority_display(),
                   d.get_status_display(), getattr(d.assignee, "username", ""), str(d.due_date or "")])
    from io import BytesIO
    buff = BytesIO();
    wb.save(buff);
    buff.seek(0)
    resp = HttpResponse(buff.getvalue(),
                        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    resp["Content-Disposition"] = 'attachment; filename="defects.xlsx"'
    return resp
