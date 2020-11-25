from rest_framework import serializers
from core.validators import ValidateAbsoluteName, ValidateType, ValidateHostname
from core.models import Namespace, Zone, Rr

class NamespaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Namespace
        fields = ['id', 'name']

class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = ['id', 'name', 'namespace', 'nsmaster', 'mail', 'serial', 'refresh', 'retry', 'expire', 'minttl']

class RrSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rr
        fields = ['id', 'name', 'type', 'ttl', 'zone', 'a', 'aaaa', 'cname', 'ns', 'prio', 'mx', 'ptr', 'txt', 'srv_priority', 'srv_weight', 'srv_port', 'srv_target', 'caa_flag', 'caa_tag', 'caa_value', 'dname' ]

    def validate(self, attrs):
        ValidateType(attrs)

        zone = attrs["zone"].name
        # Force name to lowercase
        name = attrs["name"] = attrs["name"].lower()

        # For hosts, specific restrictions apply to name format
        if attrs["type"] == "A" or attrs["type"] == "AAAA":
            ValidateHostname(name)

        # Check if absolute name ends with zone name
        if name.endswith("."):
            if not name.endswith(f"{zone}."):
                raise ValidationException(detail=f"Absolute name '{name}' does not end with zone name")

        # Name and zone name should have been validated up to this point
        # Just check total length 
        fqdn = f"{name}.{attrs['zone'].name}"
        if len(fqdn) > 255:
            raise ValidationException(detail=f"Full name '{fqdn}' is too long (length must be <= 255)")

        return attrs
