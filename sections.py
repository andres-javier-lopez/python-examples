# coding: utf8

import json

from pyramid import httpexceptions as ex
from pyramid import view
from inhouse.database import models

@view.view_defaults(renderer='json')
class SectionsEditionView(object):
    def __init__(self, request):
        self.db_session = request.db_session
        self.request = request
        self.user = request.matchdict['user']

    @view.view_config(route_name='sections_edition')
    def section_view(self):
        if self.request.method == 'POST':
            return self.update_order()
        elif self.request.method == 'PUT':
            return self.update_section()
        else:
            raise ex.HTTPMethodNotAllowed

    def update_order(self):
        """Modify stock order"""
        body = self.request.body
        data = json.loads(body)

        position = 0
        for id_section in data['sections']:
            if id_section:
                section = self.db_session.query(models.Section).get(id_section)
                position += 1
                section.position = position

        self.db_session.flush()
        return {'status': 'ok'}

    def update_section(self):
        """Modify a section on the database"""
        data = json.loads(self.request.body)

        section =  {}

        element = self.db_session.query(
            models.Elements
        ).get(data['element']['id'])

        for field in element.fields:
            try:
                field.value = data['element']['fields'][field.field.name]
                if field.field.name == 'title':
                    element.name = field.value
            except KeyError:
                pass

        section_styles = self.db_session.query(
            models.SectionStyle
        ).filter(
            models.SectionStyle.id_section == data['element']['section']['id']
        ).all()


        stock_styles = {}

        for style in section_styles:
            if style.field not in stock_styles:
                stock_styles[style.field] = {}

            stock_styles[style.field][style.style] = style.value


        for (field_name, styles) in data['element']['styles'].iteritems():

            for (style, value) in styles.iteritems():

                if field_name not in stock_styles:
                    new_style = models.SectionStyle(
                        field = field_name,
                        style = style,
                        value = value,
                        id_section = data['element']['section']['id']
                    )
                    self.db_session.add(new_style)

                else:
                    if style not in stock_styles[field_name]:
                        new_style = models.SectionStyle(
                            field = field_name,
                            style = style,
                            value = value,
                            id_section = data['element']['section']['id']
                        )
                        self.db_session.add(new_style)

                    else:
                        element_style = self.db_session.query(
                            models.SectionStyle
                        ).filter(
                            models.SectionStyle.id_section == data['element']['section']['id']
                        ).filter(
                            models.SectionStyle.field == field_name
                        ).filter(
                            models.SectionStyle.style == style
                        ).first()

                        element_style.value = value

        self.db_session.flush()

        section['element'] = element

        return section
