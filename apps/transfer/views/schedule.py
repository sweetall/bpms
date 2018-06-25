from django.views.generic import TemplateView
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView, DeleteView, FormView, UpdateView
from django.shortcuts import reverse, get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
import json
import uuid

from common.utils import get_object_or_none
from ops.models.celery import Schedule
from transfer.forms.schedule import ImportScheduleEditForm
from common.const import create_success_msg, update_success_msg


class ImportScheduleListView(TemplateView):
    template_name = 'transfer/schedule_import_list.html'

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Ops'),
            'action': _('Ops Schedule'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class ImportScheduleCreateView(SuccessMessageMixin, FormView):
    initial = {}
    form_class = ImportScheduleEditForm
    template_name = 'transfer/schedule_import_create.html'
    success_url = reverse_lazy('transfer:schedule-import-list')

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        form.save(request=self.request)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Transfer'),
            'action': '新建导入任务',
            'form': self.get_form_class()
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get_success_message(self, cleaned_data):
        return create_success_msg % ({"name": cleaned_data["name"]})


class ImportScheduleUpdateView(SuccessMessageMixin, FormView):
    initial = {}
    form_class = ImportScheduleEditForm
    template_name = 'transfer/schedule_import_update.html'
    success_url = reverse_lazy('transfer:schedule-import-list')

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        form.save(request=self.request)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        pk = self.request.META.get("PATH_INFO").split('/')[-3]
        schedule = get_object_or_404(Schedule, id=pk)
        form_default = {}
        name = schedule.periodic.name
        database = json.loads(schedule.periodic.kwargs).get('database')
        tables = json.loads(schedule.periodic.kwargs).get('tables')
        year = json.loads(schedule.periodic.kwargs).get('year')
        crontab = schedule.periodic.crontab
        comment = schedule.comment
        form_default["name"] = name
        form_default["database"] = database
        form_default["tables"] = tables
        form_default['crontab'] = year + '-' + crontab.month_of_year + '-' + crontab.day_of_month + ' ' + \
                                  crontab.hour + ':' + crontab.minute
        form_default['comment'] = comment
        form = self.get_form_class()(initial=form_default)

        context = {
            'app': _('Transfer'),
            'action': '更新导入任务',
            'form': form,
            'database_id': database,
            'tables': ' '.join(tables),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get_success_message(self, cleaned_data):
        return update_success_msg % ({"name": cleaned_data["name"]})
