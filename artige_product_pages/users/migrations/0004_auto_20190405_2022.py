# Generated by Django 2.1.7 on 2019-04-05 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20190405_1945'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instagramaccount',
            name='insta_id',
            field=models.IntegerField(verbose_name='Instagram ID'),
        ),
    ]
