# -*- coding:utf-8 -*-
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q

from elements.models import ENTITIES_MODELS, FEATURES_MODELS
from services.cache import cache_function

INFO_URL = r'http://www.%(region_name)s.vybory.izbirkom.ru/region/%(region_name)s?action=show_komissia&region=%(region_code)d&sub_region=%(region_code)d&type=100&vrnorg=%(vrnorg)d&vrnkomis=%(vrnkomis)d'

class LocationManager(models.Manager):
    @cache_function('location/country', 1000)
    def country(self):
        return self.get(country=None, date=None)

    def info_for(self, ids, related=True):
        """
        Return {id: {'location': location, entities_keys: entities_data}}.
        If related is True, return list of entities data, otherwise - only ids.
        """
        cache_prefix = self.model.cache_prefix
        cached_locations = cache.get_many([cache_prefix+str(id) for id in ids])

        cached_ids = []
        res = {}
        for key, entity in cached_locations.iteritems():
            id = int(key[len(cache_prefix):])
            cached_ids.append(id)
            res[id] = entity

        other_ids = set(ids) - set(cached_ids)
        if len(other_ids) > 0:
            other_res = dict((id, {}) for id in other_ids)

            comments_data = FEATURES_MODELS['comments'].objects.get_for(Location, other_ids)

            ct_id = ContentType.objects.get_for_model(self.model).id
            locations = self.filter(id__in=other_ids).select_related()
            participants_ids = []
            for loc in locations:
                # TODO: instance is a dict in all entities
                other_res[loc.id] = {'instance': loc, 'ct': ct_id}

                # TODO: do we need tools data here?
                for name, model in ENTITIES_MODELS.iteritems():
                    if name == 'participants':
                        continue

                    other_res[loc.id][name] = loc.get_entities(name)(
                            limit=settings.LIST_COUNT['tools'])

                # Get participants
                participants_data = loc.get_entities('participants')(limit=settings.LIST_COUNT['participants'])
                participants_ids += participants_data['ids']
                other_res[loc.id]['participants'] = {
                    'count': participants_data['count'],
                    'entities': [{'id': id} for id in participants_data['ids']],
                }

                # Comments
                other_res[loc.id]['comments'] = comments_data[loc.id]

            profiles_by_id = ENTITIES_MODELS['participants'].objects.only('id', 'first_name', 'last_name', 'rating') \
                    .in_bulk(set(participants_ids))

            for loc in locations:
                for entity in other_res[loc.id]['participants']['entities']:
                    entity.update(profiles_by_id[entity['id']].display_info())

            res.update(other_res)

            cache_res = dict((cache_prefix+str(id), other_res[id]) for id in other_res)
            cache.set_many(cache_res, 60) # TODO: specify time outside of this method

        if related:
            for name, model in ENTITIES_MODELS.iteritems():
                if name == 'participants':
                        continue

                e_ids = set(e_id for id in ids for e_id in res[id][name]['ids'])
                e_info = model.objects.info_for(e_ids, related=False)

                for id in ids:
                    res[id][name]['entities'] = [e_info[e_id] for e_id in res[id][name]['ids']
                            if e_id in e_info]

        return res

# TODO: add foreign uiks (in other countries)
class Location(models.Model):
    """ The number of non-null values of parent specifies the level of location """
    # keys to the parents of the corresponding level (if present)
    country = models.ForeignKey('self', null=True, blank=True, related_name='country_related')
    region = models.ForeignKey('self', null=True, blank=True, related_name='in_region')
    tik = models.ForeignKey('self', null=True, blank=True, related_name='in_tik')

    date = models.DateField(u'Дата', null=True, blank=True, db_index=True)

    name = models.CharField(max_length=150, db_index=True)
    region_name = models.CharField(max_length=20)
    region_code = models.IntegerField()

    postcode = models.IntegerField(blank=True, null=True)
    address = models.CharField(max_length=200, blank=True)
    telephone = models.CharField(max_length=50, blank=True)
    email = models.CharField(max_length=40, blank=True)

    # Ids required to access comission data from izbirkom.ru (address, phone, etc.)
    vrnorg = models.BigIntegerField(blank=True, null=True)
    vrnkomis = models.BigIntegerField(blank=True, null=True)

    merge_id = models.IntegerField(blank=True, null=True) # used for tiks only

    # Coordinates used in Yandex maps
    x_coord = models.FloatField(blank=True, null=True, db_index=True)
    y_coord = models.FloatField(blank=True, null=True, db_index=True)

    #participants = generic.GenericRelation('participants.EntityParticipant', object_id_field='entity_id')

    objects = LocationManager()

    cache_prefix = 'location_info'

    # A hack to implement participants and comments
    features = ['participants', 'comments']
    roles = ['follower']

    def level(self):
        if self.region_id is None:
            return 2
        else:
            return 3

    def is_country(self):
        return self.country_id is None

    def is_region(self):
        return self.country_id is not None and self.region_id is None

    def is_tik(self):
        return self.region_id is not None

    def is_uik(self):
        return self.tik_id is not None

    def info_url(self):
        """ Link to the page with commission information on izbirkom.ru """
        if self.vrnorg is None:
            return ''

        return INFO_URL % {'region_name': self.region_name, 'region_code': self.region_code,
                'vrnorg': self.vrnorg, 'vrnkomis': self.vrnkomis}

    def path(self):
        # using int() is a hack for mysql to avoid using long int
        if not self.region_id:
            return [int(self.id)]
        elif not self.tik_id:
            return [int(self.region_id), int(self.id)]
        else:
            return [int(self.region_id), int(self.tik_id), int(self.id)]

    def __unicode__(self, full_path=False):
        name = self.name

        if self.is_uik():
            name = u'УИК №' + name

        if full_path:
            if self.region:
                name = str(self.region) + u'->' + name
        return name

    def children_query_field(self):
        """ Return name of of Location field to construct db query filtering children """
        i = self.level() - 1
        return ['country', 'region', 'tik'][i] if i<3 else None

    def info(self, related=True):
        return Location.objects.info_for([self.id], related)[self.id]

    def cache_key(self):
        return self.cache_prefix + str(self.id)

    def clear_cache(self):
        cache.delete(self.cache_key())

    # TODO: cache count separately?
    # TODO: cache it (at least for data for side panels) - in Location
    def get_entities(self, entity_type, qfilter=None):
        """ Return {'ids': sorted_entities_ids, 'count': total_count} """
        from elements.locations.models import EntityLocation
        model = ENTITIES_MODELS[entity_type]

        def method(start=0, limit=None, sort_by=('-rating',)):
            entity_query = Q()

            # Filter out unactivated accounts
            # TODO: make queryset a parameter of entity model (?)
            if model.entity_name == 'participants':
                entity_query = Q(user__is_active=True)

            if not self.is_country(): # used to speed up processing
                loc_query = Q(location__id=self.id)

                field = self.children_query_field()
                if field:
                    loc_query |= Q(**{'location__'+field: self.id})

                entity_ids = set(EntityLocation.objects.filter(
                        content_type=ContentType.objects.get_for_model(model)) \
                        .filter(loc_query).values_list('entity_id', flat=True))

                # TODO: what happens when the list of ids is too long (for the next query)? - use subqueries
                entity_query &= Q(id__in=entity_ids)

            if qfilter:
                entity_query &= qfilter

            ids = model.objects.filter(entity_query).order_by(*sort_by).values_list('id', flat=True)
            return {
                'count': ids.count(),
                'ids': ids[slice(start, start+limit if limit else None)],
            }

        return method

    # TODO: cache it
    def related(self):
        """ Return {date: location} with versions of this location at different dates """
        if self.is_country():
            locations = Location.objects.filter(country=None).select_related()
        elif self.is_region():
            locations = Location.objects.exclude(country=None).filter(region=None, region_code=self.region_code).select_related()
        elif self.is_tik():
            locations = Location.objects.filter(tik=None, region_code=self.region_code, name=self.name).select_related()
        else:
            locations = Location.objects.filter(region_code=self.region_code, tik__name=self.tik.name, name=self.name).select_related()

        return dict((location.date, location) for location in locations)

    @models.permalink
    def get_absolute_url(self):
        if self.is_country() and self.date is None:
            return ('main', (), {})
        else:
            return ('location_info', (), {'loc_id': str(self.id)})

    def tab_url(self):
        if self.is_country() and self.date is None:
            return {
                '': reverse('main'),
                'participants': reverse('participants'),
            }
        else:
            return {
                'participants': reverse('location_participants', args=[str(self.id)]),
            }
