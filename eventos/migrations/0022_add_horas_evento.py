from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0021_alter_evento_estado'),
    ]

    operations = [
        migrations.AddField(
            model_name='evento',
            name='hora_inicio',
            field=models.TimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='evento',
            name='hora_fin',
            field=models.TimeField(null=True, blank=True),
        ),
    ]
