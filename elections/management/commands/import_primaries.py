# -*- coding:utf-8 -*-
from datetime import datetime
import json
import os
import os.path

from django.conf import settings
from django.core.management.base import BaseCommand

from grakon.utils import print_progress

PRIMERIES_VRN = -5

class Command(BaseCommand):
    help = "Import opposition primaries"

    def handle(self, *args, **options):
        path = os.path.join(settings.PROJECT_PATH, 'data', 'elections', 'opposition-merge.json')
        data = json.loads(open(path, 'r').read().decode('utf8'))

        from elections.models import Election, ElectionLocation
        from locations.models import Location
        election_date = datetime.strptime(data['date'], r'%d.%m.%Y')

        # Create country location for the date
        country, created = Location.objects.get_or_create(name=u'Россия', region_code=0, date=election_date, defaults={'vrnorg': PRIMERIES_VRN})

        election, created = Election.objects.get_or_create(vrn=PRIMERIES_VRN, prver=0,
                defaults={'title': data['election_name'], 'date': election_date, 'location': country})
        if not created:
            raise ValueError("Election has been imported already")

        ElectionLocation(location=country, election=election).save()

        country_no_date = Location.objects.country()
        regions_by_code = {}
        for region in Location.objects.filter(country=country_no_date, region=None):
            region.id = None
            region.country = country
            region.date = election_date
            region.vrnorg = PRIMERIES_VRN
            region.save()

            regions_by_code[region.region_code] = region

            ElectionLocation(location=region, election=election).save()

            rvk, created = Location.objects.get_or_create(region=region, date=election_date, name=u'Голосование онлайн',
                    defaults={'country': country, 'region_name': region.region_name, 'region_code': region.region_code, 'vrnorg': PRIMERIES_VRN})

            ElectionLocation(location=rvk, election=election, tvd=0).save()

        for rvk_data in data['merge']:
            region = regions_by_code[rvk_data['merge_id']]
            rvk, created = Location.objects.get_or_create(region=region, date=election_date, name=rvk_data['name'],
                    defaults={'country': country, 'region_name': region.region_name, 'region_code': region.region_code,
                    'address': rvk_data['address'], 'email': rvk_data['email'], 'telephone': rvk_data['telephone'], 'vrnorg': PRIMERIES_VRN})

            ElectionLocation(location=rvk, election=election, tvd=0).save()
