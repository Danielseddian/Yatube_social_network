# Generated by Django 2.2.6 on 2021-04-20 05:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0014_auto_20210416_1221'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, help_text='Можно добавить изображение', null=True, upload_to='posts/', verbose_name='Изображение'),
        ),
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(fields=('user', 'author'), name='follows'),
        ),
    ]
