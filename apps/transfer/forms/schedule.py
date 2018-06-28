import random
import string
from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django_celery_beat.models import PeriodicTask

from transfer.models import Database, Table
from ops.celery.utils import create_or_update_schedule_task
__all__ = ['ImportScheduleCreateForm', 'ImportScheduleUpdateForm']


class ImportScheduleCreateForm(forms.Form):
    database = forms.ChoiceField(
        choices=[('0', '--------')]+list(Database.objects.filter(is_active=True).values_list('id', 'name')),
        required=True, label='选择库 *')
    tables = forms.MultipleChoiceField(
        required=True,
        label='选择表 *', choices=list(Table.objects.filter(is_active=True).values_list('id', 'name')),
        widget=forms.SelectMultiple(
            attrs={
                'class': 'select2',
                'data-placeholder': _('Select tables')
            }
        )
    )
    crontab = forms.CharField(max_length=100, label='执行时间 *')
    comment = forms.CharField(widget=forms.Textarea, required=False, label='备注')

    def clean_crontab(self):
        crontab_list = self.cleaned_data['crontab'].strip().replace('-', ' ').replace(':', ' ').split(' ')
        crontab_list.reverse()
        crontab = ' '.join(crontab_list)
        return crontab

    def clean_tables(self):
        return self.cleaned_data['tables']

    def save(self, request):
        database_id = self.cleaned_data.get('database')
        tables_id_list = self.cleaned_data.get('tables')
        task_name = create_task_name(database_id)
        task_info = {
            'name': task_name,
            'task': '',  # A registered celery task,
            'crontab': self.cleaned_data.get('crontab')[:-4] + '*',
            'args': (),
            'kwargs': {
                'database': database_id,
                'tables': tables_id_list,
                'year': self.cleaned_data.get('crontab')[-4:],
                'cmd': create_import_cmd(database_id, tables_id_list),
                'task_name': task_name,
            },
            'enabled': False,
            'schedule': {
                'type': 1,
                'comment': self.cleaned_data.get('comment'),
                'user': request.user,
            }
        }
        create_or_update_schedule_task(task=task_info)


class ImportScheduleUpdateForm(forms.Form):
    name = forms.CharField(widget=forms.HiddenInput)
    database = forms.ChoiceField(
        choices=[('0', '--------')]+list(Database.objects.filter(is_active=True).values_list('id', 'name')),
        required=True, label='选择库 *')
    tables = forms.MultipleChoiceField(
        required=True,
        label='选择表 *', choices=list(Table.objects.filter(is_active=True).values_list('id', 'name')),
        widget=forms.SelectMultiple(
            attrs={
                'class': 'select2',
                'data-placeholder': _('Select tables')
            }
        )
    )
    crontab = forms.CharField(max_length=100, label='执行时间 *')
    comment = forms.CharField(widget=forms.Textarea, required=False, label='备注')

    def clean_crontab(self):
        crontab_list = self.cleaned_data['crontab'].strip().replace('-', ' ').replace(':', ' ').split(' ')
        crontab_list.reverse()
        crontab = ' '.join(crontab_list)
        return crontab

    def clean_tables(self):
        return self.cleaned_data['tables']

    def save(self, request):
        database_id = self.cleaned_data.get('database')
        tables_id_list = self.cleaned_data.get('tables')
        task_name = self.cleaned_data.get('name')
        task_info = {
            'name': task_name,
            'task': '',  # A registered celery task,
            'crontab': self.cleaned_data.get('crontab')[:-4] + '*',
            'args': (),
            'kwargs': {
                'database': database_id,
                'tables': tables_id_list,
                'year': self.cleaned_data.get('crontab')[-4:],
                'cmd': create_import_cmd(database_id, tables_id_list),
                'task_name': task_name,
            },
            'enabled': False,
            'schedule': {
                'type': 1,
                'comment': self.cleaned_data.get('comment'),
                'user': request.user,
            }
        }
        create_or_update_schedule_task(task=task_info)


def create_task_name(database_id):
    try:
        database = Database.objects.get(id=database_id)
    except Database.DoesNotExist:
        return
    database_name = database.name
    task_name = database_name + timezone.localtime(timezone.now()).strftime('-%Y-%m-%d_%H-%M-%S')
    if not PeriodicTask.objects.filter(name=task_name):
        return task_name
    for i in range(10):
        random_str = '_' + ''.join(random.sample(string.ascii_letters + string.digits, 3))
        task_name += random_str
        if not PeriodicTask.objects.filter(name=task_name):
            return task_name


def create_import_cmd(database_id, tables_id_list):
    try:
        database = Database.objects.get(id=database_id)
    except Database.DoesNotExist:
        return []
    cmd = []
    database_name = database.name
    for table_id in tables_id_list:
        try:
            table = Table.objects.get(id=table_id)
        except Table.DoesNotExist:
            break
        table_name = table.name
        cmd.append(
            '/appdata/hadoopbak/shell/bachBackupHdfs.sh /user/hive/warehouse/{db}/{table}'.format(db=database_name,
                                                                                                  table=table_name)
        )
    return cmd
