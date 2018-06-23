from django.views.generic import TemplateView, ListView
from django.utils.translation import ugettext_lazy as _
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView, DeleteView, FormView, UpdateView
from django.urls import reverse_lazy
from django.shortcuts import redirect, reverse
from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
import datetime

from common.utils import get_object_or_none, get_logger, is_uuid
from common.const import create_success_msg, update_success_msg
from common.mixins import AdminUserRequiredMixin
from transfer.models import Database, Table, Field
from transfer.forms.field import FieldCreateForm, FieldUpdateForm, FieldBulkUpdateForm


class FieldListView(AdminUserRequiredMixin, TemplateView):
    template_name = 'transfer/field_list.html'

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Transfer'),
            'action': _('Transfer field'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get(self, request, pk, *args, **kwargs):
        # messages.success(request, repr(request.META))
        context = self.get_context_data(**kwargs)
        context.update({'table_id': pk})
        table = get_object_or_none(Table, id=pk)
        context['action'] = (table.__str__() + '-字段清单') if table else '字段清单'
        return self.render_to_response(context)


class FieldCreateView(AdminUserRequiredMixin, SuccessMessageMixin, CreateView):
    model = Field
    form_class = FieldCreateForm
    template_name = 'transfer/field_create.html'
    success_url = '/bpms/'

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        table_id = self.request.META.get("PATH_INFO").split('/')[-4]
        form["table"].initial = table_id
        return form

    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        self.success_url = reverse('transfer:field-list',
                                   kwargs={'pk': self.request.META.get("PATH_INFO").split('/')[-4]})
        if self.success_url:
            url = self.success_url.format(**self.object.__dict__)
        else:
            try:
                url = self.object.get_absolute_url()
            except AttributeError:
                raise ImproperlyConfigured(
                    "No URL to redirect to.  Either provide a url or define"
                    " a get_absolute_url method on the Model.")
        return url

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        field = form.save()
        field.modifier = self.request.user.username or 'Admin'
        field.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        table = get_object_or_none(Table, id=self.request.META.get("PATH_INFO").split('/')[-4])
        context = {
            'app': _('Transfer'),
            'action': table.__str__() + '-创建字段' if table else '创建字段',
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get_success_message(self, cleaned_data):
        return create_success_msg % ({"name": cleaned_data["name"]})


class FieldUpdateView(AdminUserRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Field
    form_class = FieldUpdateForm
    template_name = 'transfer/field_update.html'
    success_url = '/bpms/'

    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        self.success_url = reverse('transfer:field-list',
                                   kwargs={'pk': self.request.META.get("PATH_INFO").split('/')[-5]})
        if self.success_url:
            url = self.success_url.format(**self.object.__dict__)
        else:
            try:
                url = self.object.get_absolute_url()
            except AttributeError:
                raise ImproperlyConfigured(
                    "No URL to redirect to.  Either provide a url or define"
                    " a get_absolute_url method on the Model.")
        return url

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        field = form.save()
        field.modifier = self.request.user.username or 'Admin'
        field.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        table = get_object_or_none(Table, id=self.request.META.get("PATH_INFO").split('/')[-5])
        context = {
            'app': _('Transfer'),
            'action': table.__str__() + '-更新字段' if table else '更新字段',
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get_success_message(self, cleaned_data):
        return update_success_msg % ({"name": cleaned_data["name"]})


class FieldBulkUpdateView(AdminUserRequiredMixin, ListView):
    model = Field
    form_class = FieldBulkUpdateForm
    template_name = 'transfer/field_bulk_update.html'
    success_url = '/bpms/'
    id_list = None
    form = None
    success_message = _("Bulk update field success")

    def get(self, request, *args, **kwargs):
        field_id = self.request.GET.get('field_id', '')
        self.id_list = [i for i in field_id.split(',')]

        if kwargs.get('form'):
            self.form = kwargs['form']
        elif field_id:
            self.form = self.form_class(
                initial={'fields': self.id_list}
            )
        else:
            self.form = self.form_class()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        self.success_url = reverse('transfer:field-list',
                                   kwargs={'pk': self.request.META.get("PATH_INFO").split('/')[-4]})

        form = self.form_class(request.POST)
        if form.is_valid():
            fields = form.save()
            fields.update(modifier=request.user.username, modify_time=datetime.datetime.now())
            messages.success(request, self.success_message)
            return redirect(self.success_url)
        else:
            return self.get(request, form=form, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Transfer'),
            'action': _('Bulk update field'),
            'form': self.form,
            'field_selected': self.id_list,
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


