# -*- coding:utf-8 -*-
import json
import os.path

from django.conf import settings
from django.core.management.base import BaseCommand

def location_from_info(info):
    from locations.models import Location
    return Location(**{
        'name': info['name'],

        'postcode': info.get('postcode'),
        'address': info.get('address', ''),
        'telephone': info.get('telephone', ''),
        'email': info.get('email', ''),

        'x_coord': info.get('x_coord'),
        'y_coord': info.get('y_coord'),

        'vrnorg': int(info['vrnorg']) if 'vrnorg' in info else None,
        'vrnkomis': int(info['vrnkomis']) if 'vrnkomis' in info else None,
        'tvd': int(info.get('tvd', 0)),
        'root': int(info.get('root', 0)),
    })

class Command(BaseCommand):
    help = "Loads locations data after first syncdb."

    def handle(self, *args, **options):
        country = location_from_info({'name': u'Россия'})
        country.region_code = 0
        country.save()

        hierarchy_data = json.loads(open(os.path.join(settings.PROJECT_PATH, 'data', 'hierarchy.json')).read().decode('utf8'))

        for region_info in hierarchy_data['sub']:
            print region_info['name']

            region = location_from_info(region_info)
            region.country = country
            region.region_code = region_info['id']
            region.save()

            for tik_info in region_info['sub']:
                tik = location_from_info(tik_info)
                tik.country = country
                tik.region_code = region_info['id']
                tik.region = region

                tik.save()
