#!/usr/bin/env python

import os, sys
proj_path = "/home/test/dnsapp"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dnsapp.settings")
sys.path.append(proj_path)
os.chdir(proj_path)
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

import dns.zone

from dns.exception import DNSException
from core.models import Namespace, Zone, Rr

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
print("base dir path"+BASE_DIR)

domain = "unistra.fr"
zone_file = "testdata/"+domain

# Utility functions
def gen_SOA(name, origin, ttl, data, z):
    mname = str(data.mname.derelativize(origin))
    rname = str(data.rname.derelativize(origin))
    minimum = data.minimum
    serial = data.serial
    refresh = data.refresh
    retry = data.retry
    expire = data.expire
    minimum = data.minimum
    print(str(name)+" "+mname+" "+rname+" ( "+str(serial)+ " "+ str(refresh) + " "+ str(retry) + " "+ str(expire) + " "+ str(minimum) + " )")
    rr = Rr.objects.create(name=name, zone=z, ttl=ttl, type='SOA', soa_master = mname, soa_mail = rname, soa_serial = serial, soa_refresh = refresh, soa_retry = retry, soa_expire = expire, soa_minttl = minimum)
    rr.save()

def gen_CNAME(name, origin, ttl, data, z):
    cname = str(data.target.derelativize(origin))
    print(str(name)+" "+cname)
    rr = Rr.objects.create(name=name, zone=z, ttl=ttl, type='CNAME', cname=cname)
    rr.save()
    
def gen_MX(name, origin, ttl, data, z):
    preference = data.preference
    exchange = str(data.exchange.derelativize(origin))
    print(name+" "+str(preference)+" "+exchange)
    rr = Rr.objects.create(name=name, zone=z, ttl=ttl, type='MX', mx=exchange, prio=preference)
    rr.save()

def gen_PTR(name, origin, ttl, data, z):
    target = str(data.target)
    print(name+" "+target)
    rr = Rr.objects.create(name=name, zone=z, ttl=ttl, type='PTR', ptr=target)
    rr.save()

def gen_SRV(name, origin, ttl, data, z):
    priority = data.priority
    weight = data.weight
    port = data.port
    target = str(data.target.derelativize(origin))
    print(name + " " + str(priority)+ " " + str(weight)+ " " + str(port)+ " " + target)
    rr = Rr.objects.create(name=name, zone=z, ttl=ttl, type='SRV', srv_priority = priority, srv_weight = weight, srv_port = port, srv_target = target)
    rr.save()

def gen_TXT(name, origin, ttl, data, z):
    joined = ''.join([str(s, encoding='ascii') for s in data.strings])
    strings = f'"{joined}"'
    print(name + strings)
    rr = Rr.objects.create(name=name, zone=z, ttl=ttl, type='TXT',txt=joined)
    rr.save()

def gen_NS(name, origin, ttl, data, z):
    ns = str(data.target.derelativize(origin))
    print(name+" "+ns)
    rr = Rr.objects.create(name=name, zone=z, ttl=ttl, type='NS',ns=ns)
    rr.save()

def gen_A(name, origin, ttl, data, z):
    a=str(data.address)
    print(name+" "+a)
    rr = Rr.objects.create(name=name, zone=z, ttl=ttl, type='A',a=a)
    rr.save()

def gen_AAAA(name, origin, ttl, data, z):
    aaaa=str(data.address)
    print(name+" "+aaaa)
    rr = Rr.objects.create(name=name, zone=z, ttl=ttl, type='AAAA',aaaa=aaaa)
    rr.save()

l = (
    (dns.rdatatype.SOA,gen_SOA),
    (dns.rdatatype.NS,gen_NS),
    (dns.rdatatype.CNAME,gen_CNAME),
    (dns.rdatatype.MX,gen_MX),
    (dns.rdatatype.PTR,gen_PTR),
    (dns.rdatatype.SRV,gen_SRV),
    (dns.rdatatype.TXT,gen_TXT),
    (dns.rdatatype.AAAA,gen_AAAA),
    (dns.rdatatype.A,gen_A),
    )

# Create or get namespace and zone
try:
    n = Namespace.objects.get(name='ns')
except:
    n = Namespace.objects.create(name='ns')
try:
    z = Zone.objects.get(name=domain)
except:
    z = Zone.objects.create(name=domain, namespace=n)
print(z)
exit
# Load zone file
try:
    izone = dns.zone.from_file(zone_file, domain)
    origin = izone.origin
except DNSException     as e:
    print(e.__class__, e)
for t,f in l:
    for name,ttl,data in izone.iterate_rdatas(t):
        name = str(name)
        print("Creating '"+name+"'")
        f(name,origin, ttl, data, z)
