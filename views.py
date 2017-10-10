# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import math

from django.http import Http404
from django.shortcuts import render

from embedvideos.models import Video, Category, Tag


def get_videos_context(request, query):
    total_videos = query.count()
    total_pages = int(math.ceil(total_videos/20))

    if 'p' in request.GET:
        current_page = int(request.GET['p'])
    else:
        current_page = 1

    if current_page > total_pages:
        current_page = total_pages

    initial_video = 20*(current_page - 1)
    last_video = 20*current_page

    videos = query[initial_video:last_video]

    if current_page > 4:
        init_page = current_page - 2
    else:
        init_page = 1

    if total_pages - current_page > 3:
        end_page = current_page + 2 + 1
    else:
        end_page = total_pages + 1

    pages = range(init_page, end_page)

    context = {
        'videos': videos,
        'pages': pages,
        'current_page': current_page,
        'total_pages': total_pages
    }
    return context


def list_videos(request):
    context = get_videos_context(request, Video.objects.all())
    context['filter'] = 'all'
    return render(request, 'embedvideos/videolist.html', context)


def search_videos(request):
    search_string= request.GET['s']
    search_terms = search_string.split(' ')
    query = Video.objects
    for term in search_terms:
        query = query.filter(name__icontains=term)
    context = get_videos_context(request, query)
    context['filter'] = search_string
    return render(request, 'embedvideos/videolist.html', context)


def list_category_videos_slug(request, category_slug):
    try:
        category = Category.objects.get(slug=category_slug)
    except Category.DoesNotExist:
        raise Http404("Category doesn't exists")

    return list_category_videos(request, category)


def list_category_videos_id(request, category_id):
    try:
        category = Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        raise Http404("Category doesn't exists")
    return list_category_videos(request, category)


def list_category_videos(request, category):
    context = get_videos_context(request, category.video_set.all())
    context['filter'] = category.name
    return render(request, 'embedvideos/videolist.html', context)


def list_tag_videos_slug(request, tag_slug):
    try:
        tag = Tag.objects.get(slug=tag_slug)
    except Tag.DoesNotExist:
        raise Http404("Tag doesn't exists")
    return list_tag_videos(request, tag)


def list_tag_videos_id(request, tag_id):
    try:
        tag = Tag.objects.get(id=tag_id)
    except Tag.DoesNotExist:
        raise Http404("Tag doesn't exists")
    return list_tag_videos(request, tag)


def list_tag_videos(request, tag):
    context = get_videos_context(request, tag.video_set.all())
    context['filter'] = tag.name
    return render(request, 'embedvideos/videolist.html', context)


def show_video_slug(request, video_slug):
    try:
        video = Video.objects.get(slug=video_slug)
    except Video.DoesNotExist:
        raise Http404("Video doesn't exists")
    return show_video(request, video)


def show_video_id(request, video_id):
    try:
        video = Video.objects.get(id=video_id)
    except Video.DoesNotExist:
        raise Http404("Video doesn't exists")
    return show_video(request, video)


def show_video(request, video):
    context = {
        'video': video
    }
    return render(request, 'embedvideos/video.html', context)
