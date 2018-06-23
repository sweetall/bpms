from django import forms
from django.utils.translation import gettext_lazy as _

from ops.models import Schedule
from transfer.models import Database, Table
__all__ = ['ImportScheduleCreateForm', ]


class ImportScheduleCreateForm(forms.Form):
    task = forms.CharField(widget=forms.HiddenInput, initial='')
    type = forms.IntegerField(widget=forms.HiddenInput, initial=1)
    database = forms.ChoiceField(
        choices=[('0', '--------')]+list(Database.objects.filter(is_active=True).values_list('id', 'name')),
        required=True, label='选择库 *')
    tables = forms.MultipleChoiceField(
        required=True,
        label=_('Select tables *'), choices=(),
        widget=forms.SelectMultiple(
            attrs={
                'class': 'select2',
                'data-placeholder': _('Select fields')
            }
        )
    )
    name = forms.CharField(max_length=100, required=True, help_text='* required', label='任务名称')
    run_time = forms.DateTimeField(input_formats='%y-%m-%d %H:%M')
    comment = forms.Textarea()

