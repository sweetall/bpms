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
        database_fields = [Database._meta.get_field(name) for name in ('name', 'quota', 'dev', 'opr')]
        table_fields = [Table._meta.get_field(name) for name in ('name', 'format', 'table_create_time',
                        'table_update_time', 'is_partitioned', 'partition_field', 'dev', 'opr')]
        field_fields = [Field._meta.get_field(name) for name in ('name', 'type', 'is_sensitive')]

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

        header = [field.verbose_name for field in database_fields] + [field.verbose_name for field in table_fields] + \
                 [field.verbose_name for field in field_fields]
        writer.writerow(header)

        for database in databases:
            database_data = [database[field.name] for field in database_fields]
            if not database['tables']:
                data = database_data
                writer.writerow(data)
                continue
            for table in database['tables']:
                table_data = [table[field.name] for field in table_fields]
                if not table['fields']:
                    data = database_data + table_data
                    writer.writerow(data)
                    continue
                for field_ in table['fields']:
                    field_data = [field_[field.name] for field in field_fields]
                    data = database_data + table_data + field_data
                    writer.writerow(data)
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
        database_fields = ['name', 'quota', 'dev', 'opr']
        table_fields = ['name', 'format', 'table_create_time', 'table_update_time', 'is_partitioned',
                        'partition_field', 'dev', 'opr']
        field_fields = ['name', 'type', 'is_sensitive']

        created = {'database': [], 'table': [], 'field': []}
        # updated = {'database': [], 'table': [], 'field': []}
        # failed = {'database': [], 'table': [], 'field': []}
        for row in csv_data[1:]:
            if set(row) == {''}:
                continue
            elif len(row) < len(database_fields)+len(table_fields)+len(field_fields):
                row.extend(['']*(len(database_fields)+len(table_fields)+len(field_fields)-len(row)))
            database_dict = dict(zip(database_fields, row[:len(database_fields)]))
            table_dict = dict(zip(table_fields, row[len(database_fields):len(database_fields)+len(table_fields)]))
            field_dict = dict(zip(field_fields, row[-len(field_fields):]))
            database_dict.update({'modifier': self.request.user.username or 'Admin'})
            table_dict.update({'modifier': self.request.user.username or 'Admin',
                               'is_partitioned': True if table_dict['is_partitioned'].lower() == 'true' else False})
            field_dict.update({'modifier': self.request.user.username or 'Admin',
                               'is_sensitive': True if field_dict['is_sensitive'].lower() == 'true' else False})

            if not database_dict['name']:
                continue
            database, _created = Database.objects.update_or_create(name=database_dict['name'], defaults=database_dict)
            if _created:
                created['database'].append(database_dict['name'])

            if not table_dict['name']: continue
            table_dict.update({'database': database})
            table, _created = Table.objects.update_or_create(database=database, name=table_dict['name'],
                                                             defaults=table_dict)
            if _created:
                created['table'].append(table_dict['name'])

            if not field_dict['name']: continue
            field_dict.update({'table': table})
            field, _created = Field.objects.update_or_create(table=table, name=field_dict['name'], defaults=field_dict)
            if _created:
                created['field'].append(field_dict['name'])

        data = {
            'created': '\n'.join([(item + ': ' + ','.join(created[item])) for item in created]),
            'created_info': 'Created database:{} table:{} field:{}'.format(len(created['database']),
                                                                           len(created['table']),
                                                                           len(created['field'])),
            # 'updated': updated,
            # 'updated_info': 'Updated {}'.format(len(updated)),
            # 'failed': failed,
            # 'failed_info': 'Failed {}'.format(len(failed)),
            'valid': True,
            'msg': 'Created database:{} table:{} field:{}'.format(len(created['database']),
                                                                  len(created['table']),
                                                                  len(created['field'])),
        }
        return self.render_json_response(data)
