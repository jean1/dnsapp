from django.contrib.auth.models import User, Group
from rest_framework import status
from rest_framework.test import APITestCase
from core.models import Namespace, Zone, Rr, Zonerule, PermNamespace, PermZone

class APIPermNamespaceZoneTests(APITestCase):
    def setUp(self):
        # Create user 'admin' and put user in group 'admin'
        self.admin = User.objects.create(username='admin')
        self.admin.set_password('admin')
        self.admin.is_superuser = True
        self.admin.save()
        # Create user 'toto' and put user in group 'gr1'
        u = User.objects.create(username='toto')
        u.set_password('toto')
        u.save()
        g = Group.objects.create(name='gr1') 
        g.save()
        g.user_set.add(u) 

        # Allowed namespace
        self.n1 = Namespace.objects.create(name='default')
        self.n1.save()
        # Forbidden namespace (no permission)
        self.n2 = Namespace.objects.create(name='other')
        self.n2.save()
        # Allowed namespace
        self.n3 = Namespace.objects.create(name='myns')
        self.n3.save()
        # Give access to 'default' namespace
        self.p1 = PermNamespace(action = 'AccessNamespace', group = g, namespace = self.n1)
        self.p1.save()
        # Give access to 'myns' namespace
        self.p3 = PermNamespace(action = 'AccessNamespace', group = g, namespace = self.n3)
        self.p3.save()
        # Give zone creation permission to 'default' namespace
        self.p4 = PermNamespace(action = 'CreateZoneInNamespace', group = g, namespace = self.n1)
        self.p4.save()

        # Allowed zone
        self.z1 = Zone.objects.create(name='example.com',namespace=self.n1, nsmaster='ns1.example.com', mail='hostmaster.example.com')
        self.z1.save()
        # Denied zone, zone created but no perm created
        self.z2 = Zone.objects.create(name='denied.example.com',namespace=self.n1, nsmaster='ns1.example.com', mail='hostmaster.example.com')
        self.z2.save()
        # Allowed zone in forbidden namespace
        self.z3 = Zone.objects.create(name='example.net',namespace=self.n2, nsmaster='ns1.example.com', mail='hostmaster.example.com')
        self.z3.save()
        # updatable zone
        self.z4 = Zone.objects.create(name='update.example.com',namespace=self.n1, nsmaster='ns1.example.com', mail='hostmaster.example.com')
        self.z4.save()
        # Give access to 'example.com' zone
        self.zp1 = PermZone(action='GetZone', group = g, zone = self.z1)
        self.zp1.save()
        # Give access to 'example.net' zone
        # (in 'other' namespace whose access is forbidden)
        self.zp3 = PermZone(action='GetZone', group = g, zone = self.z3)
        self.zp3.save()
        self.zp4 = PermZone(action='DeleteZone', group = g, zone = self.z3)
        self.zp4.save()
        self.zp5 = PermZone(action='UpdateZone', group = g, zone = self.z4)
        self.zp5.save()

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
        n1 = str(self.n1.id)
        url = f'/namespace/{n1}/'
        # check
        self.client.login(username='toto', password='toto')
        response = self.client.get(url)
        self.assertTrue(status.is_success(response.status_code))

    def test_002_api_namespace_get_perm_denied(self):
        """ test access to a forbidden namespace /namespace/2
             must be denied
        """
        # request
        n2 = str(self.n2.id)
        url = f'/namespace/{n2}/'
        # check
        self.client.login(username='toto', password='toto')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_003_api_namespace_nonadmin_delete_denied(self):
        """ test delete to a namespace /namespace/2 for non-admin user
            must be denied
        """
        n2 = str(self.n2.id)
        url = f'/namespace/{n2}/'
        # check
        self.client.login(username='toto', password='toto')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_004_api_namespace_admin_delete_allow(self):
        """ test delete to a namespace /namespace/3 for admin user
            must be allowed
        """
        n3 = str(self.n3.id)
        url = f'/namespace/{n3}/'
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
            only 2 zones must be retrieved
        """
        # request
        url = f'/zone/'
        self.client.login(username='toto', password='toto')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        number_of_zones = len(response.data)
        self.assertEqual(number_of_zones, 2)

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
        n2id = self.n2.id
        z4 = str(self.z4.id)
        # request
        url = f'/zone/{z4}/'
        self.client.login(username='toto', password='toto')
        data = {'name': 'update1.example.com', 'namespace': n2id, 'nsmaster': 'ns2.example.com', 'mail': 'hostmaster6.example.com'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_017_api_zone_update_denied_zone(self):
        """ test update allowed zone
            must be denied
        """
        z1 = str(self.z1.id)
        n1id = self.n1.id
        # request
        url = f'/zone/{z1}/'
        self.client.login(username='toto', password='toto')
        data = {'name': 'foo.example.com', 'namespace': n1id, 'nsmaster': 'ns2.example.com', 'mail': 'hostmaster6.example.com'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_018_api_zone_create_denied(self):
        """ test create of a zone in namespace without zone creation permission
            (ie. no permission "CreateZoneInNamespace" for group g1 for namespace "other")
            must be denied
        """
        n2id = self.n2.id
        url = f'/zone/'
        self.client.login(username='toto', password='toto')
        data = {'name': 'myzone.example.com', 'namespace': n2id, 'nsmaster': 'ns1.example.com', 'mail': 'hostmaster.example.com'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) 

    def test_019_api_zone_create_allow(self):
        """ test create of a zone in namespace with zone creation permission for namespace
            must be ok
        """
        n1id = self.n1.id
        url = f'/zone/'
        self.client.login(username='toto', password='toto')
        data = {'name': 'myzone.example.com', 'namespace': n1id, 'nsmaster': 'ns1.example.com', 'mail': 'hostmaster.example.com'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
