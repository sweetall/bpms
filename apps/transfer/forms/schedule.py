import json
from django import forms
from django.utils.translation import gettext_lazy as _
from django_celery_beat.models import PeriodicTask

from transfer.models import Database, Table, TransferSchedule, Command
from ..utils import create_or_update_schedule_task, create_task_name, create_transfer_cmd
from common.utils import get_object_or_none
from assets.models.label import Label

__all__ = ['ImportScheduleCreateForm', 'ImportScheduleUpdateForm', 'ExportScheduleCreateForm',
           'ExportScheduleUpdateForm']

# ImportScheduleCreateForm = None
# ImportScheduleUpdateForm = None
# ExportScheduleCreateForm = None
# ExportScheduleUpdateForm = None


class ImportScheduleCreateForm(forms.Form):
    database = forms.ModelChoiceField(queryset=Database.objects.filter(is_active=True, label__value='生产环境'),
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

    def save(self, request):
        database_id = str(self.cleaned_data.get('database').id)
        tables_id_list = self.cleaned_data.get('tables')
        task_name = create_task_name(database_id)
        task_info = {
            'name': task_name,
            'task': 'transfer.tasks.execute_transfer_task',  # A registered celery task,
            'crontab': self.cleaned_data.get('crontab')[:-4] + '*',
            'args': (),
            'kwargs': {
                'database': database_id,
                'tables': tables_id_list,
                'year': self.cleaned_data.get('crontab')[-4:],
                'cmd': create_transfer_cmd(database_id, tables_id_list),
                'task_name': task_name,
            },
            'enabled': True,
            'schedule': {
                'type': 0,
                'comment': self.cleaned_data.get('comment'),
                'user': request.user,
            }
        }
        create_or_update_schedule_task(task=task_info)


class ImportScheduleUpdateForm(forms.Form):
    name = forms.CharField(widget=forms.HiddenInput)
    database = forms.ModelChoiceField(queryset=Database.objects.filter(is_active=True, label__value='生产环境'),
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

    def save(self, request):
        database_id = str(self.cleaned_data.get('database').id)
        tables_id_list = self.cleaned_data.get('tables')
        task_name = self.cleaned_data.get('name')
        task_info = {
            'name': task_name,
            'task': 'transfer.tasks.execute_transfer_task',  # A registered celery task,
            'crontab': self.cleaned_data.get('crontab')[:-4] + '*',
            'args': (),
            'kwargs': {
                'database': database_id,
                'tables': tables_id_list,
                'year': self.cleaned_data.get('crontab')[-4:],
                'cmd': create_transfer_cmd(database_id, tables_id_list),
                'task_name': task_name,
            },
            'enabled': True,
            'schedule': {
                'type': 0,
                'comment': self.cleaned_data.get('comment'),
                'user': request.user,
            }
        }
        create_or_update_schedule_task(task=task_info)


class ExportScheduleCreateForm(forms.Form):
    schedule = forms.ModelChoiceField(queryset=TransferSchedule.objects.filter(type=0, periodic__total_run_count__gte=1),
                                      required=True, label='选择任务 *')
    tables = forms.MultipleChoiceField(
        required=True,
        label='选择表 *', choices=list(set(Command.objects.filter(status=2)  # 2
                                    .values_list('table__id', 'table__name'))),
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

    def save(self, request):
        from_schedule = self.cleaned_data['schedule']
        database_name = Database.objects.get(id=json.loads(from_schedule.periodic.kwargs).get('database', '')).name
        database_id = str(Database.objects.filter(label__value='测试环境', name=database_name).first().id)
        tables_id_list = self.cleaned_data.get('tables')
        task_name = create_task_name(database_id)
        task_info = {
            'name': task_name,
            'task': 'transfer.tasks.execute_transfer_task',  # A registered celery task,
            'crontab': self.cleaned_data.get('crontab')[:-4] + '*',
            'args': (),
            'kwargs': {
                'database': database_id,
                'tables': tables_id_list,
                'year': self.cleaned_data.get('crontab')[-4:],
                'cmd': create_transfer_cmd(database_id, tables_id_list),
                'task_name': task_name,
                'from_schedule_id': str(from_schedule.id),
            },
            'enabled': True,
            'schedule': {
                'type': 1,
                'comment': self.cleaned_data.get('comment'),
                'user': request.user,
            }
        }
        create_or_update_schedule_task(task=task_info)


class ExportScheduleUpdateForm(forms.Form):
    name = forms.CharField(widget=forms.HiddenInput)
    schedule = forms.ModelChoiceField(queryset=TransferSchedule.objects.filter(type=0, periodic__total_run_count__gte=1),
                                      required=True, label='选择任务 *')
    tables = forms.MultipleChoiceField(
        required=True,
        label='选择表 *', choices=list(set(Command.objects.filter(status=2)  # 2
                                        .values_list('table__id', 'table__name'))),
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

    def save(self, request):
        from_schedule = self.cleaned_data['schedule']
        database_name = Database.objects.get(id=json.loads(from_schedule.periodic.kwargs).get('database', '')).name
        database_id = str(Database.objects.filter(label__value='测试环境', name=database_name).first().id)
        tables_id_list = self.cleaned_data.get('tables')
        task_name = self.cleaned_data.get('name')
        task_info = {
            'name': task_name,
            'task': 'transfer.tasks.execute_transfer_task',  # A registered celery task,
            'crontab': self.cleaned_data.get('crontab')[:-4] + '*',
            'args': (),
            'kwargs': {
                'database': database_id,
                'tables': tables_id_list,
                'year': self.cleaned_data.get('crontab')[-4:],
                'cmd': create_transfer_cmd(database_id, tables_id_list),
                'task_name': task_name,
                'from_schedule_id': str(from_schedule.id),
            },
            'enabled': True,
            'schedule': {
                'type': 1,
                'comment': self.cleaned_data.get('comment'),
                'user': request.user,
            }
        }
        create_or_update_schedule_task(task=task_info)
