from django import forms
from django.utils.translation import gettext_lazy as _

from transfer.models import Database, Table, Field
from common.utils import get_logger

logger = get_logger(__file__)
__all__ = ['FieldCreateForm', 'FieldUpdateForm', 'FieldBulkUpdateForm']


class FieldCreateForm(forms.ModelForm):
    table = forms.CharField(widget=forms.HiddenInput)

    def clean_table(self):
        try:
            table = Table.objects.get(id=self.data['table'])
        except Table.DoesNotExist as err:
            raise forms.ValidationError('您访问的表不存在')
        return table

    class Meta:
        model = Field
        fields = [
            'table',
            'name',
            'type',
            'is_sensitive',
            'comment'
        ]

        help_texts = {
            'name': '* required',
            'type': '* required',
        }


class FieldUpdateForm(forms.ModelForm):
    table = forms.CharField(widget=forms.HiddenInput)

    def clean_table(self):
        try:
            table = Table.objects.get(id=self.data['table'])
        except Table.DoesNotExist as err:
            raise forms.ValidationError('您访问的表不存在')
        return table

    class Meta:
        model = Field
        fields = [
            'table',
            'name',
            'type',
            'is_sensitive',
            'comment'
        ]

        help_texts = {
            'name': '* required',
            'type': '* required',
        }


class FieldBulkUpdateForm(forms.ModelForm):
    fields = forms.ModelMultipleChoiceField(
        required=True, help_text='* required',
        label=_('Select fields'), queryset=Field.objects.all(),
        widget=forms.SelectMultiple(
            attrs={
                'class': 'select2',
                'data-placeholder': _('Select fields')
            }
        )
    )

    class Meta:
        model = Field
        fields = [
            'fields',
            'comment'
        ]

    def save(self, commit=True):
        changed_fields = []
        for field in self._meta.fields:
            if self.data.get(field) not in [None, '']:
                changed_fields.append(field)

        cleaned_data = {k: v for k, v in self.cleaned_data.items()
                        if k in changed_fields}
        fields = cleaned_data.pop('fields')
        fields = Field.objects.filter(id__in=[asset.id for asset in fields])
        fields.update(**cleaned_data)
        return fields
