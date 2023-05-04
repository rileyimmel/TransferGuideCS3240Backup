
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TransferGuide', '0010_remove_requestform_approval_requestform_accepted_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='requestform',
            name='accepted',
        ),
        migrations.RemoveField(
            model_name='requestform',
            name='pending',
        ),
        migrations.RemoveField(
            model_name='requestform',
            name='rejected',
        ),
        migrations.AddField(
            model_name='requestform',
            name='status',
            field=models.CharField(default='Pending', max_length=7),
        ),
    ]
