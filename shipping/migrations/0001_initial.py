import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('length_cm', models.DecimalField(decimal_places=2, max_digits=8)),
                ('width_cm', models.DecimalField(decimal_places=2, max_digits=8)),
                ('height_cm', models.DecimalField(decimal_places=2, max_digits=8)),
                ('weight_kg', models.DecimalField(decimal_places=2, max_digits=8)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Box',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('internal_length_cm', models.DecimalField(decimal_places=2, max_digits=8)),
                ('internal_width_cm', models.DecimalField(decimal_places=2, max_digits=8)),
                ('internal_height_cm', models.DecimalField(decimal_places=2, max_digits=8)),
                ('max_weight_kg', models.DecimalField(decimal_places=2, max_digits=8)),
                ('cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['cost'],
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('reference', models.CharField(max_length=100, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(
                    choices=[
                        ('PENDING', 'Pending'),
                        ('PROCESSING', 'Processing'),
                        ('COMPLETED', 'Completed'),
                    ],
                    default='PENDING',
                    max_length=20,
                )),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('order', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='items',
                    to='shipping.order',
                )),
                ('product', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='order_items',
                    to='shipping.product',
                )),
            ],
        ),
    ]
