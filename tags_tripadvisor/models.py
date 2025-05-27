from django.db import models

from django.db import models


class TagsTripadvisor(models.Model):
    id = models.AutoField(primary_key=True)  # ID autoincrementable
    place = models.TextField(null=True, blank=True)
    category = models.TextField(null=True, blank=True)
    tag = models.TextField(null=True, blank=True)
    id_element_html = models.TextField(null=True, blank=True)
    id_element = models.TextField(null=True, blank=True)
    id_element_html_modal = models.TextField(null=True, blank=True)
    category_url = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.place} - {self.category} - {self.tag}"

    class Meta:
        db_table = 'tags_tripadvisor'  # Cambia el nombre de la tabla
