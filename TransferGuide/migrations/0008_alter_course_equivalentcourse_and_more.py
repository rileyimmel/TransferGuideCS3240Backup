# Generated by Django 4.1.7 on 2023-03-31 22:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TransferGuide', '0007_requestform_studentemail_alter_requestform_pending'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='equivalentCourse',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='nonEquivalentCourse',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
    ]