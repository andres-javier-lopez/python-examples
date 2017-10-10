# coding: utf-8

from pyramid import response
import sqlalchemy

from inhouse.database import models
from inhouse.views.site import preview


def get_site_id(domain, db_session):
    site = db_session.query(models.Site).filter(
        models.Site.domain == domain.replace('www.', '', 1)
    ).one()
    return site.id


class INhPublishHome(object):
    def __init__(self, request):
        self.request = request
        self.domain = request.domain
        self.db_session = request.db_session

    def __call__(self):
        try:
            return self.render()
        except sqlalchemy.orm.exc.NoResultFound:
            return preview.show404()
        except sqlalchemy.orm.exc.MultipleResultsFound:
            return response.Response('Configuration error',
                                     status_int=500)
        except preview.NotFoundError:
            return preview.show404()

    def render(self):
        id_site = get_site_id(self.domain, self.db_session)
        site = self.db_session.query(models.Site).get(id_site)

        try:
            payment = self.db_session.query(models.Payments).filter(
                models.Payments.id_site == id_site).one()
        except sqlalchemy.orm.exc.NoResultFound:
            payment = False

        if site.published is False:
            return preview.showBuilding()
        else:
            if payment is False:
                return preview.showUnavalaible()
            else:
                site_builder = preview.SiteBuilder(self.request, id_site,
                                                   self.db_session,
                                                   domain=self.domain,
                                                   is_domain=True)
                layout = site_builder.get_page_layout(
                    site_builder.get_home_id()
                )
                return response.Response(layout)


class INhPublishPage(object):
    def __init__(self, request):
        self.request = request
        self.domain = request.domain
        self.page_id = int(request.matchdict['menu'])

    def __call__(self):
        try:
            return response.Response(self.render())
        except sqlalchemy.orm.exc.NoResultFound:
            return preview.show404()
        except sqlalchemy.orm.exc.MultipleResultsFound:
            return response.Response('Configuration error',
                                     status_int=500)
        except preview.NotFoundError:
            return preview.show404()

    def render(self):
        site_builder = preview.SiteBuilder(self.request,
                                           get_site_id(self.domain,
                                                       self.request.db_session),
                                           self.request.db_session,
                                           domain=self.domain, is_domain=True)
        layout = site_builder.get_page_layout(self.page_id)
        return layout


class INhPublishElement(object):
    def __init__(self, request):
        self.request = request
        self.domain = request.domain
        self.page_id = int(request.matchdict['menu'])
        self.element_id = int(request.matchdict['element'])

    def __call__(self):
        try:
            return response.Response(self.render())
        except sqlalchemy.orm.exc.NoResultFound:
            return preview.show404()
        except sqlalchemy.orm.exc.MultipleResultsFound:
            return response.Response('Configuration error',
                                     status_int=500)
        except preview.NotFoundError:
            return preview.show404()

    def render(self):
        site_builder = preview.SiteBuilder(self.request,
                                           get_site_id(self.domain,
                                                       self.request.db_session),
                                           self.request.db_session,
                                           domain=self.domain, is_domain=True)
        layout = site_builder.get_stock_layout(self.element_id)
        return layout


class INhPublishAll(object):
    def __init__(self, request):
        self.request = request
        self.domain = request.domain
        self.section_id = int(request.matchdict['section'])

    def __call__(self):
        try:
            return response.Response(self.render())
        except sqlalchemy.orm.exc.NoResultFound:
            return preview.show404()

    def render(self):
        site_builder = preview.SiteBuilder(self.request,
                                           get_site_id(self.domain,
                                                       self.request.db_session),
                                           self.request.db_session,
                                           domain=self.domain, is_domain=True)
        layout = site_builder.get_all_layout(self.section_id)
        return layout
