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
        pass

    def test_000_api_get_access_rr(self):
        """ create rr and read permission for group
            accessed rr with GET
            -> must be allowed
        """
        # Create group & user
        group000 = Group.objects.create(name='group000') 
        group000.save()
        user000 = User.objects.create(username='user000', default_pref=group000)
        user000.set_password('user000')
        user000.save()
        # Assign user to group
        group000.user_set.add(user000) 
        # Create namespace & zone
        namespace000 = Namespace.objects.create(name='namespace000')
        namespace000.save()
        zone000 = Zone.objects.create(name='zone000.example.com',namespace=namespace000, nsmaster='ns1.example.com', mail='hostmaster.example.com')
        zone000.save()
        # Create RR and permissions
        # rr has read and write access for group group000
        rr000 = Rr.objects.create(name='rr000',type='A',a='192.0.9.1',zone=zone000)
        rr000.save()
        pr000 = PermRr.objects.create(action="rw",group=group000,obj=rr000)
        pr000.save()

        url = f'/rr/{rr000.id}/'
        self.client.login(username='user000', password='user000')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
            
    def test_001_api_get_rr_not_allowed(self):
        """ access to rr001 for groups of user user001 (group001-1, group001-2)
            "r" permission exist only for group group001-3 to rr001
            and user is not in group group001-3
            -> must be denied
        """

        # Create group & user
        group001_1 = Group.objects.create(name='group001-1')
        group001_1.save()
        group001_2 = Group.objects.create(name='group001-2')
        group001_2.save()
        group001_3 = Group.objects.create(name='group001-3')
        group001_3.save()
        user001 = User.objects.create(username='user001', default_pref=group001_1)
        user001.set_password('user001')
        user001.save()
        # assign user to groups 1 & 2, not 3
        group001_1.user_set.add(user001) 
        group001_2.user_set.add(user001) 

        # Create namespace
        namespace001 = Namespace.objects.create(name='namespace001')
        namespace001.save()
        # Create zone (without any permission as zone permission are not necessary for rr access)
        zone001 = Zone.objects.create(name='zone001.example.com',namespace=namespace001, nsmaster='ns1.example.com', mail='hostmaster.example.com')
        zone001.save()

        # rr001 has read access for group group001-3
        rr001 = Rr.objects.create(name='rr001',type='A',a='192.0.9.2', zone=zone001)
        rr001.save()
        pr001 = PermRr.objects.create(action="r",group=group001_3,obj=rr001)
        pr001.save()

        url = f'/rr/{rr001.id}/'
        self.client.login(username='user001', password='user001')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_002_api_get_all_allowed_rr(self):
        """ access to all allowed rr for a given user
            -> response must contain 2 rr
        """
        n002 = Namespace.objects.create(name='namespace002')
        n002.save()
        zone002 = Zone.objects.create(name='zone002.example.com',namespace=n002, nsmaster='ns1.example.com', mail='hostmaster.example.com')
        zone002.save()

        group002 = Group.objects.create(name='group002') 
        group002.save()
        user002 = User.objects.create(username='user002', default_pref=group002)
        user002.set_password('user002')
        user002.save()
        group002.user_set.add(user002) 
       
        # create 2 rr
        rr002_1 = Rr.objects.create(name='rr002-1',type='A',a='192.0.9.221',zone=zone002)
        rr002_1.save()
        pr002_1 = PermRr.objects.create(action="rw", group=group002, obj=rr002_1)
        pr002_1.save()
        rr002_2 = Rr.objects.create(name='rr002-2',type='A',a='192.0.9.222',zone=zone002)
        rr002_2.save()
        pr002_2 = PermRr.objects.create(action="rw", group=group002, obj=rr002_2)
        pr002_2.save()

        url = f'/rr/'
        self.client.login(username='user002', password='user002')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        number_of_rr = len(response.data)
        self.assertEqual(number_of_rr, 2)

    def test_003_api_delete_not_allowed(self):
        """ delete a rr without permission
            -> must be denied
        """
        # Create group & user
        group003 = Group.objects.create(name='group003')
        group003.save()
        user003 = User.objects.create(username='user003', default_pref=group003)
        user003.set_password('user003')
        user003.save()
        # assign user to groups
        group003.user_set.add(user003) 

        # Create namespace
        namespace003 = Namespace.objects.create(name='namespace003')
        namespace003.save()
        # Create zone
        zone003 = Zone.objects.create(name='zone003.example.com',namespace=namespace003, nsmaster='ns1.example.com', mail='hostmaster.example.com')
        zone003.save()
        # create rr003 without permission
        rr003 = Rr.objects.create(name='rr003',type='A',a='192.0.9.2', zone=zone003)
        rr003.save()

        url = f'/rr/{rr003.id}/'
        self.client.login(username='user003', password='user003')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_004_api_delete_rr_ok(self):
        """ delete rr with "w" permission
            -> must be allowed
        """
        # Create group & user
        group004 = Group.objects.create(name='group004')
        group004.save()
        user004 = User.objects.create(username='user004', default_pref=group004)
        user004.set_password('user004')
        user004.save()
        # assign user to groups
        group004.user_set.add(user004) 

        # Create namespace
        namespace004 = Namespace.objects.create(name='namespace004')
        namespace004.save()
        # Create zone
        zone004 = Zone.objects.create(name='zone004.example.com',namespace=namespace004, nsmaster='ns1.example.com', mail='hostmaster.example.com')
        zone004.save()
        # create rr004 wit read-write permission
        rr004 = Rr.objects.create(name='rr004',type='A',a='192.0.9.2', zone=zone004)
        rr004.save()
        pr004 = PermRr.objects.create(action="rw", group=group004, obj=rr004)
        pr004.save()

        url = f'/rr/{rr004.id}/'
        self.client.login(username='user004', password='user004')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_005_api_create_rr_in_zone_ok(self):
        """ create rr 
            rr in zone create permission is set
            -> must be allowed
        """
        # Create group & user
        group005 = Group.objects.create(name='group005')
        group005.save()
        user005 = User.objects.create(username='user005', default_pref=group005)
        user005.set_password('user005')
        user005.save()
        # assign user to group
        group005.user_set.add(user005) 

        # Create namespace
        namespace005 = Namespace.objects.create(name='namespace005')
        namespace005.save()
        # Create zone
        zone005 = Zone.objects.create(name='zone005.example.com',namespace=namespace005, nsmaster='ns1.example.com', mail='hostmaster.example.com')
        zone005.save()
        # Add permission to create rr in zone
        zp005 = PermZone(action='rc', group = group005, obj = zone005)
        zp005.save()

        self.client.login(username='user005', password='user005')
        url = f'/rr/'
        data = {'name': 'rr005', 'type': 'A', 'zone': zone005.id, 'a': '192.0.9.11',}
        #import ipdb; ipdb.set_trace()
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_006_api_create_rr_in_zone_ok(self):
        """ create rr in zone z2 without permission "c"
            -> must be denied
        """
        # Create group & user
        group006 = Group.objects.create(name='group006')
        group006.save()
        user006 = User.objects.create(username='user006', default_pref=group006)
        user006.set_password('user006')
        user006.save()
        # assign user to group
        group006.user_set.add(user006) 

        # Create namespace
        namespace006 = Namespace.objects.create(name='namespace006')
        namespace006.save()
        # Create zone
        zone006 = Zone.objects.create(name='zone006.example.com',namespace=namespace006, nsmaster='ns1.example.com', mail='hostmaster.example.com')
        zone006.save()
        zp006 = PermZone(action='r', group = group006, obj = zone006)
        zp006.save()

        self.client.login(username='user006', password='user006')
        url = f'/rr/'
        data = {'name': 'rr006', 'type': 'A', 'zone': zone006.id, 'a': '192.0.9.12',}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_007_api_create_rr_name_exist_ok(self):
        """ create rr with same name as an existing rr in same zone 
            But this new rr has different type, A as other rr is of type TXT
            -> must be allowed
        """
        # Create group & user
        group007 = Group.objects.create(name='group007')
        group007.save()
        user007 = User.objects.create(username='user007', default_pref=group007)
        user007.set_password('user007')
        user007.save()
        # assign user to group
        group007.user_set.add(user007) 

        # Create namespace
        namespace007 = Namespace.objects.create(name='namespace007')
        namespace007.save()
        # Create zone
        zone007 = Zone.objects.create(name='zone007.example.com',namespace=namespace007, nsmaster='ns1.example.com', mail='hostmaster.example.com')
        zone007.save()
        zp007 = PermZone(action='rc', group = group007, obj = zone007)
        zp007.save()

        # create first rr as TXT without permission
        rr007 = Rr.objects.create(name='rr007',type='TXT',txt='foobar',zone=zone007)
        rr007.save()

        self.client.login(username='user007', password='user007')
        url = f'/rr/'
        # create new rr with same name
        data = {'name': 'rr007', 'type': 'A', 'zone': zone007.id, 'a': '192.0.9.12',}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_008_api_create_rr_name_type_exist_and_updatable_ok(self):
        """ create rr with same name and type as existing RR with update permission
            -> must be allowed
        """

        n008 = Namespace.objects.create(name='namespace008')
        n008.save()
        zone008 = Zone.objects.create(name='zone008.example.com',namespace=n008, nsmaster='ns1.example.com', mail='hostmaster.example.com')
        zone008.save()

        group008 = Group.objects.create(name='group008') 
        group008.save()
        user008 = User.objects.create(username='user008', default_pref=group008)
        user008.set_password('user008')
        user008.save()
        group008.user_set.add(user008) 

        # add rr create permission for this zone for this group
        zp008 = PermZone(action='rc', group = group008, obj = zone008)
        zp008.save()
       
        # rr008 has same name and same type as the rr we will create is this test 
        # and is updatable by user008 in group008
        rr008 = Rr.objects.create(name='rr008',type='A',a='192.0.9.222',zone=zone008)
        rr008.save()
        p = PermRr.objects.create(action="rw", group=group008, obj=rr008)
        p.save()

        self.client.login(username='user008', password='user008')
        url = f'/rr/'
        data = {'name': 'rr008', 'type': 'A', 'zone': zone008.id, 'a': '192.0.9.66',}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    def test_009_api_create_rr_name_type_exist_and_not_updatable_denied(self):
        """ create rr with same name and type as existing RR without update permission
            -> must be denied
        """
        group009 = Group.objects.create(name='group009') 
        group009.save()
        user009 = User.objects.create(username='user009', default_pref=group009)
        user009.set_password('user009')
        user009.save()
        group009.user_set.add(user009) 

        # create namespace
        n009 = Namespace.objects.create(name='namespace009')
        n009.save()
        # create zone
        # add rr create permission for this zone for this group
        zone009 = Zone.objects.create(name='zone009.example.com',namespace=n009, nsmaster='ns1.example.com', mail='hostmaster.example.com')
        zone009.save()
        zp009 = PermZone(action='rc', group = group009, obj = zone009)
        zp009.save()
       
        # rr009 has same name and same type as the rr we will create is this test 
        # and is updatable by user009 in group009
        rr009 = Rr.objects.create(name='rr009',type='A',a='192.0.9.222',zone=zone009)
        rr009.save()
        p = PermRr.objects.create(action="r", group=group009, obj=rr009)
        p.save()

        self.client.login(username='user009', password='user009')
        url = f'/rr/'
        data = {'name': 'rr009', 'type': 'A', 'zone': zone009.id, 'a': '192.0.9.77',}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_012_api_zonerule_create_type_denied(self):
        """ rr create / typepat zone rule by posting to url "/rr/"; "test456 NS 192.0.9.11 in zone shared.example.com" ; must be denied (NS is not in typepat for zone)
        """

        n012 = Namespace.objects.create(name='namespace012')
        n012.save()
        zone012 = Zone.objects.create(name='zone012.example.com',namespace=n012, nsmaster='ns1.example.com', mail='hostmaster.example.com')
        zone012.save()

        group012 = Group.objects.create(name='group012') 
        group012.save()
        user012 = User.objects.create(username='user012', default_pref=group012)
        user012.set_password('user012')
        user012.save()
        group012.user_set.add(user012) 

        # add rr create permission for this zone for this group
        zp012 = PermZone(action='rc', group = group012, obj = zone012)
        zp012.save()
        # add zonerule
        tpat1 = '^(A|AAAA|CNAME|MX)$'
        npat1='^[-a-zA-Z0-9_.]+$'
        r = Zonerule.objects.create(zone=zone012,typepat=tpat1,namepat=npat1)
        r.save()
       
        self.client.login(username='user012', password='user012')
        data = {'name': 'rr012', 'type': 'NS', 'zone': zone012.id, 'ns': 'ns1.example.com',}

        #import ipdb; ipdb.set_trace()
        url = f'/rr/'
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.content, b'{"detail":"rr create unauthorized: name or type invalid by rule"}')
        
    def test_013_api_zonerule_create_name_denied(self):
        """ namepat zone rule checks for alphanumeric char in name
            create a rr named "@"
            -> must be denied: @ is not in namepat for zone
        """
        n013 = Namespace.objects.create(name='namespace013')
        n013.save()
        zone013 = Zone.objects.create(name='zone013.example.com',namespace=n013, nsmaster='ns1.example.com', mail='hostmaster.example.com')
        zone013.save()

        group013 = Group.objects.create(name='group013')
        group013.save()
        user013 = User.objects.create(username='user013', default_pref=group013)
        user013.set_password('user013')
        user013.save()
        group013.user_set.add(user013) 

        # add rr create permission for this zone for this group
        zp013 = PermZone(action='rc', group = group013, obj = zone013)
        zp013.save()
        # add zonerule
        tpat1 = '^(A|AAAA|CNAME|MX)$'
        npat1='^[-a-zA-Z0-9_.]+$'
        r = Zonerule.objects.create(zone=zone013,typepat=tpat1,namepat=npat1)
        r.save()
       
        self.client.login(username='user013', password='user013')
        url = f'/rr/'
        data = {'name': '@', 'type': 'A', 'zone': zone013.id, 'a': '192.0.9.12',}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_014_api_zonerule_create_with_admin_ok(self):
        """ zone rule is defined 
            admin creates a rr
        -> must be allowed
        """
        n014 = Namespace.objects.create(name='namespace014')
        n014.save()
        zone014 = Zone.objects.create(name='zone014.example.com',namespace=n014, nsmaster='ns1.example.com', mail='hostmaster.example.com')
        zone014.save()

        # create user as admin
        group014 = Group.objects.create(name='group014') 
        group014.save()
        admin014 = User.objects.create(username='admin014', default_pref=group014)
        admin014.set_password('admin014')
        admin014.is_superuser = True
        admin014.save()
        group014.user_set.add(admin014) 

        # create zone rule
        tpat1 = '^(A|AAAA|CNAME|MX)$'
        npat1='^[-a-zA-Z0-9_.]+$'
        r = Zonerule.objects.create(zone=zone014,typepat=tpat1,namepat=npat1)
        r.save()

        self.client.login(username='admin014', password='admin014')
        url = f'/rr/'
        data = {'name': '@', 'type': 'A', 'zone': zone014.id, 'a': '192.0.9.1',}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_015_api_zonerule_create_with_invalid_data(self):
        """ zone rule exist
            create rr with empty string for "type" field
            -> must be rejected as invalid
        """
        n015 = Namespace.objects.create(name='namespace015')
        n015.save()
        zone015 = Zone.objects.create(name='zone015.example.com',namespace=n015, nsmaster='ns1.example.com', mail='hostmaster.example.com')
        zone015.save()

        group015 = Group.objects.create(name='group015')
        group015.save()
        user015 = User.objects.create(username='user015', default_pref=group015)
        user015.set_password('user015')
        user015.save()
        group015.user_set.add(user015) 

        # add rr create permission for this zone for this group
        zp015 = PermZone(action='rc', group = group015, obj = zone015)
        zp015.save()
        # add zonerule
        tpat1 = '^(A|AAAA|CNAME|MX)$'
        npat1='^[-a-zA-Z0-9_.]+$'
        r = Zonerule.objects.create(zone=zone015,typepat=tpat1,namepat=npat1)
        r.save()
       
        self.client.login(username='user015', password='user015')
        url = f'/rr/'
        data = {'name': '@', 'type': '', 'zone': zone015.id, 'a': '192.0.9.2',}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_016_api_zonerule_create_with_empty_data(self):
        """ zone rule exist
            create rr with empty serializer
            -> must be rejected as invalid
        """
        n016 = Namespace.objects.create(name='namespace016')
        n016.save()
        zone016 = Zone.objects.create(name='zone016.example.com',namespace=n016, nsmaster='ns1.example.com', mail='hostmaster.example.com')
        zone016.save()

        group016 = Group.objects.create(name='group016')
        group016.save()
        user016 = User.objects.create(username='user016', default_pref=group016)
        user016.set_password('user016')
        user016.save()
        group016.user_set.add(user016) 

        # add rr create permission for this zone for this group
        zp016 = PermZone(action='rc', group = group016, obj = zone016)
        zp016.save()
        # add zonerule
        tpat1 = '^(A|AAAA|CNAME|MX)$'
        npat1='^[-a-zA-Z0-9_.]+$'
        r = Zonerule.objects.create(zone=zone016,typepat=tpat1,namepat=npat1)
        r.save()
       
        self.client.login(username='user016', password='user016')
        url = f'/rr/'
        data = {}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_017_api_zonerule_create_with_invalid_name(self):
        """ 
            zone rule exist
            create rr with name starting with a dash
            -> must be rejected as invalid
        """
        n017 = Namespace.objects.create(name='namespace017')
        n017.save()
        zone017 = Zone.objects.create(name='zone017.example.com',namespace=n017, nsmaster='ns1.example.com', mail='hostmaster.example.com')
        zone017.save()

        group017 = Group.objects.create(name='group017')
        group017.save()
        user017 = User.objects.create(username='user017', default_pref=group017)
        user017.set_password('user017')
        user017.save()
        group017.user_set.add(user017) 

        # add rr create permission for this zone for this group
        zp017 = PermZone(action='rc', group = group017, obj = zone017)
        zp017.save()
        # add zonerule
        tpat1 = '^(A|AAAA|CNAME|MX)$'
        npat1='^[-a-zA-Z0-9_.]+$'
        r = Zonerule.objects.create(zone=zone017,typepat=tpat1,namepat=npat1)
        r.save()
       
        self.client.login(username='user017', password='user017')
        url = f'/rr/'
        data = {'name': '-rr017', 'type': 'A', 'zone': zone017.id, 'a': '192.0.9.3',}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # FIXME: first implement permission add at RR creation
    # create rr ; check delete
    def test_018_api_test_pref_application_create_rr_and_delete(self):
        """ if default pref is applied for newly created rr
            create and delete a rr ; delete must be allowed
        """
        n018 = Namespace.objects.create(name='namespace018')
        n018.save()
        zone018 = Zone.objects.create(name='zone018.example.com',namespace=n018, nsmaster='ns1.example.com', mail='hostmaster.example.com')
        zone018.save()

        group018 = Group.objects.create(name='group018') 
        group018.save()
        user018 = User.objects.create(username='user018', default_pref=group018)
        user018.set_password('user018')
        user018.save()
        group018.user_set.add(user018) 

        # add rr create permission for this zone for this group
        zp018 = PermZone(action='rc', group = group018, obj = zone018)
        zp018.save()
       
        self.client.login(username='user018', password='user018')
        url = f'/rr/'
        data = {'name': 'rr018', 'type': 'A', 'zone': zone018.id, 'a': '192.0.9.66',}
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
