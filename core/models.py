import re
from django.db import models
from django.db.models import CheckConstraint, Q, F
from django.core.validators import MaxLengthValidator
from core.validators import NamespaceNameValidator, ZoneNameValidator, ValidateRrName

nameformat='^[-0-9a-z.]+$'
rrnameformat='^([-0-9a-zA-Z._*]+|@)$'

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
]

class Namespace(models.Model):
    # Le nom est obligatoire : ne peut pas être vide, doit être unique
    name = models.TextField(validators=[NamespaceNameValidator()],
                             unique=True, blank=False)
    class Meta:
        default_permissions = ()
        permissions = ( ('access_namespace', 'Access namespace'),)
        constraints = [ 
                        CheckConstraint( check=Q(name__regex=nameformat),
                                         name='namespace_name_must_contain_only_letters_numbers_or_dots'
                        ),
                      ]

    def __str__(self):
        return self.name

class Zone(models.Model):
    name = models.TextField(validators=[ZoneNameValidator()], blank=False)
    namespace = models.ForeignKey(Namespace, on_delete=models.PROTECT, blank=False)
    def __str__(self):
        return self.name
    class Meta:
        default_permissions = ()
        permissions = ( ('access_zone', 'Access zone'),)
        unique_together = ('name', 'namespace',)
        constraints = [ 
                        CheckConstraint( check=Q(name__regex=nameformat),
                                         name='zone_name_must_contain_only_letters_numbers_or_dots'
                        ),
                      ]

class Rr(models.Model):
    name = models.TextField(validators=[ValidateRrName], blank=False)
    # Le nom est obligatoire : ne peut pas être vide
    type = models.TextField(choices=RECORDTYPES, blank=False)
    ttl = models.PositiveIntegerField(default=3600, blank=False)
    zone = models.ForeignKey(Zone, on_delete=models.PROTECT, blank=False)
    # SOA
    soa_master = models.TextField(validators=[ValidateRrName], blank=True, null=True)
    soa_mail = models.TextField(validators=[ValidateRrName], blank=True, null=True)
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
    cname = models.TextField(validators=[ValidateRrName], blank=True, null=True)
    # NS
    ns = models.TextField(validators=[ValidateRrName], blank=True, null=True)
    # MX
    prio = models.PositiveIntegerField(blank=True, null=True)
    mx = models.TextField(validators=[ValidateRrName], blank=True, null=True)
    # PTR
    ptr = models.TextField(validators=[ValidateRrName], blank=True, null=True)
    # TXT; FIXME: valider la longueur maximale 
    txt = models.TextField(validators=[MaxLengthValidator(65535)], blank=True, null=True)
    # SRV
    srv_priority = models.PositiveIntegerField(blank=True, null=True)
    srv_weight = models.PositiveIntegerField(blank=True, null=True)
    srv_port = models.PositiveIntegerField(blank=True, null=True)
    srv_target = models.TextField(validators=[ValidateRrName], blank=True, null=True)
    # CAA ; FIXME: ajouter CHOICE pour caa_tag (issue, issuewild, iodef, contactemail)
    caa_flag = models.PositiveIntegerField(blank=True, null=True)
    caa_tag = models.TextField(validators=[MaxLengthValidator(253)], blank=True, null=True)
    caa_value = models.TextField(validators=[MaxLengthValidator(253)], blank=True, null=True)
    # DNAME
    dname = models.TextField(validators=[ZoneNameValidator()], blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        default_permissions = ()
        permissions = ( ('access_rr', 'Access Rr'),)
        constraints = [ CheckConstraint( check=Q(name__regex=rrnameformat),
                                         name='record_name_must_contain_only_letters_numbers_star_or_dots'
                        ),
                      ]

# Rule to add a record to a zone
# namepat is the regexp checked for allowed Rr names 
#   example : '^[-a-zA-Z0-9_.]+$' rules out names such as '*' or '@'
# typepat is the regexp checked for allowed Rr types
#   example : '^(A|AAAA|CNAME|MX|SRV|TXT)$' rules out types such as 'NS' or 'SOA'

class Zonerule(models.Model):
    zone = models.OneToOneField(Zone, on_delete=models.CASCADE, primary_key=True)
    namepat = models.TextField(validators=[MaxLengthValidator(1024)], blank=True, null=True)
    typepat = models.TextField(validators=[MaxLengthValidator(1024)], blank=True, null=True)

    def __str__(self):
        return f"namepat='{self.namepat}',typepat='{self.typepat}'"

    def is_checked(self, name, type):
        # check name
        m1 = (re.match(self.namepat, name) != None)
        # check type
        m2 = (re.match(self.typepat, type) != None)
        return (m1 and m2)
