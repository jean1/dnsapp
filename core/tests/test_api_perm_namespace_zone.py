from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase
from core.models import Namespace, Zone, Rr, Zonerule, PermNamespace, PermZone, User

class APIPermNamespaceZoneTests(APITestCase):
    def setUp(self):
        # Create group 'gr1' and default group
        g = Group.objects.create(name='gr1') 
        g.save()
        defgrp = Group.objects.create(name='defgrp') 
        defgrp.save()

        # Create user 'admin' and put user in group 'admin'
        self.admin = User.objects.create(username='admin', default_pref=defgrp)
        self.admin.set_password('admin')
        self.admin.is_superuser = True
        self.admin.save()
        # Create user 'toto' and put user in group 'gr1'
        u = User.objects.create(username='toto', default_pref=g)
        u.set_password('toto')
        u.save()
        # Put user u in group g
        g.user_set.add(u) 
        # Allowed namespace
        self.nsdefault = Namespace.objects.create(name='default')
        self.nsdefault.save()
        # Forbidden namespace (no permission)
        self.nsother = Namespace.objects.create(name='other')
        self.nsother.save()
        # Allowed namespace
        self.nsmyns = Namespace.objects.create(name='myns')
        self.nsmyns.save()

        # Give access to 'myns' namespace to group g
        self.p3 = PermNamespace(action = 'rw', group = g, obj = self.nsmyns) 
        self.p3.save()
        # + Give access to 'default' namespace to group g
        # + Give zone creation permission to 'default' namespace to group g
        self.p4 = PermNamespace(action = 'rc', group = g, obj = self.nsdefault)
        self.p4.save()

        # Allowed zone
        self.z1 = Zone.objects.create(name='example.com',namespace=self.nsdefault, nsmaster='ns1.example.com', mail='hostmaster.example.com')
        self.z1.save()
        # Denied zone, zone created but no perm created
        self.z2 = Zone.objects.create(name='denied.example.com',namespace=self.nsdefault, nsmaster='ns1.example.com', mail='hostmaster.example.com')
        self.z2.save()
        # Allowed zone in forbidden namespace
        self.z3 = Zone.objects.create(name='example.net',namespace=self.nsother, nsmaster='ns1.example.com', mail='hostmaster.example.com')
        self.z3.save()
        # updatable zone
        self.z4 = Zone.objects.create(name='update.example.com',namespace=self.nsdefault, nsmaster='ns1.example.com', mail='hostmaster.example.com')
        self.z4.save()
        # Give read access to 'example.com' zone to g
        self.zp1 = PermZone(action='r', group = g, obj = self.z1)
        self.zp1.save()
        # Give read-write access to 'example.net' zone to g
        # (in 'other' namespace whose access is forbidden)
        self.zp4 = PermZone(action='rw', group = g, obj = self.z3)
        self.zp4.save()
        # Give read-write access to 'update.example.net' zone to g
        self.zp5 = PermZone(action='rw', group = g, obj = self.z4)
        self.zp5.save()
        # NB: Group g has no access to z2

    def test_000_api_namespace_get_all_allowed_namespace(self):
        """ test access permission to all allowed namespace "default" 
            must get 2 namespaces
        """
        # request
        url = f'/namespace/'
        # check
        self.client.login(username='toto', password='toto')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        number_of_namespace = len(response.data)
        self.assertEqual(number_of_namespace, 2)
            
    def test_001_api_namespace_get_perm_ok(self):
        """ test access permission to an allowed namespace "default" 
             must be ok
        """
        # request
        nsdefault = str(self.nsdefault.id)
        url = f'/namespace/{nsdefault}/'
        # check
        self.client.login(username='toto', password='toto')
        response = self.client.get(url)
        self.assertTrue(status.is_success(response.status_code))

    def test_002_api_namespace_get_perm_denied(self):
        """ test access to a forbidden namespace /namespace/2
             must be denied
        """
        # request
        nsother = str(self.nsother.id)
        url = f'/namespace/{nsother}/'
        # check
        self.client.login(username='toto', password='toto')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_003_api_namespace_nonadmin_delete_denied(self):
        """ test delete to a namespace /namespace/2 for non-admin user
            must be denied
        """
        nsother = str(self.nsother.id)
        url = f'/namespace/{nsother}/'
        # check
        self.client.login(username='toto', password='toto')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_004_api_namespace_admin_delete_allow(self):
        """ test delete to a namespace /namespace/3 for admin user
            must be allowed
        """
        nsmyns = str(self.nsmyns.id)
        url = f'/namespace/{nsmyns}/'
        self.client.login(username='admin', password='admin')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_005_api_namespace_nonadmin_create_denied(self):
        """ test create of a namespace by non-admin user
            must be denied
        """
        url = f'/namespace/'
        self.client.login(username='toto', password='toto')
        data = {'name': 'foobar'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) 

    def test_006_api_namespace_admin_create_allow(self):
        """ test create of a namespace by admin user
            must be allowed
        """
        url = f'/namespace/'
        self.client.login(username='admin', password='admin')
        data = {'name': 'foobar'}
        response = self.client.post(url, data)
        self.assertTrue(status.is_success(response.status_code))

    def test_007_api_namespace_get_all_namespace_as_admin(self):
        """ test access permission to all allowed namespace "default" 
            must get 3 namespaces
        """
        # request
        url = f'/namespace/'
        # check
        self.client.login(username='admin', password='admin')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        number_of_namespace = len(response.data)
        self.assertEqual(number_of_namespace, 3)
            

    def test_010_api_zone_get_perm_ok(self):
        """ test access permission to an allowed zone "example.com" 
             must be ok
        """
        z1id = str(self.z1.id)
        # request
        url = f'/zone/{z1id}/'
        # check
        self.client.login(username='toto', password='toto')
        #import ipdb; ipdb.set_trace()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_011_api_zone_get_perm_denied(self):
        """ test access permission to a forbidden zone /zone/2 
             must be denied
        """
        z2 = str(self.z2.id)
        # request
        url = f'/zone/{z2}/'
        # check
        self.client.login(username='toto', password='toto')
        response =  self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_012_api_zone_get_perm_ok_in_denied_namespace(self):
        """ test access permission : zone allowed under unallowed namespace
            must be ok
        """
        z3=str(self.z3.id)
        # request
        url = f'/zone/{z3}/'
        # check
        self.client.login(username='toto', password='toto')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_013_api_zone_get_allowed_zones(self):
        """ test access to list of allowed zones
            only 3 zones must be retrieved
        """
        # request
        url = f'/zone/'
        self.client.login(username='toto', password='toto')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        number_of_zones = len(response.data)
        self.assertEqual(number_of_zones, 3)

    def test_014_api_zone_delete_allowed_zone(self):
        """ test delete allowed zone
            must be ok
        """
        z3 = str(self.z3.id)
        # request
        url = f'/zone/{z3}/'
        self.client.login(username='toto', password='toto')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_015_api_zone_delete_denied_zone(self):
        """ test delete allowed zone
            must be denied
        """
        z1 = str(self.z1.id)
        # request
        url = f'/zone/{z1}/'
        self.client.login(username='toto', password='toto')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_016_api_zone_update_allowed_zone(self):
        """ test update allowed zone
            must be ok
        """
        nsother = self.nsother.id
        z4 = str(self.z4.id)
        # request
        url = f'/zone/{z4}/'
        self.client.login(username='toto', password='toto')
        data = {'name': 'update1.example.com', 'namespace': nsother, 'nsmaster': 'ns2.example.com', 'mail': 'hostmaster6.example.com'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_017_api_zone_update_denied_zone(self):
        """ test update allowed zone
            must be denied
        """
        z1 = str(self.z1.id)
        nsdefault = self.nsdefault.id
        # request
        url = f'/zone/{z1}/'
        self.client.login(username='toto', password='toto')
        data = {'name': 'foo.example.com', 'namespace': nsdefault, 'nsmaster': 'ns2.example.com', 'mail': 'hostmaster6.example.com'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_018_api_zone_create_denied(self):
        """ test create of a zone in namespace without zone creation permission
            (ie. no permission "CreateZoneInNamespace" for group g1 for namespace "other")
            must be denied
        """
        nsother = self.nsother.id
        url = f'/zone/'
        self.client.login(username='toto', password='toto')
        data = {'name': 'myzone.example.com', 'namespace': nsother, 'nsmaster': 'ns1.example.com', 'mail': 'hostmaster.example.com'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) 

    def test_019_api_zone_create_allow(self):
        """ test create of a zone in namespace with zone creation permission for namespace
            must be ok
        """
        nsdefault = self.nsdefault.id
        url = f'/zone/'
        self.client.login(username='toto', password='toto')
        data = {'name': 'myzone.example.com', 'namespace': nsdefault, 'nsmaster': 'ns1.example.com', 'mail': 'hostmaster.example.com'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
