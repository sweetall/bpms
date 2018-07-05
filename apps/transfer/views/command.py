from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.utils.translation import ugettext_lazy as _


class CommandListView(LoginRequiredMixin, TemplateView):
    template_name = 'transfer/command_list.html'

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Transfer'),
            'action': _('Transfer command'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)
