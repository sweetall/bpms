from django.views.generic import TemplateView
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView, DeleteView, FormView, UpdateView
from django.shortcuts import reverse, get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
import json
import uuid

from common.utils import get_object_or_none
from ..models import TransferSchedule
from transfer.forms.schedule import ImportScheduleCreateForm, ImportScheduleUpdateForm, ExportScheduleCreateForm, \
    ExportScheduleUpdateForm
from common.const import create_success_msg, update_success_msg
from ..utils import ScheduleEditableAccessMixin


class ImportScheduleListView(LoginRequiredMixin, TemplateView):
    template_name = 'transfer/schedule_import_list.html'

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Transfer'),
            'action': _('Transfer in'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class ImportScheduleCreateView(SuccessMessageMixin, FormView):
    initial = {}
    form_class = ImportScheduleCreateForm
    template_name = 'transfer/schedule_import_create.html'
    success_url = reverse_lazy('transfer:schedule-import-list')

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        form.save(request=self.request)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Transfer'),
            'action': _('Transfer in create'),
            'form': self.get_form_class()
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get_success_message(self, cleaned_data):
        return create_success_msg % ({"name": '导入任务'})

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            messages.error(request, form.errors)
            return self.form_invalid(form)


class ImportScheduleUpdateView(ScheduleEditableAccessMixin, SuccessMessageMixin, FormView):
    initial = {}
    form_class = ImportScheduleUpdateForm
    template_name = 'transfer/schedule_import_update.html'
    success_url = reverse_lazy('transfer:schedule-import-list')

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        form.save(request=self.request)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        pk = self.request.META.get("PATH_INFO").split('/')[-3]
        schedule = get_object_or_404(TransferSchedule, id=pk)
        database_id = schedule.database.id
        tables = [str(item[0]) for item in schedule.commands.values_list('table__id')]
        run_time = schedule.run_time
        form_default = {}

        comment = schedule.comment
        form_default["schedule"] = pk
        form_default["database"] = database_id
        form_default["tables"] = tables
        form_default['run_time'] = run_time
        form_default['comment'] = comment
        form = self.get_form_class()(initial=form_default)

        context = {
            'app': _('Transfer'),
            'action': _('Transfer in update'),
            'form': form,
            'database_id': database_id,
            'tables': ' '.join(tables),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get_success_message(self, cleaned_data):
        return update_success_msg % ({"name": cleaned_data["schedule"]})


class ExportScheduleListView(LoginRequiredMixin, TemplateView):
    template_name = 'transfer/schedule_export_list.html'

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Transfer'),
            'action': _('Transfer out'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class ExportScheduleCreateView(SuccessMessageMixin, FormView):
    initial = {}
    form_class = ExportScheduleCreateForm
    template_name = 'transfer/schedule_export_create.html'
    success_url = reverse_lazy('transfer:schedule-export-list')

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        form.save(request=self.request)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Transfer'),
            'action': _('Transfer out create'),
            'form': self.get_form_class()
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get_success_message(self, cleaned_data):
        return create_success_msg % ({"name": '导出任务'})

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            messages.error(request, form.errors)
            return self.form_invalid(form)


class ExportScheduleUpdateView(ScheduleEditableAccessMixin, SuccessMessageMixin, FormView):
    initial = {}
    form_class = ExportScheduleUpdateForm
    template_name = 'transfer/schedule_export_update.html'
    success_url = reverse_lazy('transfer:schedule-export-list')

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        form.save(request=self.request)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        pk = self.request.META.get("PATH_INFO").split('/')[-3]
        schedule = get_object_or_404(TransferSchedule, id=pk)
        from_schedule_id = schedule.from_schedule
        form_default = {}
        tables = [str(item[0]) for item in schedule.commands.values_list('table__id')]
        run_time = schedule.run_time
        comment = schedule.comment
        form_default["schedule"] = pk
        form_default["from_schedule"] = from_schedule_id
        form_default["tables"] = tables
        form_default['run_time'] = run_time
        form_default['comment'] = comment
        form = self.get_form_class()(initial=form_default)

        context = {
            'app': _('Transfer'),
            'action': _('Transfer out update'),
            'form': form,
            'schedule_id': from_schedule_id,
            'tables': ' '.join(tables),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get_success_message(self, cleaned_data):
        return update_success_msg % ({"name": cleaned_data["schedule"]})
