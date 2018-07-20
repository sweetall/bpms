import datetime
import codecs
import csv
import json
import uuid
import chardet
from io import StringIO
from django.views.generic import TemplateView, ListView
from django.utils.translation import ugettext_lazy as _
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView, DeleteView, FormView, UpdateView
from django.utils import timezone
from django.shortcuts import redirect, reverse
from django.core.cache import cache
from django.views import View
from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse, JsonResponse

from common.utils import get_object_or_none, get_logger, is_uuid
from common.const import create_success_msg, update_success_msg
from common.mixins import AdminUserRequiredMixin, JSONResponseMixin
from transfer.models import Database, Table, Field, Subsystem
from transfer.forms.table import TableCreateForm, TableUpdateForm, TableBulkUpdateForm, FileForm
from transfer.serializers import TableSerializer


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


class TableBulkUpdateView(LoginRequiredMixin, ListView):
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


@method_decorator(csrf_exempt, name='dispatch')
class TableExportView(View):

    def get(self, request):

        table_fields = [Table._meta.get_field(name) for name in ('name', 'format', 'is_partitioned', 'partition_field',
                                                                 'table_create_time', 'table_update_time', 'subsystem',
                                                                 'dev', 'opr', 'bus', 'comment')]

        spm = request.GET.get('spm', '')
        tables_id = cache.get(spm, [])
        filename = 'tables-{}.csv'.format(
            timezone.localtime(timezone.now()).strftime('%Y-%m-%d_%H-%M-%S')
        )
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename
        response.write(codecs.BOM_UTF8)
        tables = TableSerializer(instance=Table.objects.filter(id__in=tables_id), many=True).data
        writer = csv.writer(response, dialect='excel', quoting=csv.QUOTE_MINIMAL)

        header = [field.verbose_name for field in table_fields]
        writer.writerow(header)

        for table in tables:
            table_data = [table[field.name] for field in table_fields]
            writer.writerow(table_data)
        return response

    def post(self, request):
        try:
            tables_id = json.loads(request.body).get('tables_id', [])
        except ValueError:
            return HttpResponse('Json object not valid', status=400)
        spm = uuid.uuid4().hex
        cache.set(spm, tables_id, 300)
        url = reverse('transfer:table-export') + '?spm=%s' % spm
        return JsonResponse({'redirect': url})


class TableBulkImportView(AdminUserRequiredMixin, JSONResponseMixin, FormView):
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
        database_id = self.request.GET.get('database_id')
        if not get_object_or_none(Database, id=database_id):
            messages.error(self.request, '未制定Database！')
            return
        f = form.cleaned_data['file']
        det_result = chardet.detect(f.read())
        f.seek(0)  # reset file seek index
        data = f.read().decode(det_result['encoding']).strip(codecs.BOM_UTF8.decode())
        csv_file = StringIO(data)
        reader = csv.reader(csv_file)
        csv_data = [row for row in reader]
        # header_ = csv_data[0]
        table_fields = ['name', 'format', 'is_partitioned', 'partition_field', 'table_create_time', 'table_update_time',
                        'subsystem', 'dev', 'opr', 'bus', 'comment']

        created = []
        # updated = {'table': [], 'table': [], 'field': []}
        # failed = {'table': [], 'table': [], 'field': []}
        for row in csv_data[1:]:
            if set(row) == {''}:
                continue
            elif len(row) < len(table_fields):
                row.extend(['']*(len(table_fields)-len(row)))
            table_dict = dict(zip(table_fields, row[:len(table_fields)]))
            table_dict.update({
                'modifier': self.request.user.username or 'Admin',
                'subsystem': get_object_or_none(Subsystem, en_name_abbr=table_dict['subsystem']),
                'is_partitioned': True if table_dict['is_partitioned'].strip() == '是' else False
            })

            if not table_dict['name']:
                continue
            table, _created = Table.objects.update_or_create(database_id=database_id, name=table_dict['name'],
                                                             defaults=table_dict)
            if _created:
                created.append(table_dict['name'])

        data = {
            'created': '\n'.join([(item + ': ' + ','.join(created)) for item in created]),
            'created_info': 'Created table:{}'.format(len(created)),
            # 'updated': updated,
            # 'updated_info': 'Updated {}'.format(len(updated)),
            # 'failed': failed,
            # 'failed_info': 'Failed {}'.format(len(failed)),
            'valid': True,
            'msg': 'Created table:{}'.format(len(created)),
        }
        return self.render_json_response(data)
