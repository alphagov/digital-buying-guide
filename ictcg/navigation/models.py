import logging
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey

from wagtail.core.models import Orderable
from wagtail.admin.edit_handlers import FieldPanel, PageChooserPanel, InlinePanel, MultiFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel

class MainMenu(ClusterableModel):
  """
  MainMenu class for header links. Contains Orderable MenuItem class.
  """

  admin_title = models.CharField(
    max_length=100, 
    blank=False,
    null=True
  )

  title = models.CharField(max_length=100)

  language = models.CharField(
    max_length=100, 
    choices=settings.LANGUAGES
  )

  logo = models.ForeignKey(
    'wagtailimages.Image',
    blank=False,
    null=True,
    related_name='+',
    on_delete=models.SET_NULL,
  )

  button_text = models.CharField(
    max_length=100, 
    blank=False,
    null=False,
    default="Menu"
  )

  button_aria_label = models.CharField(
    max_length=100, 
    default="Show or hide Top Level Navigation",
    help_text=_('Description for navigation button aria label'),
  )

  navigation_aria_label = models.CharField(
    max_length=100,
    default="Top Level Navigation",
    help_text=_('Description for navigation aria label'),
  )

  panels = [
    FieldPanel("title"),
    FieldPanel("language"),
    ImageChooserPanel("logo"),
    FieldPanel("button_text"),
    FieldPanel("button_aria_label"),
    FieldPanel("navigation_aria_label"),
    InlinePanel("menu_items", label="Menu Item")
  ]

  def __str__(self):
    language = dict(settings.LANGUAGES)
    return f"{self.title} - {language[self.language]}"

class MenuItem(models.Model):
  """
  Reuseable class for menu item links
  """

  title = models.CharField(max_length=100, blank=True)
  url = models.CharField(max_length=500, blank=True)
  page = models.ForeignKey(
    'wagtailcore.Page',
    null=True,
    blank=True,
    related_name="+",
    on_delete=models.CASCADE
  )
  open_in_new_tab = models.BooleanField(default=False, blank=True)

  panels = [
    FieldPanel("title"),
    FieldPanel("url"),
    PageChooserPanel("page"),
    FieldPanel("open_in_new_tab"),
  ]

  @property
  def link(self):
    if self.page:
      return self.page.url
    elif self.url:
      return self.url
    return "#"


class MainMenuItem(Orderable, MenuItem):
  """
   A class that extends Orderable and MenuItem classe for the main menu link items.
   Extending Orderable allow for links to be arranaged in the order choosen by the user
  """
  panels = MenuItem.panels + []
  links = ParentalKey("MainMenu", related_name="menu_items")

class FooterMenu(ClusterableModel):
  """
  FooterMenu class for footer links. Contains Orderable MenuItem class.
  """

  admin_title = models.CharField(
    max_length=100, 
    blank=False,
    null=True
  )

  language = models.CharField(
    max_length=100, 
    choices=settings.LANGUAGES
  )

  sponsors_title = models.CharField(
    max_length=100, 
    blank=False,
    null=True,
  )

  panels = [
    FieldPanel("admin_title"),
    FieldPanel("language"),
    InlinePanel("footer_menu_items", label="Menu Item"),
    MultiFieldPanel(
      [
        FieldPanel("sponsors_title"),
        InlinePanel("sponsor_items", label="Sponsor Items")
      ],
      heading=_('Sponsors'),
    ),
  ]

  def __str__(self):
    language = dict(settings.LANGUAGES)
    return f"{self.admin_title} - {language[self.language]}"
  
  def save(self, *args, **kwards):
    try:
      clear_footer_cache(self.language)
    except Exception:
      logging.error('Error deleting footer cache')
      pass
    return super().save(*args, **kwards)

class FooterMenuItem(Orderable, MenuItem):
  """
   A class that extends Orderable and MenuItem classe for the main menu link items.
   Extending Orderable allow for links to be arranaged in the order choosen by the user
  """
  panels = MenuItem.panels + []
  links = ParentalKey("FooterMenu", related_name="footer_menu_items")


class SponsorItem(Orderable):
  """
  SponsorItem class for footer sponsors.
  """
  name = models.CharField(
    max_length=140, 
    blank=True, 
    help_text='Title'
  )

  url = models.URLField(blank=True, help_text=_("URL for sponsor link"))

  logo = models.ForeignKey(
    'wagtailimages.Image',
    blank=False,
    null=True,
    related_name='+',
    help_text=_('Sponsor image or logo'),
    on_delete=models.SET_NULL,
  )

  panels = [
    FieldPanel("name"),
    FieldPanel("url"),
    ImageChooserPanel("logo"),
  ]

  sponsor = ParentalKey("FooterMenu", related_name="sponsor_items", default='')

def clear_footer_cache(language_code):
  sponsors = make_template_fragment_key("footer_sponsors", [language_code])
  support_link = make_template_fragment_key("footer_support_links", [language_code])
  cache.delete_many([sponsors, support_link])

@receiver(pre_delete, sender=FooterMenu)
def on_footer_menu_delete(sender, instance, **kwargs):
  """ On footer menu delete, clear the cache """
  clear_footer_cache(instance.language)
