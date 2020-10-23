from rest_framework import serializers
from core.validators import NamespaceNameValidator, ZoneNameValidator, RrNameValidator, TypeValidator
from core.models import Namespace, Zone, Rr

class NamespaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Namespace
        fields = ['id', 'name']

class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = ['id', 'name', 'namespace']

# FIXME: a revoir
class RrSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rr
        fields = ['id', 'name', 'type', 'ttl', 'zone', 'soa_master', 'soa_mail', 'soa_serial', 'soa_refresh', 'soa_retry', 'soa_expire', 'soa_minttl', 'a', 'aaaa', 'cname', 'ns', 'prio', 'mx', 'ptr', 'txt', 'srv_priority', 'srv_weight', 'srv_port', 'srv_target', 'caa_flag', 'caa_tag', 'caa_value', 'dname' ]

    def validate(self, attrs):
        TypeValidator(attrs)
        return attrs
        
