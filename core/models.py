import re
from django.db import models
from django.db.models import CheckConstraint, Q, F
from django.core.validators import MaxLengthValidator
from django.contrib.auth.models import (Group, AbstractUser, BaseUserManager)
from core.validators import (NamespaceNameValidator, ZoneNameValidator,
                             ValidateRrName)

nameformat = '^[-0-9a-z.]+$'

RECORDTYPES = [
    ("SOA", "SOA"),
    ("NS", "NS"),
    ("A", "A"),
    ("AAAA", "AAAA"),
    ("CNAME", "CNAME"),
    ("MX", "MX"),
    ("PTR", "PTR"),
    ("SRV", "SRV"),
    ("TXT", "TXT"),
    ("DNAME", "DNAME"),
]

PERMACTION = [
    ("r", "Read-Only"),
    ("rw", "Read-Write"),    #
    ("rwc", "Read-Write and Create Records"),
    ("rc", "Read and Create Records"),
]


class User(AbstractUser):
    '''
    Inherited from django user; related name is set to '+' because backward relationship
    from group to user through default_pref is not needed
    '''
    default_pref = models.OneToOneField(Group, on_delete=models.PROTECT, related_name='+')
    objects = BaseUserManager()


class Namespace(models.Model):
    # Le nom est obligatoire : ne peut pas être vide, doit être unique
    name = models.TextField(validators=[NamespaceNameValidator()],
                            unique=True, blank=False)

    class Meta:
        default_permissions = ()

    def __str__(self):
        return self.name


class Zone(models.Model):
    name = models.TextField(validators=[NamespaceNameValidator()], blank=False)
    namespace = models.ForeignKey(Namespace, on_delete=models.PROTECT,
                                  blank=False)
    nsmaster = models.TextField(validators=[ValidateRrName],  blank=False)
    mail = models.TextField(validators=[ValidateRrName], blank=False)
    serial = models.PositiveIntegerField(default=1, blank=False)
    refresh = models.PositiveIntegerField(default=1200, blank=False)
    retry = models.PositiveIntegerField(default=180, blank=False)
    expire = models.PositiveIntegerField(default=1209600, blank=False)
    minttl = models.PositiveIntegerField(default=3600, blank=False)

    def __str__(self):
        return self.name

    class Meta:
        default_permissions = ()
        unique_together = ('name', 'namespace', )

#    def save():
#        self.serial++
#        self.super.save()

class Rr(models.Model):
    name = models.TextField(validators=[ValidateRrName], blank=False)
    # Le nom est obligatoire : ne peut pas être vide
    type = models.TextField(choices=RECORDTYPES, blank=False)
    ttl = models.PositiveIntegerField(default=3600, blank=False)
    zone = models.ForeignKey(Zone, on_delete=models.PROTECT, blank=False)

    # A
    a = models.GenericIPAddressField(protocol="IPv4", blank=True, null=True)
    # AAAA
    aaaa = models.GenericIPAddressField(protocol="IPv6", blank=True, null=True)
    # CNAME
    cname = models.TextField(validators=[ValidateRrName], blank=True,
                             null=True)
    # NS
    ns = models.TextField(validators=[ValidateRrName], blank=True, null=True)
    # MX
    prio = models.PositiveIntegerField(blank=True, null=True)
    mx = models.TextField(validators=[ValidateRrName], blank=True, null=True)
    # PTR
    ptr = models.TextField(validators=[ValidateRrName], blank=True, null=True)
    # TXT;
    # FIXME: valider la longueur maximale
    txt = models.TextField(validators=[MaxLengthValidator(65535)], blank=True,
                           null=True)
    # SRV
    srv_priority = models.PositiveIntegerField(blank=True, null=True)
    srv_weight = models.PositiveIntegerField(blank=True, null=True)
    srv_port = models.PositiveIntegerField(blank=True, null=True)
    srv_target = models.TextField(validators=[ValidateRrName], blank=True,
                                  null=True)
    # CAA ;
    # FIXME: add CHOICE to caa_tag (issue, issuewild, iodef, contactemail)
    caa_flag = models.PositiveIntegerField(blank=True, null=True)
    caa_tag = models.TextField(validators=[MaxLengthValidator(253)],
                               blank=True, null=True)
    caa_value = models.TextField(validators=[MaxLengthValidator(253)],
                                 blank=True, null=True)
    # DNAME
    dname = models.TextField(validators=[ZoneNameValidator()], blank=True,
                             null=True)

#    def save():
#        self.super.save()
#        self.zone.updateserial()

    def __str__(self):
        return self.name

    class Meta:
        default_permissions = ()

# Rule to add a record to a zone
# * namepat is the regexp checked for allowed Rr names
#   example : '^[-a-zA-Z0-9_.]+$' rules out names such as '*' or '@'
# * typepat is the regexp checked for allowed Rr types
#   example : '^(A|AAAA|CNAME|MX|SRV|TXT)$'
#             rules out types such as 'NS' or 'SOA'


class Zonerule(models.Model):
    zone = models.OneToOneField(Zone, on_delete=models.CASCADE,
                                primary_key=True)
    namepat = models.TextField(validators=[MaxLengthValidator(1024)],
                               blank=True, null=True)
    typepat = models.TextField(validators=[MaxLengthValidator(1024)],
                               blank=True, null=True)

    def __str__(self):
        return f"namepat='{self.namepat}', typepat='{self.typepat}'"

    def is_checked(self, name, type):
        # check name
        m1 = re.match(self.namepat, name)
        # check type
        m2 = re.match(self.typepat, type)
        return ((m1 is not None) and (m2 is not None))

# Generic permission model


class Perm(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, blank=False)
    action = models.TextField(choices=PERMACTION, blank=False)

    class Meta:
        abstract = True
        unique_together = ('obj', 'group')

# Permission table for a Namespace
# Semantic:
# + r: group can access this namespace (ie. namespace is visible when
#      listing all namespaces)
# + c: group can create new zone in this namespace
# NB: namespaces can only by created and deleted by admin; non-admin
#     user can not create/delete/modify namespace
#


class PermNamespace(Perm):
    obj = models.ForeignKey(Namespace, on_delete=models.CASCADE, blank=False)

    class Meta:
        unique_together = ('obj', 'group')
    def __str__(self):
        return f"perm namespace='{self.obj.name}', group='{self.group.name}' action='self.group.action'"

# Permission table for a Zone
# Semantic:
# + r: can list all Rr in this zone
# + c: can create new Rr in this zone
# + w: can modify SOA parameters for this zone (nsmaster, refresh ...)


class PermZone(Perm):
    obj = models.ForeignKey(Zone, on_delete=models.CASCADE, blank=False)

    class Meta:
        unique_together = ('obj', 'group')
    def __str__(self):
        return f"perm zone='{self.obj.name}', group='{self.group.name}' action='self.group.action'"

# Permission table for individual Resource Record
# Semantic:
# + r: can get this Rr
# + w: can delete and update this Rr value (can not modify its type nor
#      its name)
#        example: change "www.example.com A 192.0.9.1"
#                     to "www.example.com A 192.0.9.222"


class PermRr(Perm):
    obj = models.ForeignKey(Rr, on_delete=models.CASCADE, blank=False)

    class Meta:
        unique_together = ('obj', 'group')
    def __str__(self):
        return f"perm rr='{self.obj.name}', group='{self.group.name}' action='self.group.action'"
