from django.views.generic import TemplateView
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView, DeleteView, FormView, UpdateView
from django.shortcuts import reverse
from django.utils.translation import ugettext_lazy as _

from common.utils import get_object_or_none
from ops.models.celery import Schedule
from transfer.forms.schedule import ImportScheduleCreateForm
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


class ImportScheduleCreateView(SuccessMessageMixin, TemplateView):
    form_class = ImportScheduleCreateForm
    template_name = 'transfer/schedule_import_create.html'
    success_url = '/bpms/'  # reverse('transfer:import-schedule-list')

    # def get_form(self, form_class=None):
    #     form = super().get_form(form_class=form_class)
    #     # table_id = self.request.META.get("PATH_INFO").split('/')[-4]
    #     # form["table"].initial = table_id
    #     return form

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        field = form.save()
        # field.modifier = self.request.user.username or 'Admin'
        # field.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Transfer'),
            'action': '新建导入任务',
            'form': self.form_class()
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get_success_message(self, cleaned_data):
        return create_success_msg % ({"name": cleaned_data["name"]})


class ImportScheduleUpdateView(SuccessMessageMixin, CreateView):
    pass
