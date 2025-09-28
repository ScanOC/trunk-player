# Generated manually for fine-grained authorization system

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('radio', '0062_siteoption_copyright_notice'),
    ]

    operations = [
        migrations.CreateModel(
            name='SystemRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('admin', 'System Administrator'), ('user', 'Regular User')], default='user', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_system_roles', to=settings.AUTH_USER_MODEL)),
                ('system', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_roles', to='radio.system')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='system_roles', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['system__name', 'user__username'],
            },
        ),
        migrations.CreateModel(
            name='UserTalkgroupMenu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('show_in_menu', models.BooleanField(default=True)),
                ('order', models.IntegerField(default=0, help_text='Display order in menu')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('talkgroup', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='menu_users', to='radio.talkgroupwithsystem')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='menu_talkgroups', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['user__username', 'order', 'talkgroup__alpha_tag'],
            },
        ),
        migrations.CreateModel(
            name='UserTalkgroupAccess',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('granted_at', models.DateTimeField(auto_now_add=True)),
                ('granted_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='granted_talkgroup_access', to=settings.AUTH_USER_MODEL)),
                ('system_role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='talkgroup_access', to='radio.systemrole')),
                ('talkgroup', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_permissions', to='radio.talkgroupwithsystem')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='talkgroup_permissions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['user__username', 'talkgroup__alpha_tag'],
            },
        ),
        migrations.CreateModel(
            name='UserScanList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_default', models.BooleanField(default=False, help_text='Default scan list for this user')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('talkgroups', models.ManyToManyField(blank=True, related_name='user_scan_lists', to='radio.talkgroupwithsystem')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='custom_scan_lists', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['user__username', 'name'],
            },
        ),
        migrations.CreateModel(
            name='SystemPermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('permission', models.CharField(choices=[('edit_talkgroups', 'Edit Talkgroup Names'), ('edit_units', 'Edit Unit Names'), ('manage_users', 'Manage System Users'), ('view_all_transmissions', 'View All Transmissions'), ('download_audio', 'Download Audio Files')], max_length=30)),
                ('granted_at', models.DateTimeField(auto_now_add=True)),
                ('granted_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='granted_permissions', to=settings.AUTH_USER_MODEL)),
                ('system_role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='permissions', to='radio.systemrole')),
            ],
            options={
                'ordering': ['system_role', 'permission'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='usertalkgroupmenu',
            unique_together={('user', 'talkgroup')},
        ),
        migrations.AlterUniqueTogether(
            name='usertalkgroupaccess',
            unique_together={('user', 'talkgroup')},
        ),
        migrations.AlterUniqueTogether(
            name='userscanlist',
            unique_together={('user', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='systemrole',
            unique_together={('user', 'system')},
        ),
        migrations.AlterUniqueTogether(
            name='systempermission',
            unique_together={('system_role', 'permission')},
        ),
    ]