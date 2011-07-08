from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from models import AgendaPlugin
from django.utils.translation import ugettext as _
import agenda

class CMSCalendarPlugin(CMSPluginBase):
    model =  AgendaPlugin
    name = _("Agenda Cal")
    render_template = "calendar/calendar.html"

    def render(self, context, instance, placeholder):
        context.update({
            'calendar':instance.calendar,
            'object':instance,
            'placeholder':placeholder
        })
        return context

plugin_pool.register_plugin(CMSCalendarPlugin)