from django.core.validators import RegexValidator
from rest_framework.exceptions import ValidationError
from django.core.validators import validate_ipv4_address,validate_ipv6_address
import re

class NamespaceNameValidator(RegexValidator):
    regex = '^[-0-9a-z.]+$'
    message = "Invalid Namespace name"

zn = '(?!-)[a-z0-9-]{1,64}(?<!-)'
multiplezn = '(' + zn + '\.){1,126}'
tld = '[a-z]{2,64}'
zonename = f'{zn}|{multiplezn}{tld}'
class ZoneNameValidator(RegexValidator):
    regex = f'^{zonename}$'
    message = "Invalid Zone name"

attrchecks = {
    "A":     ["a"],
    "AAAA":  ["aaaa"],
    "NS":    ["ns"],
    "CNAME": ["cname"],
    "MX":    ["prio", "mx"],
    "PTR":   ["ptr"],
    "SRV":   ["srv_priority", "srv_weight", "srv_port", "srv_target"],
    "TXT":   ["txt"],
    "DNAME": ["dname"],
    "CAA":   ["caa_flag", "caa_tag", "caa_value"],
}

def ValidateType(attrs):
    t = attrs["type"]
    missing = []
    for field in attrchecks[t]:
        if attrs.get(field) is None:
            missing.append(field)
    if missing:
        raise ValidationError(detail=f"missing fields '{','.join(missing)}' for type '{t}'")

def ValidateRelativeName(name):
    if len(name) > 64:
        raise ValidationError(detail=f"Relative name '{name}' is too long (length must be <= 64)")
    if name[0] in ('-','.') or name[-1] in ('-','.'):
        raise ValidationError(detail=f"Relative name '{name}' must not start or end with dash or dot")
    if re.match(r'\.\.', name):
        raise ValidationError(detail=f"Relative name '{name}' can not contain two successive dots")
    c = '[.a-zA-Z0-9-]+'
    if not re.match(f"^(@|\*|\*\.{c}|{c}|_{c})$", name):
        raise ValidationError(detail=f"Relative name must be '@', '*' or an alpha-numeric string")
    
def ValidateAbsoluteName(name):
    if len(name) > 255:
        raise ValidationError(detail=f"Absolute name '{name}' is too long (length must be <= 255)")
    for component in name.split('.')[0:-1]:
        ValidateRelativeName(component)

def ValidateRrName(name):
    # if absolute name (ending with dot)
    if name[-1] == '.':
        ValidateAbsoluteName(name)
    else: # relative name
        ValidateRelativeName(name)

# Name has been *already been validated* by RrNameValidate
def ValidateHostname(name):
    for component in name.split('.')[0:-1]:
        if "_" in name:
            raise ValidationError(detail=f"hostname '{name}' can't contain underscore")
