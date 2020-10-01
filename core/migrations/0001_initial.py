# Generated by Django 3.0.6 on 2020-09-18 15:34

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Namespace',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(default=None, unique=True, validators=[django.core.validators.MinLengthValidator(1), django.core.validators.MaxLengthValidator(63)])),
            ],
        ),
        migrations.CreateModel(
            name='Zone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(default=None, validators=[django.core.validators.MinLengthValidator(1), django.core.validators.MaxLengthValidator(63)])),
                ('namespace', models.ForeignKey(default=None, on_delete=django.db.models.deletion.PROTECT, to='core.Namespace')),
            ],
        ),
        migrations.CreateModel(
            name='Rr',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(default=None, validators=[django.core.validators.MinLengthValidator(1), django.core.validators.MaxLengthValidator(63)])),
                ('type', models.TextField(choices=[('SOA', 'SOA'), ('NS', 'NS'), ('A', 'A'), ('AAAA', 'AAAA'), ('CNAME', 'CNAME'), ('MX', 'MX'), ('PTR', 'PTR'), ('SRV', 'SRV'), ('TXT', 'TXT'), ('DNAME', 'DNAME'), ('DNSKEY', 'DNSKEY'), ('RRSIG', 'RRSIG'), ('DS', 'DS'), ('NSEC', 'NSEC')], default=None, validators=[django.core.validators.MinLengthValidator(1), django.core.validators.MaxLengthValidator(10)])),
                ('ttl', models.PositiveIntegerField(default=3600)),
                ('soa_master', models.TextField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(253)])),
                ('soa_mail', models.TextField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(253)])),
                ('soa_serial', models.PositiveIntegerField(blank=True, null=True)),
                ('soa_refresh', models.PositiveIntegerField(blank=True, null=True)),
                ('soa_retry', models.PositiveIntegerField(blank=True, null=True)),
                ('soa_expire', models.PositiveIntegerField(blank=True, null=True)),
                ('soa_minttl', models.PositiveIntegerField(blank=True, null=True)),
                ('a', models.GenericIPAddressField(blank=True, null=True, protocol='IPv4')),
                ('aaaa', models.GenericIPAddressField(blank=True, null=True, protocol='IPv6')),
                ('cname', models.TextField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(253)])),
                ('ns', models.TextField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(253)])),
                ('prio', models.PositiveIntegerField(blank=True, null=True)),
                ('mx', models.TextField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(253)])),
                ('ptr', models.TextField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(253)])),
                ('txt', models.TextField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(65535)])),
                ('srv_priority', models.PositiveIntegerField(blank=True, null=True)),
                ('srv_weight', models.PositiveIntegerField(blank=True, null=True)),
                ('srv_port', models.PositiveIntegerField(blank=True, null=True)),
                ('srv_target', models.TextField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(253)])),
                ('caa_flag', models.PositiveIntegerField(blank=True, null=True)),
                ('caa_tag', models.TextField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(253)])),
                ('caa_value', models.TextField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(253)])),
                ('dname', models.TextField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(253)])),
                ('dnskey_flag', models.PositiveIntegerField(blank=True, null=True)),
                ('dnskey_proto', models.PositiveIntegerField(blank=True, null=True)),
                ('dnskey_algorithm', models.PositiveIntegerField(blank=True, null=True)),
                ('dnskey_pubkey', models.TextField(blank=True, null=True)),
                ('rrsig_type', models.TextField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(10)])),
                ('rrsig_algorithm', models.PositiveIntegerField(blank=True, null=True)),
                ('rrsig_labels', models.PositiveIntegerField(blank=True, null=True)),
                ('rrsig_origttl', models.PositiveIntegerField(blank=True, null=True)),
                ('rrsig_keytag', models.PositiveIntegerField(blank=True, null=True)),
                ('rrsig_signer', models.TextField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(255)])),
                ('rrsig_signature', models.TextField(blank=True, null=True)),
                ('nsec_nextdomain', models.TextField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(255)])),
                ('nsec_typebitmaps', models.TextField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(255)])),
                ('ds_keytag', models.PositiveIntegerField(blank=True, null=True)),
                ('ds_algorithm', models.PositiveIntegerField(blank=True, null=True)),
                ('ds_digesttype', models.PositiveIntegerField(blank=True, null=True)),
                ('ds_digest', models.TextField(blank=True, null=True)),
                ('nsec3_hashalgorithm', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(255)])),
                ('nsec3_flags', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(255)])),
                ('nsec3_iteration', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(65535)])),
                ('nsec3_saltlength', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(255)])),
                ('nsec3_salt', models.TextField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(255)])),
                ('nsec3_hashlength', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(255)])),
                ('nsec3_nexthashedownername', models.TextField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(255)])),
                ('nsec3_typebitmaps', models.TextField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(255)])),
                ('zone', models.ForeignKey(default=None, on_delete=django.db.models.deletion.PROTECT, to='core.Zone')),
            ],
        ),
        migrations.AddConstraint(
            model_name='namespace',
            constraint=models.CheckConstraint(check=models.Q(name__regex='^[-0-9a-z.]+$'), name='namespace_name_must_contain_only_letters_numbers_or_dots'),
        ),
        migrations.AddConstraint(
            model_name='zone',
            constraint=models.CheckConstraint(check=models.Q(name__regex='^[-0-9a-z.]+$'), name='zone_name_must_contain_only_letters_numbers_or_dots'),
        ),
        migrations.AlterUniqueTogether(
            name='zone',
            unique_together={('name', 'namespace')},
        ),
        migrations.AddConstraint(
            model_name='rr',
            constraint=models.CheckConstraint(check=models.Q(name__regex='^[-0-9a-z.]+$'), name='record_name_must_contain_only_letters_numbers_or_dots'),
        ),
    ]