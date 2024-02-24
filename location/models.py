from django.db import models
from django.utils.translation import gettext_lazy as _
# from django.contrib.gis.db import models as gis_models
class Nationality(models.Model):
    nationality = models.CharField(max_length=50, blank=True, verbose_name=_("Nationality"))

    def __str__(self):
        return self.nationality


class Location(models.Model):
    city = models.CharField(max_length=50, blank=True, verbose_name=_("City"))
    country = models.CharField(max_length=50, blank=True, verbose_name=_("Country"))
    # s = gis_models.PointField(srid=4326)
    def __str__(self):
        return f"{self.city}, {self.country}"


