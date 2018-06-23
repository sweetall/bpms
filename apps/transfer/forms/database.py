from django import forms
from django.utils.translation import gettext_lazy as _

from transfer.models import Database, Table, Field
from common.utils import get_logger

logger = get_logger(__file__)
__all__ = ['DatabaseCreateForm', 'DatabaseUpdateForm', 'DatabaseBulkUpdateForm']


class DatabaseCreateForm(forms.ModelForm):
    class Meta:
        model = Database
        fields = ['name', 'quota', 'dev', 'opr',  'is_active', 'comment']
        # widgets = {
        #     'nodes': forms.SelectMultiple(attrs={
        #         'class': 'select2', 'data-placeholder': _('Nodes')
        #     }),
        #     'admin_user': forms.Select(attrs={
        #         'class': 'select2', 'data-placeholder': _('Admin user')
        #     }),
        #     'labels': forms.SelectMultiple(attrs={
        #         'class': 'select2', 'data-placeholder': _('Label')
        #     }),
        #     'port': forms.TextInput(),
        #     'domain': forms.Select(attrs={
        #         'class': 'select2', 'data-placeholder': _('Domain')
        #     }),
        # }
        # labels = {
        #     'nodes': _("Node"),
        # }
        help_texts = {
            'name': '* required',
            'quota': '* required',
            'port': '* required',
        }


class DatabaseUpdateForm(forms.ModelForm):
    class Meta:
        model = Database
        fields = ['name', 'quota', 'dev', 'opr', 'is_active', 'comment']
        help_texts = {
            'name': '* required',
            'quota': '* required',
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

    class Meta:
        model = Database
        fields = [
            'databases', 'dev', 'opr', 'comment'
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
