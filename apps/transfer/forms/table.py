from django import forms
from django.utils.translation import gettext_lazy as _

from transfer.models import Database, Table, Field
from common.utils import get_logger

logger = get_logger(__file__)
__all__ = ['TableCreateForm', 'TableUpdateForm', 'TableBulkUpdateForm']


class TableCreateForm(forms.ModelForm):
    database = forms.CharField(widget=forms.HiddenInput)

    def clean_table(self):
        try:
            database = Database.objects.get(id=self.data['table'])
        except Database.DoesNotExist as err:
            raise forms.ValidationError('您访问的表不存在')
        return database

    class Meta:
        model = Table
        fields = [
            'database',
            'name',
            'format',
            'table_create_time',
            'table_update_time',
            'is_partitioned',
            'partition_field',
            'dev',
            'opr',
            'bus',
            'is_active',
            'comment'
        ]

        help_texts = {
            'name': '* required',
            'format': '* required',
            'table_create_time': '* required',
            'table_update_time': '* required',
        }


class TableUpdateForm(forms.ModelForm):
    database = forms.CharField(widget=forms.HiddenInput)

    def clean_table(self):
        try:
            database = Database.objects.get(id=self.data['table'])
        except Database.DoesNotExist as err:
            raise forms.ValidationError('您访问的表不存在')
        return database

    class Meta:
        model = Table
        fields = [
            'database',
            'name',
            'format',
            'table_create_time',
            'table_update_time',
            'is_partitioned',
            'partition_field',
            'dev',
            'opr',
            'bus',
            'is_active',
            'comment'
        ]
        help_texts = {
            'name': '* required',
            'format': '* required',
            'table_create_time': '* required',
            'table_update_time': '* required',
        }


class TableBulkUpdateForm(forms.ModelForm):
    tables = forms.ModelMultipleChoiceField(
        required=True, help_text='* required',
        label=_('Select tables'), queryset=Table.objects.all(),
        widget=forms.SelectMultiple(
            attrs={
                'class': 'select2',
                'data-placeholder': _('Select tables')
            }
        )
    )

    class Meta:
        model = Table
        fields = [
            'tables',
            'dev',
            'opr',
            'bus',
            'comment'
        ]

    def save(self, commit=True):
        changed_fields = []
        for field in self._meta.fields:
            if self.data.get(field) not in [None, '']:
                changed_fields.append(field)

        cleaned_data = {k: v for k, v in self.cleaned_data.items()
                        if k in changed_fields}
        tables = cleaned_data.pop('tables')
        tables = Table.objects.filter(id__in=[asset.id for asset in tables])
        tables.update(**cleaned_data)
        return tables
