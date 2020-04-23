# Generated by Django 3.0.5 on 2020-04-22 15:21

from django.db import migrations, models
import django.db.models.deletion
import wagtail.core.blocks
import wagtail.core.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('wagtailtrans', '0009_create_initial_language'),
        ('modules', '0001_squashed_0002_auto_20200422_1348'),
    ]

    operations = [
        migrations.CreateModel(
            name='GuidelinesListingPage',
            fields=[
                ('translatablepage_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailtrans.TranslatablePage')),
                ('introduction', wagtail.core.fields.RichTextField(blank=True, default='')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailtrans.translatablepage',),
        ),
        migrations.CreateModel(
            name='GuidelinesSectionPage',
            fields=[
                ('translatablepage_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailtrans.TranslatablePage')),
                ('subtitle', models.CharField(max_length=140)),
                ('section_colour', models.CharField(choices=[('#25a898', 'Green'), ('#007fc2', 'Blue'), ('#79b04a', 'Lime'), ('#7f97ab', 'Grey')], max_length=140)),
                ('landing_page_summary', models.CharField(help_text='Text to be shown on the guidelines landing page', max_length=240, null=True)),
                ('body', wagtail.core.fields.StreamField([('content', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(help_text='Section title, max length 120 characters', max_length=120)), ('content', wagtail.core.blocks.RichTextBlock())]))], blank=True, null=True)),
                ('sub_sections_title', models.CharField(help_text='Title for child pages under this section', max_length=140)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailtrans.translatablepage',),
        ),
        migrations.CreateModel(
            name='GuidelinePage',
            fields=[
                ('translatablepage_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailtrans.TranslatablePage')),
                ('body', wagtail.core.fields.StreamField([('content_section', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(help_text='Section title, max length 120 characters', max_length=120)), ('content', wagtail.core.blocks.RichTextBlock())])), ('dos_and_donts', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(help_text="Do's and dont's title", max_length=200)), ('dos', wagtail.core.blocks.ListBlock(wagtail.core.blocks.StructBlock([('item', wagtail.core.blocks.CharBlock(help_text='Item text', max_length=250))]))), ('donts', wagtail.core.blocks.ListBlock(wagtail.core.blocks.StructBlock([('item', wagtail.core.blocks.CharBlock(help_text='Item text', max_length=250))])))]))], blank=True, null=True)),
                ('links_module', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='modules.LinksModule')),
                ('more_information_module', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='modules.MoreInformationModule')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailtrans.translatablepage',),
        ),
    ]