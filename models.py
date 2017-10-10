# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import itertools

from django.db import models
from django.utils.text import slugify


def get_slug(model, name, max_length):
    slug = orig = slugify(name)[:max_length]
    for x in itertools.count(1):
        if not model.objects.filter(slug=slug).exists():
            break
        slug = "%s-%d" % (orig[:max_length - len(str(x)) - 1], x)
    return slug


class Provider(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Category(models.Model):
    prepopulated_fields = {'slug': ('name',)}
    name = models.CharField(max_length=100)
    slug = models.SlugField(blank=True, max_length=100, null=True, unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = get_slug(Category, self.name, 100)
        super(Category, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "categories"


class Tag(models.Model):
    prepopulated_fields = {'slug': ('name',)}
    name = models.CharField(max_length=100)
    slug = models.SlugField(blank=True, max_length=100, null=True, unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = get_slug(Tag, self.name, 100)
        super(Tag, self).save(*args, **kwargs)


class Video(models.Model):
    prepopulated_fields = {'slug': ('name',)}
    url = models.CharField(max_length=250)
    video_id = models.CharField(max_length=100, null=True)
    name = models.CharField(blank=True, max_length=250)
    slug = models.SlugField(blank=True,max_length=250, null=True, unique=True)
    provider = models.ForeignKey(Provider, blank=True, null=True)
    categories = models.ManyToManyField(Category, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    description = models.TextField(blank=True)
    image = models.CharField(blank=True, max_length=250)
    embed = models.TextField(blank=True)
    published_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = get_slug(Video, self.name, 100)
        super(Video, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-published_on']
        unique_together = ('video_id', 'provider')
