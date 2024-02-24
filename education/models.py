from django.db import models
from django.utils.translation import gettext_lazy as _


class University(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_("University"))

    def __str__(self):
        return self.name


class Major(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Major"))

    def __str__(self):
        return self.name


class Degree(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Degree"))

    def __str__(self):
        return self.name


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Skill"))

    # description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
