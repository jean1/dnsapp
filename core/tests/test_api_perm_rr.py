from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase
from core.models import Namespace, Zone, Rr, Zonerule, PermRr, PermZone, User
from core.serializers import RrSerializer
from rest_framework.renderers import JSONRenderer

import sys
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

class APIPermRrTests(APITestCase):
    def setUp(self):
        # Create groups
        self.defgrp = Group.objects.create(name='defgrp') 
        self.defgrp.save()
        self.gr1 = Group.objects.create(name='gr1') 
        self.gr1.save()
        self.gr2 = Group.objects.create(name='gr2') 
        self.gr2.save()
        self.gr3 = Group.objects.create(name='gr3') 
        self.gr3.save()
        # Create user 'admin' and make it superuser
        self.admin = User.objects.create(username='admin', default_pref=self.defgrp)
        self.admin.set_password('admin')
        self.admin.is_superuser = True
        self.admin.save()
        # Create user 'titi'
        self.user = User.objects.create(username='titi', default_pref=self.gr1)
        self.user.set_password('titi')
        self.user.save()
        # Create user 'toto'
        self.usertoto = User.objects.create(username='toto', default_pref=self.gr3)
        self.usertoto.set_password('toto')
        self.usertoto.save()
        # Put user titi in groups gr1 & gr2
        self.gr1.user_set.add(self.user) 
        self.gr2.user_set.add(self.user) 
        # Put user toto in groups gr3
        self.gr3.user_set.add(self.usertoto) 

        self.n1 = Namespace.objects.create(name='default')
        self.n1.save()
        # create zones
        self.z0 = Zone.objects.create(name='example.com',namespace=self.n1, nsmaster='ns1.example.com', mail='hostmaster.example.com')
        self.z0.save()
        self.zp0 = PermZone(action='rc', group = self.gr1, obj = self.z0)
        self.zp0.save()
        self.z1 = Zone.objects.create(name='shared.example.com',namespace=self.n1, nsmaster='ns1.example.com', mail='hostmaster.example.com')
        self.z1.save()
        self.zp1 = PermZone(action='rc', group = self.gr1, obj = self.z1)
        self.zp1.save()

        # zone z2 created without creating permission
        self.z2 = Zone.objects.create(name='denied.example.com',namespace=self.n1, nsmaster='ns1.example.com', mail='hostmaster.example.com')
        self.z2.save()

        # Set zone rules for create in zone z1
        tpat1 = '^(A|AAAA|CNAME|MX)$'
        npat1='^[-a-zA-Z0-9_.]+$'
        r1 = Zonerule.objects.create(zone=self.z1,typepat=tpat1,namepat=npat1)
        r1.save()
        self.url = '/rr/'
           
        # Create RR and permissions
        # rr0 has read and write access for group gr1
        self.rr0 = Rr.objects.create(name='rr0',type='A',a='192.0.9.1',zone=self.z0)
        self.rr0.save()
        self.pr0 = PermRr.objects.create(action="rw",group=self.gr1,obj=self.rr0)
        self.pr0.save()
        # rr1 has read access for group gr2
        self.rr1 = Rr.objects.create(name='rr1',type='A',a='192.0.9.2',zone=self.z0)
        self.rr1.save()
        self.pr1 = PermRr.objects.create(action="r",group=self.gr2,obj=self.rr1)
        self.pr1.save()
        # rr2 has read access for group gr1
        self.rr2 = Rr.objects.create(name='rr2',type='A',a='192.0.9.2',zone=self.z0)
        self.rr2.save()
        self.pr2 = PermRr.objects.create(action="r",group=self.gr1,obj=self.rr2)
        self.pr2.save()

        # rr3 has same name as newrr but different type, set permission for user toto in gr3
        self.rr3 = Rr.objects.create(name='newrr',type='TXT',txt='foobar',zone=self.z0)
        self.rr3.save()
        self.prrr3 = PermRr.objects.create(action="r",group=self.gr3,obj=self.rr3)
        self.prrr3.save()


        # rr5 has same name and same type as newrr2 , and is *not* updatable by user titi/group gr1
        # (gr2 has permission, but user titi is not in group gr2)
        self.rr5 = Rr.objects.create(name='newrr2',type='A',a='192.0.9.111',zone=self.z0)
        self.rr5.save()
        self.pr5 = PermRr.objects.create(action="rw",group=self.gr2,obj=self.rr5)
        self.pr5.save()

    def test_000_api_get_access_rr(self):
        """ test if rr0 can be accessed with GET -> must be allowed
        """
        self.url = f'/rr/{self.rr0.id}/'
        self.client.login(username='titi', password='titi')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
            
    def test_001_api_get_rr_not_allowed(self):
        """ test access to rr1 for groups of user toto (gr1, gr2)
            "r" permission exist only for group gr3 to rr1
            and user toto is not in group gr3 
            -> must be denied
        """
        self.url = f'/rr/{self.rr1.id}/'
        self.client.login(username='toto', password='toto')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            
    def test_002_api_get_all_allowed_rr(self):
        """ test access to all allowed rr for a given user
            -> response must contain 2 rr
        """

        n002 = Namespace.objects.create(name='z002')
        n002.save()
        z002 = Zone.objects.create(name='z002.example.com',namespace=n002, nsmaster='ns1.example.com', mail='hostmaster.example.com')
        z002.save()

        group002 = Group.objects.create(name='gr002') 
        group002.save()
        user002 = User.objects.create(username='user002', default_pref=group002)
        user002.set_password('user002')
        user002.save()
        group002.user_set.add(user002) 
       
        # create 2 rr
        rr002_1 = Rr.objects.create(name='rr002-1',type='A',a='192.0.9.221',zone=z002)
        rr002_1.save()
        p = PermRr.objects.create(action="rw", group=group002, obj=rr002_1)
        p.save()
        rr002_2 = Rr.objects.create(name='rr002-2',type='A',a='192.0.9.222',zone=z002)
        rr002_2.save()
        p = PermRr.objects.create(action="rw", group=group002, obj=rr002_2)
        p.save()

        self.url = f'/rr/'
        self.client.login(username='user002', password='user002')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        number_of_rr = len(response.data)
        self.assertEqual(number_of_rr, 2)

    def test_003_api_delete_not_allowed(self):
        """ test delete a rr without permission
            -> must be denied
        """
        self.url = f'/rr/{self.rr1.id}/'
        self.client.login(username='titi', password='titi')
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_004_api_delete_rr_ok(self):
        """ test delete rr0 with "w" permission
            -> must be allowed
        """
        self.url = f'/rr/{self.rr0.id}/'
        self.client.login(username='titi', password='titi')
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_005_api_create_rr_in_zone_ok(self):
        """ create rr in zone z0 with permission "c" in zone
            -> must be allowed
        """
        self.client.login(username='titi', password='titi')
        self.url = f'/rr/'
        data = {'name': 'myrr', 'type': 'A', 'zone': self.z0.id, 'a': '192.0.9.11',}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_006_api_create_rr_in_zone_ok(self):
        """ create rr in zone z2 without permission CreateRrInZone
            -> must be denied
        """
        self.client.login(username='titi', password='titi')
        self.url = f'/rr/'
        data = {'name': 'otherrr', 'type': 'A', 'zone': self.z2.id, 'a': '192.0.9.12',}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_007_api_create_rr_name_exist_ok(self):
        """ create rr "newrr" with same name as existing RR rr3
            in same zone z0
            But this newrr has different type,A as rr3 is of type TXT
            -> must be allowed
        """
        self.client.login(username='titi', password='titi')
        self.url = f'/rr/'
        data = {'name': 'newrr', 'type': 'A', 'zone': self.z0.id, 'a': '192.0.9.12',}
        response = self.client.post(self.url, data)
        # DEBUG
        #print(response.content)
        #import ipdb; ipdb.set_trace()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_008_api_create_rr_name_type_exist_and_updatable_ok(self):
        """ create rr with same name and type as existing RR with update permission
            -> must be allowed
        """

        n008 = Namespace.objects.create(name='z008')
        n008.save()
        z008 = Zone.objects.create(name='z008.example.com',namespace=n008, nsmaster='ns1.example.com', mail='hostmaster.example.com')
        z008.save()

        group008 = Group.objects.create(name='gr008') 
        group008.save()
        user008 = User.objects.create(username='user008', default_pref=group008)
        user008.set_password('user008')
        user008.save()
        group008.user_set.add(user008) 

        # add rr create permission for this zone for this group
        zp008 = PermZone(action='rc', group = group008, obj = z008)
        zp008.save()
       
        # rr008 has same name and same type as the rr we will create is this test 
        # and is updatable by user008 in group008
        rr008 = Rr.objects.create(name='rr008',type='A',a='192.0.9.222',zone=z008)
        rr008.save()
        p = PermRr.objects.create(action="rw", group=group008, obj=rr008)
        p.save()

        self.client.login(username='user008', password='user008')
        self.url = f'/rr/'
        data = {'name': 'rr008', 'type': 'A', 'zone': z008.id, 'a': '192.0.9.66',}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    def test_009_api_create_rr_name_type_exist_and_not_updatable_denied(self):
        """ create rr with same name and type as existing RR without update permission
            -> must be denied
        """
        self.client.login(username='titi', password='titi')
        self.url = f'/rr/'
        data = {'name': 'newrr2', 'type': 'A', 'zone': self.z2.id, 'a': '192.0.9.77',}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_012_api_zonerule_create_type_denied(self):
        """ test rr create / typepat zone rule by posting to url "/rr/"; "test456 NS 192.0.9.11 in zone shared.example.com" ; should be denied (NS is not in typepat for zone)
        """

        n012 = Namespace.objects.create(name='z012')
        n012.save()
        z012 = Zone.objects.create(name='z012.example.com',namespace=n012, nsmaster='ns1.example.com', mail='hostmaster.example.com')
        z012.save()

        group012 = Group.objects.create(name='gr012') 
        group012.save()
        user012 = User.objects.create(username='user012', default_pref=group012)
        user012.set_password('user012')
        user012.save()
        group012.user_set.add(user012) 

        # add rr create permission for this zone for this group
        zp012 = PermZone(action='rc', group = group012, obj = z012)
        zp012.save()
        # add zonerule
        tpat1 = '^(A|AAAA|CNAME|MX)$'
        npat1='^[-a-zA-Z0-9_.]+$'
        r = Zonerule.objects.create(zone=z012,typepat=tpat1,namepat=npat1)
        r.save()
       
        self.client.login(username='user012', password='user012')
        data = {'name': 'rr012', 'type': 'NS', 'zone': z012.id, 'ns': 'ns1.example.com',}
        #import ipdb; ipdb.set_trace()
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.content, b'{"detail":"rr create unauthorized: name or type invalid by rule"}')
        
    def test_013_api_zonerule_create_name_denied(self):
        """ test rr create / namepat zone rule check by posting to url "/rr/"; "@ A 192.0.9.12 in zone shared.example.com" ; should be denied (@ is not in namepat for zone)
        """
        self.client.login(username='titi', password='titi')
        data = {'name': '@', 'type': 'A', 'zone': self.z1.id, 'a': '192.0.9.12',}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_014_api_zonerule_create_with_admin_ok(self):
        """ test rr create zone rule by posting to url "/rr/"; "@ A 192.0.9.1 in zone shared.example.com" ; should be allowed
        """
        n014 = Namespace.objects.create(name='z014')
        n014.save()
        z014 = Zone.objects.create(name='z014.example.com',namespace=n014, nsmaster='ns1.example.com', mail='hostmaster.example.com')
        z014.save()

        group014 = Group.objects.create(name='gr014') 
        group014.save()
        admin014 = User.objects.create(username='admin014', default_pref=group014)
        admin014.set_password('admin014')
        admin014.is_superuser = True
        admin014.save()
        group014.user_set.add(admin014) 

        self.client.login(username='admin014', password='admin014')
        data = {'name': '@', 'type': 'A', 'zone': z014.id, 'a': '192.0.9.1',}
        # DEBUG
        #import ipdb; ipdb.set_trace()
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_015_api_zonerule_create_with_invalid_data(self):
        """ test rr create zone rule by posting to url "/rr/"; "@ A 192.0.9.1 in zone shared.example.com" ; should be allowed
        """
        self.client.login(username='titi', password='titi')
        data = {'name': '@', 'type': '', 'zone': self.z1.id, 'a': '192.0.9.2',}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_016_api_zonerule_create_with_empty_data(self):
        """ test rr create zone rule by posting to url "/rr/"; "@ A 192.0.9.1 in zone shared.example.com" ; should be allowed
        """
        self.client.login(username='titi', password='titi')
        data = {}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_017_api_zonerule_create_with_invalid_data(self):
        """ test rr create zone rule by posting to url "/rr/"; "@ A 192.0.9.1 in zone shared.example.com" ; should be allowed
        """
        self.client.login(username='titi', password='titi')
        data = {'name': '-caribou', 'type': 'A', 'zone': self.z1.id, 'a': '192.0.9.3',}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # FIXME: first implement permission add at RR creation
    # create rr ; check delete

    def test_018_api_test_pref_application_create_rr_and_delete(self):
        """ test if default pref is applied for newly created rr
            create and delete a rr ; delete must be allowed
        """
        n018 = Namespace.objects.create(name='z018')
        n018.save()
        z018 = Zone.objects.create(name='z018.example.com',namespace=n018, nsmaster='ns1.example.com', mail='hostmaster.example.com')
        z018.save()

        group018 = Group.objects.create(name='gr018') 
        group018.save()
        user018 = User.objects.create(username='user018', default_pref=group018)
        user018.set_password('user018')
        user018.save()
        group018.user_set.add(user018) 

        # add rr create permission for this zone for this group
        zp018 = PermZone(action='rc', group = group018, obj = z018)
        zp018.save()
       
        self.client.login(username='user018', password='user018')
        url = f'/rr/'
        data = {'name': 'rr018', 'type': 'A', 'zone': z018.id, 'a': '192.0.9.66',}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # get id of created rr
        #import ipdb; ipdb.set_trace()
        rr018 = Rr.objects.get(name='rr018')
        perm_exists = PermRr.objects.filter(obj=rr018,group=group018,action__contains='w').exists()
        self.assertTrue(perm_exists)
    
#        response = self.client.delete(urldelete)
#        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
#
