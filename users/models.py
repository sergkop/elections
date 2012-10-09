# -*- coding:utf-8 -*-
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models

from elements.participants.models import EntityParticipant
from elements.models import BaseEntityManager, BaseEntityModel, ENTITIES_MODELS, \
        entity_class, HTMLField
from locations.models import Location

class ProfileManager(BaseEntityManager):
    def get_info(self, data, ids):
        # TODO: add info on non-profile entities followed by the user

        # Get contacts
        contacts = EntityParticipant.objects.participant_in('follower', ids, Profile)
        contacts_ids = set(c_id for id in ids for c_id in contacts[id]['ids'])
        contacts_by_id = Profile.objects.only('id', 'first_name', 'last_name', 'rating') \
                .in_bulk(contacts_ids)

        for id in ids:
            data[id]['contacts'] = {
                'count': contacts[id]['count'],
                'entities': [contacts_by_id[c_id].display_info() for c_id in contacts[id]['ids']],
            }

        # Get data for related entities
        participants_data = list(EntityParticipant.objects.filter(person__in=ids) \
                .values_list('content_type', 'entity_id', 'role', 'person'))

    def get_related_info(self, data, ids):
        pass

@entity_class(['locations', 'participants'])
class Profile(BaseEntityModel):
    user = models.OneToOneField(User)

    first_name = models.CharField(u'Имя', max_length=40, help_text=u'на русском языке')
    last_name = models.CharField(u'Фамилия', max_length=40, help_text=u'на русском языке')

    about = HTMLField(u'О себе', default='', blank=True)

    objects = ProfileManager()

    entity_name = 'participants'
    entity_title = u'Участники'
    cache_prefix = 'user_info/'
    editable_fields = ['first_name', 'last_name', 'about']

    roles = ['follower']

    follow_button = {
        'role': 'follower',
        'cancel_msg': u'Вы хотите удалить этого пользователя из списка контактов?',
        'cancel_btn': u'Удалить',
        'cancel_btn_long': u'Удалить из контактов',
        'confirm_msg': u'Вы хотите добавить этого пользователя в список контактов?',
        'confirm_btn': u'Добавить',
        'confirm_btn_long': u'Добавить в контакты',
    }

    def info_data(self):
        data = super(Profile, self).info_data()
        data['full_name'] = unicode(self)
        return data

    def display_info(self):
        res = {
            'id': self.id,
            'url': self.get_absolute_url(),
            'full_name': unicode(self),
        }
        return res

    def calc_rating(self):
        info = self.info()
        rating = 0

        if self.about:
            rating += 0.1

        # TODO: take into account provided comments and contacts

        return rating

    def has_contact(self, profile):
        return EntityParticipant.objects.is_participant(profile, self, 'follower')

    @models.permalink
    def get_absolute_url(self):
        return ('profile', [self.user_id])

    def __unicode__(self):
        return self.first_name + u' ' + self.last_name

def create_profile(sender, **kwargs):
    if kwargs.get('created', False):
        profile = Profile()
        profile.user = kwargs['instance']
        profile.save()

models.signals.post_save.connect(create_profile, sender=User)

class Message(models.Model):
    sender = models.ForeignKey(Profile, verbose_name=u'Отправитель', related_name='sent_messages')
    receiver = models.ForeignKey(Profile, verbose_name=u'Получатель', related_name='received_messages')
    title = models.CharField(u'Тема', max_length=100)
    body = models.TextField(u'Сообщение')
    show_email = models.BooleanField(u'Показать email получателю', default=True)
    time = models.DateTimeField(auto_now=True)

MEMBER_CHOICES = (
    ('chairman', u'Председатель'),
    ('vice', u'Заместитель председателя'),
    ('secretary', u'Секретарь'),
    ('prg', u'Член с правом решающего голоса'),
    ('psg', u'Член с правом совещательного голоса'),
    ('other', u'Другое'),
)

PARTY_CHOICES = (
    ('ER', u'Единая Россия'),
    ('KPRF', u'КПРФ'),
    ('LDPR', u'ЛДПР'),
    ('SR', u'Справедливая Россия'),
    ('Yabloko', u'Яблоко'),
    ('other', u'Другое'),
)

class CommissionMember(models.Model):
    last_name = models.CharField(u'Фамилия', max_length=50)
    first_name = models.CharField(u'Имя', max_length=50)
    middle_name = models.CharField(u'Отчество', max_length=50, blank=True)
    role = models.CharField(u'Должность', max_length=100, choices=MEMBER_CHOICES)
    party = models.CharField(u'Кем выдвинут', max_length=100, choices=PARTY_CHOICES)
    job = models.CharField(u'Место работы', max_length=100, blank=True)

    user = models.ForeignKey(Profile)
    location = models.ForeignKey(Location)
    time = models.DateTimeField(auto_now=True)

class WebObserver(models.Model):
    start_time = models.IntegerField(u'Начало наблюдения', help_text=u'Местное время')
    end_time = models.IntegerField(u'Окончание наблюдения')
    capture_video = models.BooleanField(u'Будет ли производиться захват видео', default=False)
    url = models.URLField(u'Ссылка на видео', blank=True)

    user = models.ForeignKey(Profile)
    location = models.ForeignKey(Location)
    time = models.DateTimeField(auto_now=True)

ROLES_DATA = (
    ('voter', u'Избиратель', u'Избиратели'),
    ('observer', u'Наблюдатель', u'Наблюдатели'),
    ('member', u'Член избирательной комиссии', u'Члены избирательной комиссии'),
    ('journalist', u'Журналист', u'Журналисты'),
    ('lawyer', u'Юрист', u'Юристы'),
)

ROLE_CHOICES = [(name, title) for name, title, plural in ROLES_DATA]
ROLE_CHOICES_PLURAL = [(name, plural) for name, title, plural in ROLES_DATA]
ROLE_TYPES = dict(ROLE_CHOICES)

class RoleManager(models.Manager):
    def get_participants(self, query):
        participants = {}

        roles_by_type = {}
        for role_id, role_type in list(self.filter(query).values_list('id', 'type')):
            roles_by_type.setdefault(role_type, []).append(role_id)

        role_ids = []
        for role_type in roles_by_type:
            # TODO: Temporary hack
            role_ids += roles_by_type[role_type][:10]

        for role in list(Role.objects.filter(id__in=role_ids).select_related('profile')):
            participants.setdefault(role.type, []).append(role)

        for role in participants:
            participants[role] = sorted(participants[role], key=lambda r: unicode(r.profile))

        return participants

class Role(models.Model):
    profile = models.ForeignKey(Profile, related_name='roles_set')
    location = models.ForeignKey(Location)
    type = models.CharField(max_length=10, choices=ROLE_CHOICES, db_index=True)
    time = models.DateTimeField(auto_now=True)

    objects = RoleManager()

    class Meta:
        unique_together = ('profile', 'location', 'type')

    def type_name(self):
        return ROLE_TYPES[self.type]

    def __unicode__(self):
        return unicode(self.profile) + ' is ' + self.type + ' at ' + unicode(self.location)
