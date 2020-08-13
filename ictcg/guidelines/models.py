import logging
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from wagtailtrans.models import TranslatablePage, Language
from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey
from wagtail.core.models import Orderable, Page
from wagtail.snippets.models import register_snippet
from wagtail.admin.edit_handlers import (
    FieldPanel,
    MultiFieldPanel,
    StreamFieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.core.fields import RichTextField, StreamField
from wagtail.search import index
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from ictcg.guidelines.choices import COLOUR_CHOICES
from ictcg.streams import blocks


class GuidelinesListingPage(TranslatablePage):
    """
    A TranslatablePage class used for the entry to the guidelines section of the site. 
    The page contains a list of the child (GuidelinesSectionPage)
    """

    parent_page_types = ["base.HomePage"]
    subpage_types = ["guidelines.GuidelinesSectionPage"]

    introduction = RichTextField(blank=True, default="")

    search_fields = Page.search_fields + [
        index.SearchField('introduction'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('introduction'),
    ]

    def get_context(self, request, *args, **kwards):
        context = super().get_context(request, *args, **kwards)
        context['descendants'] = Page.objects.child_of(self).live()
        return context

class GuidelinesSectionPage(TranslatablePage):
    """
    A TranslatablePage class used for each subsection with the guidelines section.
    """

    parent_page_types = ["guidelines.GuidelinesListingPage"]
    subpage_types = ["guidelines.GuidancePage"]

    introduction = RichTextField(blank=True, default="")

    subtitle = models.CharField(
        max_length=140,
        blank=False
    )

    body = RichTextField(blank=True, default="")

    section_colour = models.CharField(
        max_length=140,
        choices=COLOUR_CHOICES,
        null=False,
        blank=False
    )

    landing_page_summary = models.CharField(
        max_length=240,
        null=True,
        blank=False,
        help_text=_("Text to be shown on the guidelines landing page")
    )

    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
        FieldPanel("subtitle"),
        FieldPanel("body"),
        FieldPanel("section_colour"),
        FieldPanel("landing_page_summary"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField('introduction'),
        index.SearchField('body'),
    ]

    def save(self,  *args, **kwards):
        try:
            listing = self.get_parent()
            clear_guidelines_listing_cache(self.language.code, listing.id)
        except Exception:
            logging.error('Error deleting GuidelinesSectionPage cache')
            pass

        return super().save(*args, **kwards)

# TODO: Hide snippets for other languages
# class CustomizedChooserPanel(SnippetChooserPanel):
#   def on_form_bound(self):
#     page_language = self.form.initial['language']
#     language_code = Language.objects.get(id=page_language)
#     choices = MoreInformationModule.objects.filter(language=language_code.code)
#     self.form.fields["more_information_module"].queryset = choices
#     super().on_form_bound()

class GuidancePage(TranslatablePage):
    """
    A TranslatablePage class used for the many content pages for each guidelines subsection
    """

    parent_page_types = ["guidelines.GuidelinesSectionPage"]
    subpage_types = []

    introduction = RichTextField(blank=True, default="")

    body = StreamField([
        ("content_section", blocks.RichTextWithTitleBlock()),
        ("dos_and_donts", blocks.DosAndDontsBlock()),
    ], null=True, blank=True)

    content_panels = TranslatablePage.content_panels + [
        FieldPanel("introduction"),
        StreamFieldPanel("body"),
    ]

    more_information_module = models.ForeignKey(
        'modules.MoreInformationModule',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    links_module = models.ForeignKey(
        'modules.LinksModule',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    Sidebar_panels = [
        SnippetChooserPanel("more_information_module"),
        SnippetChooserPanel("links_module")
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(Sidebar_panels, heading='Sidebar'),
        ObjectList(TranslatablePage.settings_panels, heading='Settings'),
        ObjectList(TranslatablePage.promote_panels, heading='Promote')
    ])

    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]

    def get_context(self, request, *args, **kwards):
        context = super().get_context(request, *args, **kwards)
        guidelines = GuidelinesListingPage.objects.ancestor_of(self).live().first()
        context['guidelines_title'] = guidelines.title
        context['section'] = GuidelinesSectionPage.objects.ancestor_of(self).live().first()

        prev_page = self.get_prev_siblings().live().first()
        next_page = self.get_next_siblings().live().first()

        if prev_page == None:
            prev_page = self.get_parent().specific
            prev_page.title = prev_page.subtitle

        if next_page == None:
            next_page = self.get_parent().get_next_siblings().live().first()

        context['prev_page'] = prev_page
        context['next_page'] = next_page

        return context

    def save(self, *args, **kwards):
        try:
            section = self.get_parent()
            listing = section.get_parent()
            clear_guidelines_listing_cache(self.language.code, listing.id)
            clear_guidelines_section_cache(section.id)
        except Exception:
            logging.error('Error deleting GuidancePage cache')
            pass

        return super().save(*args, **kwards)

def clear_guidelines_section_cache(section_id):
    section_key = make_template_fragment_key("guidelines_sections_children", [section_id])
    cache.delete(section_key)

def clear_guidelines_listing_cache(language_code, listing_id):
    guidelines_key = make_template_fragment_key("guidelines_listing_descendant", [listing_id])
    guidelines_footer_key = make_template_fragment_key("guidelines_footer", [language_code])
    cache.delete_many([guidelines_key, guidelines_footer_key])

@receiver(pre_delete, sender=GuidelinesSectionPage)
@receiver(pre_delete, sender=GuidancePage)
def on_guidance_page_delete(sender, instance, **kwargs):
    """ On a guidance or section page delete, clear the cache for the section and listings pages"""
    listing = instance.get_parent()
            
    if sender.__name__ == 'GuidancePage':
        section = instance.get_parent()
        listing = section.get_parent()
        if section.id:
            clear_guidelines_section_cache(section.id)

    if listing.id:
        clear_guidelines_listing_cache(instance.language.code, listing.id)
