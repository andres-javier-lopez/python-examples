# loader.py
This module read snippets and layouts html files and renders them with information
provided on variables. Uses regular expresion to replace some parts of the html.

# models.py
Database definition for a list of videos, with providers, categories and tags.
Using Django ORM.

# views.py
Django views to render a list of videos.

# sections.py
A Pyramid view that is used to create some endpoints for a REST API.

# views2.py
Pyramid views based on callable objects that render different parts of a website
utilizing an external library.