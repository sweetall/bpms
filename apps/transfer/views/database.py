import datetime
import codecs
import csv
import json
import uuid
import chardet
from io import StringIO

from django.views.generic import TemplateView, ListView
from django.views import View
from django.utils.translation import ugettext_lazy as _
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, DeleteView, FormView, UpdateView
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect, reverse
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy

from common.utils import get_object_or_none, get_logger, is_uuid
from common.const import create_success_msg, update_success_msg
from common.mixins import AdminUserRequiredMixin, JSONResponseMixin
from transfer.models import Database, Table, Field
from transfer.forms.database import DatabaseCreateForm, DatabaseUpdateForm, DatabaseBulkUpdateForm, FileForm
from transfer.serializers import DatabaseSerializer
from assets.models import Asset


class DatabaseListView(LoginRequiredMixin, TemplateView):
    template_name = 'transfer/database_list.html'

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Transfer'),
            'action': _('Transfer database'),
            'labels': '',
            'nodes': '',
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class DatabaseCreateView(AdminUserRequiredMixin, SuccessMessageMixin, CreateView):
    model = Database
    form_class = DatabaseCreateForm
    template_name = 'transfer/database_create.html'
    success_url = reverse_lazy('transfer:database-list')

    # def get_form(self, form_class=None):
    #     form = super().get_form(form_class=form_class)
    #     node_id = self.request.GET.get("node_id")
    #     if node_id:
    #         node = get_object_or_none(Node, id=node_id)
    #     else:
    #         node = Node.root()
    #     form["nodes"].initial = node
    #     return form
    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        database = form.save()
        database.modifier = self.request.user.username or 'Admin'
        database.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Transfer'),
            'action': _('Create database'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get_success_message(self, cleaned_data):
        return create_success_msg % ({"name": cleaned_data["name"]})


class DatabaseUpdateView(AdminUserRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Database
    form_class = DatabaseUpdateForm
    template_name = 'transfer/database_update.html'
    success_url = reverse_lazy('transfer:database-list')

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        database = form.save()
        database.modifier = self.request.user.username or 'Admin'
        database.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Transfer'),
            'action': _('Update database'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

    def get_success_message(self, cleaned_data):
        return update_success_msg % ({"name": cleaned_data["name"]})


class DatabaseBulkUpdateView(LoginRequiredMixin, ListView):
    model = Database
    form_class = DatabaseBulkUpdateForm
    template_name = 'transfer/database_bulk_update.html'
    success_url = reverse_lazy('transfer:database-list')
    id_list = None
    form = None
    success_message = _("Bulk update database success")

    def get(self, request, *args, **kwargs):
        database_id = self.request.GET.get('database_id', '')
        self.id_list = [i for i in database_id.split(',')]

        if kwargs.get('form'):
            self.form = kwargs['form']
        elif database_id:
            self.form = self.form_class(
                initial={'databases': self.id_list}
            )
        else:
            self.form = self.form_class()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            databases = form.save()
            databases.update(modifier=request.user.username, modify_time=datetime.datetime.now())
            messages.success(request, self.success_message)
            return redirect(self.success_url)
        else:
            return self.get(request, form=form, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Transfer'),
            'action': _('Bulk update database'),
            'form': self.form,
            'database_selected': self.id_list,
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


@method_decorator(csrf_exempt, name='dispatch')
class DatabaseExportView(View):

    def get(self, request):
        database_fields = [Database._meta.get_field(name) for name in ('name', 'asset', 'dev', 'opr', 'bus',
                                                                       'user_owner', 'user_share', 'comment')]

        spm = request.GET.get('spm', '')
        databases_id = cache.get(spm, [])
        filename = 'databases-{}.csv'.format(
            timezone.localtime(timezone.now()).strftime('%Y-%m-%d_%H-%M-%S')
        )
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename
        response.write(codecs.BOM_UTF8)
        databases = DatabaseSerializer(instance=Database.objects.filter(id__in=databases_id), many=True).data
        writer = csv.writer(response, dialect='excel', quoting=csv.QUOTE_MINIMAL)

        header = [field.verbose_name for field in database_fields]
        writer.writerow(header)

        for database in databases:
            database_data = [database[field.name] for field in database_fields]
            writer.writerow(database_data)
        return response

    def post(self, request):
        try:
            databases_id = json.loads(request.body).get('databases_id', [])
        except ValueError:
            return HttpResponse('Json object not valid', status=400)
        spm = uuid.uuid4().hex
        cache.set(spm, databases_id, 300)
        url = reverse('transfer:database-export') + '?spm=%s' % spm
        return JsonResponse({'redirect': url})


class DatabaseBulkImportView(AdminUserRequiredMixin, JSONResponseMixin, FormView):
    form_class = FileForm

    def form_invalid(self, form):
        try:
            error = form.errors.values()[-1][-1]
        except Exception as e:
            error = _('Invalid file.')
        data = {
            'success': False,
            'msg': error
        }
        return self.render_json_response(data)

    # todo: need be patch, method to long
    def form_valid(self, form):
        f = form.cleaned_data['file']
        det_result = chardet.detect(f.read())
        f.seek(0)  # reset file seek index
        data = f.read().decode(det_result['encoding']).strip(codecs.BOM_UTF8.decode())
        csv_file = StringIO(data)
        reader = csv.reader(csv_file)
        csv_data = [row for row in reader]
        # header_ = csv_data[0]
        database_fields = ['name', 'asset', 'dev', 'opr', 'bus', 'user_owner', 'user_share', 'comment']

        created = []
        # updated = {'database': [], 'table': [], 'field': []}
        # failed = {'database': [], 'table': [], 'field': []}
        for row in csv_data[1:]:
            if set(row) == {''}:
                continue
            elif len(row) < len(database_fields):
                row.extend(['']*(len(database_fields)-len(row)))
            database_dict = dict(zip(database_fields, row[:len(database_fields)]))
            database_dict.update({'modifier': self.request.user.username or 'Admin',
                                  'asset': get_object_or_none(Asset, ip=database_dict['asset'])})

            if not database_dict['name']:
                continue
            database, _created = Database.objects.update_or_create(name=database_dict['name'],
                                                                   asset=database_dict['asset'], defaults=database_dict)
            if _created:
                created.append(database_dict['name'])

        data = {
            'created': '\n'.join([(item + ': ' + ','.join(created[item])) for item in created]),
            'created_info': 'Created database:{}'.format(len(created)),
            # 'updated': updated,
            # 'updated_info': 'Updated {}'.format(len(updated)),
            # 'failed': failed,
            # 'failed_info': 'Failed {}'.format(len(failed)),
            'valid': True,
            'msg': 'Created database:{}'.format(len(created)),
        }
        return self.render_json_response(data)
