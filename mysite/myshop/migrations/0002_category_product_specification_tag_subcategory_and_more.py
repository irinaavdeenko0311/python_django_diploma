# Generated by Django 4.2.2 on 2023-07-03 15:55

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myshop', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=20)),
                ('image', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='myshop.image')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=8, validators=[django.core.validators.MinValueValidator(0.01)])),
                ('count', models.PositiveSmallIntegerField(default=0)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('title', models.CharField(max_length=20)),
                ('description', models.CharField(max_length=30)),
                ('fullDescription', models.TextField(blank=True, null=True)),
                ('freeDelivery', models.BooleanField(default=True)),
                ('rating', models.PositiveSmallIntegerField(validators=[django.core.validators.MaxValueValidator(5)])),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myshop.category')),
                ('images', models.ManyToManyField(related_name='product_image', to='myshop.image')),
            ],
        ),
        migrations.CreateModel(
            name='Specification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('value', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Subcategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=20)),
                ('categories', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myshop.category')),
                ('image', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='myshop.image')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', models.CharField(max_length=30)),
                ('email', models.EmailField(max_length=50)),
                ('text', models.TextField(blank=True, null=True)),
                ('rate', models.PositiveSmallIntegerField(validators=[django.core.validators.MaxValueValidator(5)])),
                ('date_time', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myshop.product')),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='specification',
            field=models.ManyToManyField(related_name='product_specification', to='myshop.specification'),
        ),
        migrations.AddField(
            model_name='product',
            name='tags',
            field=models.ManyToManyField(related_name='product_tag', to='myshop.tag'),
        ),
    ]
