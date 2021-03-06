# Generated by Django 3.1.7 on 2021-04-13 05:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('aiuts', '0005_auto_20210409_1111'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pending',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Type', models.CharField(choices=[('TU', 'Top Up'), ('ROP', 'Request of Payment')], default='Not fill', max_length=256)),
                ('Complete_status', models.BooleanField(default=False)),
                ('Transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aiuts.transaction')),
            ],
        ),
    ]
