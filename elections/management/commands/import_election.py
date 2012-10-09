# -*- coding:utf-8 -*-
from datetime import datetime
import json
import os
import os.path

from django.conf import settings
from django.core.management.base import BaseCommand

from grakon.utils import print_progress

def import_uiks_file(path):
    data = json.loads(open(path, 'r').read().decode('utf8'))

    from elections.models import Election, ElectionLocation
    from locations.models import Location
    election_date = datetime.strptime(data['date'], r'%d.%m.%Y')

    # Create country location for the date
    country, created = Location.objects.get_or_create(name=u'Россия', region_code=0, date=election_date)

    election, created = Election.objects.get_or_create(vrn=int(data['vrn']), prver=int(data['prver']),
            defaults={'title': data['election_name'], 'date': election_date, 'location': country})
    if not created:
        raise ValueError("Election has been imported already")

    try:
        region = Location.objects.get(region=None, region_code=data['region_id'], date=election_date)
    except Location.DoesNotExist:
        region = Location.objects.get(region=None, region_code=data['region_id'], date=None)

        region.id = None
        region.country = country
        region.date = election_date
        region.save()

    if data['vrn'][0] == '2':
        ElectionLocation(location=region, election=election).save()

    merge_ids = set(uik_data['merge_id'] for uik_data in data['merge'])
    tiks = Location.objects.filter(tik=None, merge_id__in=merge_ids, date=election_date).exclude(region=None)
    tiks_by_merge_id = dict((tik.merge_id, tik) for tik in tiks)

    for merge_id in merge_ids:
        if merge_id not in tiks_by_merge_id:
            tik = Location.objects.get(merge_id=merge_id, date=None)
            tik.id = None
            tik.date = election_date
            tik.country = country
            tik.region = region
            tik.save()
            tiks_by_merge_id[merge_id] = tik

        ElectionLocation(location=tiks_by_merge_id[merge_id], election=election).save()

    if data['vrn'][0] == '2': # region-level elections
        election.location = region
    else:
        if len(merge_ids) == 1:
            election.location = tiks_by_merge_id[list(merge_ids)[0]]
        else:
            election.location = region
    election.save()

    i = 0
    for uik_data in data['merge']:
        tik = tiks_by_merge_id[uik_data['merge_id']]
        uik, created = Location.objects.get_or_create(tik=tik, date=election_date, name=uik_data['name'][5:],
                defaults={'country': region.country, 'region': region, 'region_name': region.region_name,
                'region_code': region.region_code})

        ElectionLocation(location=uik, election=election, tvd=int(uik_data['tvd'])).save()

        i += 1
        print_progress(i, len(data['merge']))

class Command(BaseCommand):
    help = "Import uiks data from election directory"

    def handle(self, *args, **options):
        election_dir = os.path.join(settings.PROJECT_PATH, 'data', 'elections', args[0])
        for filename in os.listdir(election_dir):
            if 'merge' in filename:
                import_uiks_file(os.path.join(election_dir, filename))
