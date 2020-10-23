from django.core.validators import RegexValidator
from rest_framework.exceptions import ValidationError
from django.core.validators import validate_ipv4_address,validate_ipv6_address

class NamespaceNameValidator(RegexValidator):
    regex = '^[-0-9a-z.]+$'
    message = "Invalid Namespace name"

zn = '(?!-)[A-Za-z0-9-]{1,63}(?<!-)'
multiplezn = '(' + zn + '\.){1,126}'
tld = '[A-Za-z]{2,63}'
zonename = f'{zn}|{multiplezn}{tld}'
class ZoneNameValidator(RegexValidator):
    regex = f'^{zonename}$'
    message = "Invalid Zone name"

nstart = '(\*\.|_)?'                 # can start with "*." or "_"
nmiddle = '(?!-)[A-Za-z0-9.-]{1,63}' # name can contain alphanum. char, dot or dash
nend = '(?<![-.])'                   # does not end with dash or dot
rrname = f'(\*|@|{nstart}{nmiddle}{nend})'
class RrNameValidator(RegexValidator):
    regex = f"^{rrname}$"
    message = "Invalid Rr name"
   
class AbsOrRelNameValidator(RegexValidator):
    regex = f'^{rrname}\.?$'    # FIXME: accept longer names
    message = "Invalid absolute or relative Name"

attrchecks = {
    "A":     ["a"],
    "AAAA":  ["aaaa"],
    "SOA":   ["soa_master", "soa_mail", "soa_serial", "soa_refresh", "soa_retry", "soa_expire", "soa_minttl"],
    "NS":    ["ns"],
    "CNAME": ["cname"],
    "MX":    ["prio", "mx"],
    "PTR":   ["ptr"],
    "SRV":   ["srv_priority", "srv_weight", "srv_port", "srv_target"],
    "TXT":   ["txt"],
    "DNAME": ["dname"],
    "CAA":   ["caa_flag", "caa_tag", "caa_value"],
}

def TypeValidator(attrs):
    # raise ValidationError
    t = attrs["type"]
    missing = []
    for field in attrchecks[t]:
        if attrs.get(field) is None:
            missing.append(field)
    if missing:
        raise ValidationError(detail=f"missing fields '{','.join(missing)}' for type '{t}'")

