# -*- coding:utf-8 -*-
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('navigation.views',
    url(r'^$', 'main', name='main'),
    url(r'^wall$', 'wall', name='wall'),
    url(r'^participants$', 'country_participants', name='participants'),
    url(r'^elections$', 'country_elections', name='elections'),

    url(r'^feedback$', 'feedback', name='feedback'),
    url('^feedback_thanks$', 'static_page', kwargs={'template': 'feedback/thanks.html'}, name='feedback_thanks'),

    url(r'^sitemap$', 'sitemap', name='sitemap'),
)

def static_tabs_urls(base_template, tabs_short):
    """
    tabs_short=[(name, title, temsplate, view), ...]
    name here coincides with url slug.
    """
    tabs = [(name, title, '/'+name, template)
            for name, title, template, view in tabs_short]

    urls = []
    for name, title, template, view in tabs_short:
        kwargs = {
            'tab': name,
            'template': base_template,
            'tabs': tabs,
            'template_path': template,
            'title': title,
        }
        urls.append(url(r'^'+name+'$', view or 'navigation.views.static_page',
                kwargs, name=name))

    return urls

urlpatterns += patterns('',
    *static_tabs_urls('static_pages/about/base.html', [
        ('about', u'Описание', 'static_pages/about/about.html', ''),
        ('rules', u'Правила площадки', 'static_pages/about/rules.html', ''),
        ('publications', u'О нас в СМИ', 'static_pages/about/publications.html', ''),
    ])
)
