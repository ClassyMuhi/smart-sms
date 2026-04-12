# Generated migration for Emergency & Safety System

from django.db import migrations, models
import django.db.models.deletion
import uuid
from django.conf import settings


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EmergencySOS',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('reason', models.CharField(choices=[('medical', 'Medical Emergency'), ('accident', 'Accident'), ('fire', 'Fire'), ('theft', 'Theft/Crime'), ('lost', 'Lost/Missing'), ('other', 'Other')], default='other', max_length=20)),
                ('description', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('active', 'Active - Emergency ongoing'), ('resolved', 'Resolved - Emergency ended'), ('cancelled', 'Cancelled - False alarm')], db_index=True, default='active', max_length=20)),
                ('location_lat', models.FloatField(blank=True, null=True)),
                ('location_lon', models.FloatField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='emergency_sos', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Emergency SOS',
                'verbose_name_plural': 'Emergency SOS',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='LocationUpdate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('accuracy', models.FloatField(blank=True, null=True)),
                ('address', models.CharField(blank=True, max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('emergency_sos', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='location_updates', to='module_4_emergency.emergencysos')),
            ],
            options={
                'verbose_name': 'Location Update',
                'verbose_name_plural': 'Location Updates',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='EmergencyLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('action_type', models.CharField(choices=[('triggered', 'SOS Triggered'), ('contact_notified', 'Emergency Contact Notified'), ('message_sent', 'Alert Message Sent'), ('location_updated', 'Location Updated'), ('resolved', 'Emergency Resolved'), ('failed', 'Action Failed')], db_index=True, max_length=20)),
                ('details', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('emergency_sos', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='module_4_emergency.emergencysos')),
            ],
            options={
                'verbose_name': 'Emergency Log',
                'verbose_name_plural': 'Emergency Logs',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='emergencysos',
            index=models.Index(fields=['user', '-created_at'], name='module_4_em_user_id_created_idx'),
        ),
        migrations.AddIndex(
            model_name='emergencysos',
            index=models.Index(fields=['status'], name='module_4_em_status_idx'),
        ),
        migrations.AddIndex(
            model_name='locationupdate',
            index=models.Index(fields=['emergency_sos', '-created_at'], name='module_4_em_sos_id_created_idx'),
        ),
        migrations.AddIndex(
            model_name='emergencylog',
            index=models.Index(fields=['emergency_sos', '-created_at'], name='module_4_em_sos_id_creat_idx'),
        ),
        migrations.AddIndex(
            model_name='emergencylog',
            index=models.Index(fields=['action_type'], name='module_4_em_action_idx'),
        ),
    ]
