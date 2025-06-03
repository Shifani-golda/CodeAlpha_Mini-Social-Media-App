from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('socialapp', '0001_initial'),  # replace with your latest migration name
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='profile_pic',
            field=models.ImageField(upload_to='profile_pics/', null=True, blank=True),
        ),
    ]
