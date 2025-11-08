from django.db import migrations

DEFAULT_CATEGORIES = [
    ('solar', 'Solar'),
]


def create_categories(apps, schema_editor):
    BlogCategory = apps.get_model('blog', 'BlogCategory')
    for slug, name in DEFAULT_CATEGORIES:
        BlogCategory.objects.get_or_create(slug=slug, defaults={'name': name})


def delete_categories(apps, schema_editor):
    BlogCategory = apps.get_model('blog', 'BlogCategory')
    slugs = [slug for slug, _ in DEFAULT_CATEGORIES]
    BlogCategory.objects.filter(slug__in=slugs, posts__isnull=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_remove_blogpost_location_remove_blogpost_results_and_more'),
    ]

    operations = [
        migrations.RunPython(create_categories, delete_categories),
    ]
