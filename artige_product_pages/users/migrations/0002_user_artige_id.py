# Generated by Django 2.1.7 on 2019-03-20 20:00

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='artige_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='Artige ID'),
        ),
    ]
