from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regulatory', '0002_legalframework_scrapingsource'),
    ]

    operations = [
        migrations.AddField(
            model_name='legalframework',
            name='issuing_entity',
            field=models.CharField(blank=True, db_index=True, help_text='Ministerio, agencia u organismo que expide la normativa', max_length=200, verbose_name='Entidad emisora'),
        ),
        migrations.AlterField(
            model_name='legalframework',
            name='year',
            field=models.PositiveIntegerField(db_index=True, help_text='Año de expedición', verbose_name='Año'),
        ),
    ]
