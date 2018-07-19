from django import forms
from django.utils.translation import gettext_lazy as _

from transfer.models import Database, Table, Field
from common.utils import get_logger
from assets.models.asset import Asset

logger = get_logger(__file__)
__all__ = ['DatabaseCreateForm', 'DatabaseUpdateForm', 'DatabaseBulkUpdateForm']


class DatabaseCreateForm(forms.ModelForm):
    asset = forms.ModelChoiceField(queryset=Asset.objects.filter(labels__value__in=['生产环境', '测试环境']),
                                   required=True, label='机器', help_text='* required')

    class Meta:
        model = Database
        fields = ['name', 'asset', 'dev', 'opr', 'bus', 'user_owner', 'user_share', 'is_active', 'comment']
        help_texts = {
            'name': '* required',
            'port': '* required',
        }


class DatabaseUpdateForm(forms.ModelForm):
    asset = forms.ModelChoiceField(queryset=Asset.objects.filter(labels__value__in=['生产环境', '测试环境']),
                                   required=True, label='机器', help_text='* required')

    class Meta:
        model = Database
        fields = ['name', 'asset', 'dev', 'opr', 'bus', 'user_owner', 'user_share', 'is_active', 'comment']
        help_texts = {
            'name': '* required',
            'port': '* required',
        }


class DatabaseBulkUpdateForm(forms.ModelForm):
    databases = forms.ModelMultipleChoiceField(
        required=True, help_text='* required',
        label=_('Select databases'), queryset=Database.objects.all(),
        widget=forms.SelectMultiple(
            attrs={
                'class': 'select2',
                'data-placeholder': _('Select databases')
            }
        )
    )

    asset = forms.ModelChoiceField(queryset=Asset.objects.filter(labels__value__in=['生产环境', '测试环境']),
                                   required=True, label='机器')

    class Meta:
        model = Database
        fields = [
            'databases', 'asset', 'dev', 'opr', 'bus', 'user_owner', 'user_share', 'comment'
        ]

    def save(self, commit=True):
        changed_fields = []
        for field in self._meta.fields:
            if self.data.get(field) not in [None, '']:
                changed_fields.append(field)

        cleaned_data = {k: v for k, v in self.cleaned_data.items()
                        if k in changed_fields}
        databases = cleaned_data.pop('databases')
        databases = Database.objects.filter(id__in=[asset.id for asset in databases])
        databases.update(**cleaned_data)
        return databases


class FileForm(forms.Form):
    file = forms.FileField()
