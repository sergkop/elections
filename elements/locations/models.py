from django.db import models
from django.contrib.contenttypes.models import ContentType

from elements.models import BaseEntityProperty, BaseEntityPropertyManager, feature_model
from locations.models import Location

class EntityLocationManager(BaseEntityPropertyManager):
    def get_for(self, model, ids):
        """ Return {id: {'ids': loc_ids}} """
        locations_data = list(self.filter(content_type=ContentType.objects.get_for_model(model),
                entity_id__in=ids).values_list('entity_id', 'location'))

        res = {}
        for id in ids:
            entity_locations = filter(lambda el: el[0]==id, locations_data)
            res[id] = {'ids': map(lambda el: el[1], entity_locations)}
        return res

    def update_location(self, entity, location):
        el = self.filter(content_type=ContentType.objects.get_for_model(type(entity)),
                entity_id=entity.id)[0]
        el.location = location
        el.save()

# TODO: some models may need only one location (?)
# TODO: reset cache on save()/delete() (here and in other models)
@feature_model
class EntityLocation(BaseEntityProperty):
    location = models.ForeignKey(Location, related_name='entities')

    objects = EntityLocationManager()

    feature = 'locations'
    fk_field = 'location'

    class Meta:
        unique_together = ('content_type', 'entity_id', 'location')

    def __unicode__(self):
        return unicode(self.entity) + ': ' + unicode(self.location)
