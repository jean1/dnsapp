import re
from django.db import models
from django.db.models import CheckConstraint, Q, F
from django.core.validators import MaxValueValidator, MinValueValidator, MaxLengthValidator, MinLengthValidator

nameformat='^[-0-9a-z.]+$'

RECORDTYPES = [
    ("SOA" ,"SOA" ),
    ("NS" ,"NS" ),
    ("A" ,"A" ),
    ("AAAA" ,"AAAA" ),
    ("CNAME" ,"CNAME" ),
    ("MX" ,"MX" ),
    ("PTR" ,"PTR" ),
    ("SRV" ,"SRV" ),
    ("TXT" ,"TXT" ),
    ("DNAME" ,"DNAME" ),
    ("DNSKEY" ,"DNSKEY" ),
    ("RRSIG" ,"RRSIG" ),
    ("DS" ,"DS" ),
    ("NSEC" ,"NSEC" ),
]

class Namespace(models.Model):
    # Le nom est obligatoire : ne peut pas être vide, doit être unique
    name = models.TextField(validators=[MinLengthValidator(1),MaxLengthValidator(63)],
                             unique=True, default=None, blank=False)
    class Meta:
        constraints = [ 
                        CheckConstraint( check=Q(name__regex=nameformat),
                                         name='namespace_name_must_contain_only_letters_numbers_or_dots'
                        ),
                      ]

    def __str__(self):
        return self.name

class Zone(models.Model):
    name = models.TextField(validators=[MinLengthValidator(1),MaxLengthValidator(63)],
                            default=None, blank=False)
    namespace = models.ForeignKey(Namespace, on_delete=models.PROTECT, default=None, blank=False)
    class Meta:
      unique_together = ('name', 'namespace',)
      constraints = [ 
                        CheckConstraint( check=Q(name__regex=nameformat),
                                         name='zone_name_must_contain_only_letters_numbers_or_dots'
                        ),
                      ]
    def __str__(self):
        return self.name

class Rr(models.Model):
    # Le nom est obligatoire : ne peut pas être vide
    name = models.TextField(validators=[MinLengthValidator(1),MaxLengthValidator(63)],
                            default=None, blank=False)
    type = models.TextField(validators=[MinLengthValidator(1),MaxLengthValidator(10)],
                            choices=RECORDTYPES,
                            default=None, blank=False)
    ttl = models.PositiveIntegerField(default=3600, blank=False)
    zone = models.ForeignKey(Zone, on_delete=models.PROTECT, default=None, blank=False)
    # SOA
    soa_master = models.TextField(validators=[MaxLengthValidator(253)], blank=True, null=True)
    soa_mail = models.TextField(validators=[MaxLengthValidator(253)], blank=True, null=True)
    soa_serial = models.PositiveIntegerField(blank=True, null=True)
    soa_refresh = models.PositiveIntegerField(blank=True, null=True)
    soa_retry = models.PositiveIntegerField(blank=True, null=True)
    soa_expire = models.PositiveIntegerField(blank=True, null=True)
    soa_minttl = models.PositiveIntegerField(blank=True, null=True)
    # A
    a = models.GenericIPAddressField(protocol="IPv4", blank=True, null=True)
    # AAAA
    aaaa = models.GenericIPAddressField(protocol="IPv6", blank=True, null=True)
    # CNAME
    cname = models.TextField(validators=[MaxLengthValidator(253)], blank=True, null=True)
    # NS
    ns = models.TextField(validators=[MaxLengthValidator(253)], blank=True, null=True)
    # MX
    prio = models.PositiveIntegerField(blank=True, null=True)
    mx = models.TextField(validators=[MaxLengthValidator(253)], blank=True, null=True)
    # PTR
    ptr = models.TextField(validators=[MaxLengthValidator(253)], blank=True, null=True)
    # TXT; FIXME: valider la longueur maximale 
    txt = models.TextField(validators=[MaxLengthValidator(65535)], blank=True, null=True)
    # SRV
    srv_priority = models.PositiveIntegerField(blank=True, null=True)
    srv_weight = models.PositiveIntegerField(blank=True, null=True)
    srv_port = models.PositiveIntegerField(blank=True, null=True)
    srv_target = models.TextField(validators=[MaxLengthValidator(253)], blank=True, null=True)
    # CAA ; FIXME: ajouter CHOICE pour caa_tag (issue, issuewild, iodef, contactemail)
    caa_flag = models.PositiveIntegerField(blank=True, null=True)
    caa_tag = models.TextField(validators=[MaxLengthValidator(253)], blank=True, null=True)
    caa_value = models.TextField(validators=[MaxLengthValidator(253)], blank=True, null=True)
    # DNAME
    dname = models.TextField(validators=[MaxLengthValidator(253)], blank=True, null=True)
    # DNSKEY
    dnskey_flag = models.PositiveIntegerField(blank=True, null=True)
    dnskey_proto = models.PositiveIntegerField(blank=True, null=True)
    dnskey_algorithm = models.PositiveIntegerField(blank=True, null=True)
    dnskey_pubkey = models.TextField(blank=True, null=True) #FIXME: valider la longueur maximale 

    # RRSIG; FIXME: utiliser CHOICE RRtypes pour rrsig_type
    rrsig_type = models.TextField(validators=[MaxLengthValidator(10)], blank=True, null=True)
    rrsig_algorithm = models.PositiveIntegerField(blank=True, null=True)
    rrsig_labels = models.PositiveIntegerField(blank=True, null=True)
    rrsig_origttl = models.PositiveIntegerField(blank=True, null=True)
    rrsig_keytag = models.PositiveIntegerField(blank=True, null=True)
    rrsig_signer = models.TextField(validators=[MaxLengthValidator(255)], blank=True, null=True)
    rrsig_signature = models.TextField(blank=True, null=True) #FIXME: valider la longueur maximale 

    # NSEC; FIXME: valider format de typebits
    nsec_nextdomain = models.TextField(validators=[MaxLengthValidator(255)], blank=True, null=True)
    nsec_typebitmaps = models.TextField(validators=[MaxLengthValidator(255)], blank=True, null=True)

    # DS; FIXME: valider max_value pour les Integer
    ds_keytag = models.PositiveIntegerField(blank=True, null=True)
    ds_algorithm = models.PositiveIntegerField(blank=True, null=True)
    ds_digesttype = models.PositiveIntegerField(blank=True, null=True)
    ds_digest = models.TextField(blank=True, null=True) #FIXME: valider la longueur maximale 

    # NSEC3; FIXME: valider max values
    nsec3_hashalgorithm = models.PositiveIntegerField(blank=True, null=True, validators=[MaxValueValidator(255)])
    nsec3_flags = models.PositiveIntegerField(blank=True, null=True, validators=[MaxValueValidator(255)])
    nsec3_iteration = models.PositiveIntegerField(blank=True, null=True, validators=[MaxValueValidator(65535)])
    nsec3_saltlength = models.PositiveIntegerField(blank=True, null=True, validators=[MaxValueValidator(255)])
    nsec3_salt = models.TextField(validators=[MaxLengthValidator(255)], blank=True, null=True)
    nsec3_hashlength = models.PositiveIntegerField(blank=True, null=True, validators=[MaxValueValidator(255)])
    nsec3_nexthashedownername = models.TextField(validators=[MaxLengthValidator(255)], blank=True, null=True)
    nsec3_typebitmaps = models.TextField(validators=[MaxLengthValidator(255)], blank=True, null=True)

    class Meta:
        constraints = [ 
                        CheckConstraint( check=Q(name__regex=nameformat),
                                         name='record_name_must_contain_only_letters_numbers_or_dots'
                        ),
                      ]
    def __str__(self):
        return self.name
