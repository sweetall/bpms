import datetime
from django.views.generic import TemplateView, ListView
from django.utils.translation import ugettext_lazy as _
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView, DeleteView, FormView, UpdateView
from django.urls import reverse_lazy
from django.shortcuts import redirect, reverse
from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth.mixins import LoginRequiredMixin

from common.utils import get_object_or_none, get_logger, is_uuid
from common.const import create_success_msg, update_success_msg
from common.mixins import AdminUserRequiredMixin
from transfer.models import Database, Table, Field
from transfer.forms.table import TableCreateForm, TableUpdateForm, TableBulkUpdateForm


class TableListView(LoginRequiredMixin, TemplateView):
    template_name = 'transfer/table_list.html'

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Transfer'),
            'action': _('Transfer table'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get(self, request, pk, *args, **kwargs):
        # messages.success(request, repr(request.META))
        context = self.get_context_data(**kwargs)
        context.update({'database_id': pk})
        database = get_object_or_none(Database, id=pk)
        context['action'] = (database.name + '-表清单') if database else '表清单'
        return self.render_to_response(context)


class TableCreateView(AdminUserRequiredMixin, SuccessMessageMixin, CreateView):
    model = Table
    form_class = TableCreateForm
    template_name = 'transfer/table_create.html'
    success_url = '/bpms/'

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        database_id = self.request.META.get("PATH_INFO").split('/')[-4]
        form["database"].initial = database_id
        return form

    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        self.success_url = reverse('transfer:table-list',
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
        table = form.save()
        table.modifier = self.request.user.username or 'Admin'
        table.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        database = get_object_or_none(Database, id=self.request.META.get("PATH_INFO").split('/')[-4])
        context = {
            'app': _('Transfer'),
            'action': database.__str__() + '-创建表' if database else '创建表',
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get_success_message(self, cleaned_data):
        return create_success_msg % ({"name": cleaned_data["name"]})


class TableUpdateView(AdminUserRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Table
    form_class = TableUpdateForm
    template_name = 'transfer/table_update.html'
    success_url = '/bpms/'

    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        self.success_url = reverse('transfer:table-list',
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
        table = form.save()
        table.modifier = self.request.user.username or 'Admin'
        table.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        database = get_object_or_none(Database, id=self.request.META.get("PATH_INFO").split('/')[-5])
        context = {
            'app': _('Transfer'),
            'action': database.__str__() + '-更新表' if database else '更新表',
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get_success_message(self, cleaned_data):
        return update_success_msg % ({"name": cleaned_data["name"]})


class TableBulkUpdateView(AdminUserRequiredMixin, ListView):
    model = Table
    form_class = TableBulkUpdateForm
    template_name = 'transfer/table_bulk_update.html'
    success_url = '/bpms/'
    id_list = None
    form = None
    success_message = _("Bulk update table success")

    def get(self, request, *args, **kwargs):
        table_id = self.request.GET.get('table_id', '')
        self.id_list = [i for i in table_id.split(',')]

        if kwargs.get('form'):
            self.form = kwargs['form']
        elif table_id:
            self.form = self.form_class(
                initial={'tables': self.id_list}
            )
        else:
            self.form = self.form_class()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        self.success_url = reverse('transfer:table-list',
                                   kwargs={'pk': self.request.META.get("PATH_INFO").split('/')[-4]})

        form = self.form_class(request.POST)
        if form.is_valid():
            tables = form.save()
            tables.update(modifier=request.user.username, modify_time=datetime.datetime.now())
            messages.success(request, self.success_message)
            return redirect(self.success_url)
        else:
            return self.get(request, form=form, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Transfer'),
            'action': _('Bulk update table'),
            'form': self.form,
            'table_selected': self.id_list,
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


