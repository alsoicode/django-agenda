from datetime import datetime

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sitemaps import ping_google
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from cms.models import CMSPlugin


class Location(models.Model):
    class Meta:
        verbose_name = _('Location')
        verbose_name_plural = _('Locations')
        ordering = ('title',)

    def __unicode__(self):
        return self.title

    title = models.CharField(_('Title'), max_length=255)
    slug = models.SlugField(_('Slug'), db_index=True)
    address = models.CharField(_('Address'), max_length=255, blank=True)
    address2 = models.CharField(_('Address (cont)'), max_length=255, blank=True)
    city = models.CharField(_('City'), blank=True)
    state_province = models.CharField(_('State / Province'), max_length=255, blank=True)
    postal_code = models.CharField(_('Postal Code'), max_length=20, blank=True)

class PublicationManager(CurrentSiteManager):
    def get_query_set(self):
        return super(CurrentSiteManager, self).get_query_set().filter(publish=True, publish_date__lte=datetime.now())


class Event(models.Model):
    class Meta:
        verbose_name = _('Event')
        verbose_name_plural = _('Events')
        ordering = ['-event_date', '-start_time', '-title']
        get_latest_by = 'event_date'
        permissions = (('change_author', ugettext('Change author')),)
        unique_together = ('event_date', 'slug')

    def __unicode__(self):
        return _("%(title)s on %(event_date)s") % { 'title' : self.title, 'event_date' : self.event_date }

    @models.permalink
    def get_absolute_url(self):
        return ('agenda-detail', (), {
                  'year'  : self.event_date.year,
                  'month' : self.event_date.month,
                  'day'   : self.event_date.day,
                  'slug'  : self.slug })

    objects = models.Manager()
    on_site = CurrentSiteManager()
    published = PublicationManager()

    # Core fields
    title = models.CharField(_('Title'), max_length=255)
    slug = models.SlugField(_('Slug'), db_index=True)
    event_date = models.DateField(_('Date'))
    start_time = models.TimeField(_('Start Time'), blank=True, null=True)
    end_time = models.TimeField(_('End Time'), blank=True, null=True)
    location = models.ForeignKey(Location, blank=True, null=True)
    description = models.TextField(_('Description'))
    calendar = models.ForeignKey('Calendar', blank=True, null=True, related_name='events')

    # Extra fields
    add_date = models.DateTimeField(_('add date'), auto_now_add=True)
    mod_date = models.DateTimeField(_('modification date'), auto_now=True)
    author = models.ForeignKey(User, verbose_name=_('Author'), db_index=True, blank=True, null=True)
    publish_date = models.DateTimeField(_('Publication Date'), default=datetime.now())
    publish = models.BooleanField(_('Publish'), default=False)
    allow_comments = models.BooleanField(_('Allow comments'), default=False)
    sites = models.ManyToManyField(Site)
    website = models.URLField(verify_exists=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    def save(self):
        super(Event, self).save()
        if not settings.DEBUG:
            try:
                ping_google()
            except Exception:
                import logging
                logging.warn('Google ping on save did not work.')


class Calendar(models.Model):
    name = models.CharField(_('Name'), max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = _('Calendar')
        verbose_name_plural = _('Calendars')

    def __unicode__(self):
        if self.name:
            return self.name
        return _('Unnamed Calendar')


class AgendaPlugin(CMSPlugin):
    caption = models.CharField(null=True, blank=True, max_length=255)
    calendar = models.ForeignKey(Calendar)

