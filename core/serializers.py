from rest_framework import serializers
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
        fields = ['id', 'name', 'type', 'ttl', 'zone', 'soa_master', 'soa_mail', 'soa_serial', 'soa_refresh', 'soa_retry', 'soa_expire', 'soa_minttl', 'a', 'aaaa', 'cname', 'ns', 'prio', 'mx', 'ptr', 'txt', 'srv_priority', 'srv_weight', 'srv_port', 'srv_target', 'caa_flag', 'caa_tag', 'caa_value', 'dname', 'dnskey_flag', 'dnskey_proto', 'dnskey_algorithm', 'dnskey_pubkey', 'rrsig_type', 'rrsig_algorithm', 'rrsig_labels', 'rrsig_origttl', 'rrsig_keytag', 'rrsig_signer', 'rrsig_signature', 'nsec_nextdomain', 'nsec_typebitmaps', 'ds_keytag', 'ds_algorithm', 'ds_digesttype', 'ds_digest', 'nsec3_hashalgorithm', 'nsec3_flags', 'nsec3_iteration', 'nsec3_saltlength', 'nsec3_salt', 'nsec3_hashlength', 'nsec3_nexthashedownername', 'nsec3_typebitmaps']
