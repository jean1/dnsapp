#!/bin/bash

python manage.py shell -c "
# Create User
from django.contrib.auth.models import User

try: u = User.objects.get(username='toto')
except:
  u = User.objects.create(username='toto')
  u.set_password('toto') ; u.save()
# Create Group
from django.contrib.auth.models import Group
try: g = Group.objects.get(name='gr1')
except: g = Group.objects.create(name='gr1')
# Add user to group
try: g.user_set.add(u) 
except: pass

# Create Namespace
from core.models import Namespace, Zone, Rr
try: n = Namespace.objects.get(name='ns')
except: n = Namespace.objects.create(name='ns')
try: n2 = Namespace.objects.get(name='ns2')
except: n2 = Namespace.objects.create(name='ns2')
# Create Zone
try: z = Zone.objects.get(name='example.com')
except: z = Zone.objects.create(name='example.com', namespace=n)
# Create rr1
try: rr1 = Rr.objects.get(name='rr1')
except: rr1 = Rr.objects.create(name='rr1', zone=z, type='A',a='1.2.3.4')
# Create rr2
try: rr2 = Rr.objects.get(name='rr2')
except: rr2 = Rr.objects.create(name='rr2', zone=z, type='A',a='1.2.3.5')
# Add permission
from guardian.shortcuts import assign_perm
try:
  assign_perm('access_namespace', g, n)
  assign_perm('access_zone', g, z)
  assign_perm('access_rr', g, rr1)
except: pass
"
