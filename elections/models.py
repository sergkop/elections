# -*- coding:utf-8 -*-
from django.db import models

from locations.models import Location

RESULTS_ROOT_URL = r'http://www.%(region_name)s.vybory.izbirkom.ru/region/%(region_name)s?action=show&global=1&vrn=100100031793505&region=%(region_code)d&prver=0&pronetvd=null'
RESULTS_URL = r'http://www.%(region_name)s.vybory.izbirkom.ru/region/region/%(region_name)s?action=show&tvd=%(tvd)d&vrn=100100031793505&region=%(region_code)d&global=true&sub_region=%(region_code)d&prver=0&pronetvd=null&vibid=%(tvd)d&type=226'

class Election(models.Model):
    title = models.CharField(u'Название', max_length=250)
    date = models.DateField(u'Дата', db_index=True)
    vrn = models.BigIntegerField(unique=True)
    prver = models.IntegerField()
    location = models.ForeignKey(Location)

    def __unicode__(self):
        return self.title

class ElectionLocation(models.Model):
    election = models.ForeignKey(Election)
    location = models.ForeignKey(Location)
    tvd = models.BigIntegerField(blank=True, null=True)

    class Meta:
        unique_together = ('election', 'location')

    # TODO: fix it
    def results_url(self):
        """ Link to the page with elections results on izbirkom.ru """
        data = {'region_name': self.location.region_name, 'region_code': self.location.region_code}
        if self.tvd != 0:
            data.update({'tvd': self.tvd})
            return RESULTS_URL % data
        else:
            return RESULTS_ROOT_URL % data
