from django import forms
from django.utils.translation import gettext_lazy as _
import datetime

from ops.models import Schedule
from transfer.models import Database, Table
from ops.celery.utils import create_or_update_schedule_task
__all__ = ['ImportScheduleEditForm', ]


class ImportScheduleEditForm(forms.Form):
    database = forms.ChoiceField(
        choices=[('0', '--------')]+list(Database.objects.filter(is_active=True).values_list('id', 'name')),
        required=True, label='选择库 *')
    tables = forms.MultipleChoiceField(
        required=True,
        label='选择表 *', choices=Table.objects.filter(is_active=True).values_list('id', 'name'),
        widget=forms.SelectMultiple(
            attrs={
                'class': 'select2',
                'data-placeholder': _('Select tables')
            }
        )
    )
    name = forms.CharField(max_length=100, required=True, label='任务名称 *')
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
        task_info = {
            'name': self.cleaned_data.get('name'),
            'task': '',  # A registered celery task,
            'crontab': self.cleaned_data.get('crontab')[:-4] + '*',
            'args': (),
            'kwargs': {
                'database': self.cleaned_data.get('database'),
                'tables': self.cleaned_data.get('tables'),
                'year': self.cleaned_data.get('crontab')[-4:]
            },
            'enabled': False,
            'schedule': {
                'type': 1,
                'comment': self.cleaned_data.get('comment'),
                'user': request.user,
            }
        }
        # print(task_info)
        create_or_update_schedule_task(task=task_info)
