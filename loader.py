#coding: utf-8
"""Manage the loading of template files"""
import codecs
import os
import re

import pystache

from inhouse.builder.lib import inhouse3 as inh


HERE = os.path.dirname(__file__)

STOCK_REGEX = r'<!-- stock -->(.<[^!]|[^<])*<!-- end -->'
GALLERY_REGEX = r'<!-- gallery -->(.<[^!]|[^<])*<!-- endgallery -->'
MENU_REGEX = r'<!-- menu -->(.<[^!]|[^<])*<!-- endmenu -->'
TEXT_REGEX = r'<!-- text -->(.<[^!]|[^<])*<!-- endtext -->'
SOCIAL_REGEX = r'<!-- socialmedia -->(.<[^!]|[^<])*<!-- endsocialmedia -->'


class Error(Exception):
    """Module standard exception"""
    pass


class LayoutNotFoundError(Error):
    """Layout file was not found"""
    pass


class SnippetNotFoundError(Error):
    """Snippet file was not found"""
    pass


class SnippetNotStockError(Error): 
    """Snippet does not support a stock of elements"""
    pass


class GalleryNotProvidedError(Error):
    """Gallery information was not provided"""
    pass


class WrongDataProvidedError(Error):
    """Data provided is wrong"""
    pass


def _open_snippet_file(snippet_type, snippet_name):
    """Open the snippet file then read and returns its content"""
    if '.html' not in snippet_name:
        snippet_name = '%s.html' % snippet_name

    file_path = os.path.join(HERE, 'snippets', snippet_type, snippet_name)
    if not os.path.exists(file_path):
        raise SnippetNotFoundError

    with codecs.open(file_path, encoding='utf-8') as snippet_file:
        snippet = snippet_file.read()

    return snippet


def _get_internal_stock(snippet, stock, regex, required=False):
    """Process an internal stock and retuns it as a variable"""
    match = re.search(regex, snippet, flags=re.DOTALL)
    if match:
        if not isinstance(stock, list):
            raise WrongDataProvidedError

        element_snippet = match.group(0)
        stock_list = []
        for element in stock:
            stock_list.append(pystache.render(
                element_snippet,
                element.get_vars()
            ))

        stock_html = u''.join(stock_list)
        return stock_html
    else:
        if required:
            raise SnippetNotStockError
        else:
            return ''


def _replace_internal_stock(snippet_vars, snippet, stock, regex,
                            stock_name='stock', required=False):
    """Replaces the snippet information with a loop"""
    stock_content = _get_internal_stock(snippet, stock, regex, required)

    count = 0
    while stock_content is not '':
        stock_var = '%s_%d' % (stock_name, count)
        snippet = re.sub(regex, '{{{%s}}}' % stock_var, snippet,
                         count=1, flags=re.DOTALL)
        snippet_vars[stock_var] = stock_content
        count += 1
        stock_content = _get_internal_stock(snippet, stock, regex, False)

    return (snippet, snippet_vars)

def get_snippet(snippet_type, snippet_name, snippet_data):
    """Gets and process the received snippet"""
    if snippet_type == 'headers':
        return get_header(snippet_name, snippet_data)

    if snippet_type == 'footers':
        return get_footer(snippet_name, snippet_data)

    snippet = _open_snippet_file(snippet_type, snippet_name)

    if isinstance(snippet_data, list):
        snippet, snippet_vars = _replace_internal_stock(
            {}, snippet, snippet_data, STOCK_REGEX, required=True
        )
    elif isinstance(snippet_data, inh.ApiObject):
        snippet_vars = snippet_data.get_vars()

        try:
            gallery = snippet_data.get('imagenes')
        except inh.AttributeNotFoundError:
            gallery = None

        try:
            snippet, snippet_vars = _replace_internal_stock(
                snippet_vars, snippet, gallery, GALLERY_REGEX
            )
        except WrongDataProvidedError:
            raise GalleryNotProvidedError
    else:
        snippet_vars = snippet_data

    return pystache.render(snippet, snippet_vars)


def get_header(snippet_name, snippet_data):
    """Returns a header type snippet

    This snippet has special behavior.
    """
    if not isinstance(snippet_data, inh.ApiObject):
        raise WrongDataProvidedError

    snippet = _open_snippet_file('headers', snippet_name)
    snippet_vars = snippet_data.get_vars()

    try:
        menu = snippet_data.get('menu')
    except inh.AttributeNotFoundError:
        menu = None

    snippet, snippet_vars = _replace_internal_stock(
        snippet_vars, snippet, menu, MENU_REGEX, stock_name='menu'
    )

    try:
        social_media = snippet_data.get('enlaces')
    except inh.AttributeNotFoundError:
        social_media = None

    snippet, snippet_vars = _replace_internal_stock(
        snippet_vars, snippet, social_media, SOCIAL_REGEX,
        stock_name='social_media'
    )

    return pystache.render(snippet, snippet_vars)


def get_footer(snippet_name, snippet_data):
    """Returns a footer type snippet

    This snippet has a special behavior.
    """
    if not isinstance(snippet_data, inh.ApiObject):
        raise WrongDataProvidedError

    snippet = _open_snippet_file('footers', snippet_name)
    snippet_vars = {}

    try:
        textos = snippet_data.get('textos')
    except inh.AttributeNotFoundError:
        textos = None

    snippet, snippet_vars = _replace_internal_stock(
        snippet_vars, snippet, textos, TEXT_REGEX, stock_name='texto'
    )

    try:
        gallery = snippet_data.get('imagenes')
    except inh.AttributeNotFoundError:
        gallery = None

    snippet, snippet_vars = _replace_internal_stock(
        snippet_vars, snippet, gallery, GALLERY_REGEX, stock_name='gallery'
    )

    try:
        social_media = snippet_data.get('enlaces')
    except inh.AttributeNotFoundError:
        social_media = None

    snippet, snippet_vars = _replace_internal_stock(
        snippet_vars, snippet, social_media, SOCIAL_REGEX,
        stock_name='social_media'
    )

    return pystache.render(snippet, snippet_vars)


class Theme(object):
    """Represents the theme used by the site layouts"""

    def __init__(self, theme):
        """Initializes the selected theme"""
        self.theme = theme
        self.layout_path = os.path.join(HERE, 'layouts', self.theme)

    def get_layout(self, layout_name, layout_vars=None):
        """Returns a layout processed by the system"""
        if '.html' not in layout_name:
            layout_name = '%s.html' % layout_name
        file_path = os.path.join(self.layout_path, layout_name)
        if not os.path.exists(file_path):
            raise LayoutNotFoundError

        with codecs.open(file_path, encoding='utf-8') as layout_file:
            layout = layout_file.read()

        if not layout_vars:
            layout_vars = {}

        return pystache.render(layout, layout_vars)
