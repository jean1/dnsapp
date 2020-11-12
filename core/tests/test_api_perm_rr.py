from django.contrib.auth.models import User, Group
from rest_framework import status
from rest_framework.test import APITestCase
from core.models import Namespace, Zone, Rr, Zonerule
from core.serializers import RrSerializer
from rest_framework.renderers import JSONRenderer
from guardian.shortcuts import assign_perm

import sys
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

class APIPermRrTests(APITestCase):
    def setUp(self):
        # Create user 'admin' and put user in group 'admin'
        # admin = User.objects.create(username='admin')
        self.admin = User.objects.create(username='admin')
        self.admin.set_password('admin')
        self.admin.is_superuser = True
        self.admin.save()
        # Create user 'toto' and put user in group 'gr1'
        self.user = User.objects.create(username='titi')
        self.user.set_password('titi')
        self.user.save()
        self.group = Group.objects.create(name='gr2') 
        self.group.save()
        self.group.user_set.add(self.user) 

        self.n1 = Namespace.objects.create(name='mynamespace')
        self.n1.save()
        # Give access to 'default' namespace
        assign_perm('access_namespace', self.group, self.n1)
        # create zone
        self.z1 = Zone.objects.create(name='shared.example.com',namespace=self.n1)
        self.z1.save()
        # Give access to 'example.com' zone
        assign_perm('access_zone', self.group, self.z1)

        # Set rules for create
        tpat1 = '^(A|AAAA|CNAME|MX)$'
        npat1='^[-a-zA-Z0-9_.]+$'
        r1 = Zonerule.objects.create(zone=self.z1,typepat=tpat1,namepat=npat1)
        r1.save()
        self.url = '/rr/'

    def test_010_api_zonerule_create_ok(self):
        """ test rr create zone rule by posting to url "/rr/"; "test123 A 192.0.9.10 in zone shared.example.com" ; should be allowed
        """
        self.client.login(username='titi', password='titi')
        data = {'name': 'test124', 'type': 'A', 'zone': self.z1.id, 'a': '192.0.9.10',}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_011_api_zonerule_create_type_denied(self):
        """ test rr create / typepat zone rule by posting to url "/rr/"; "test456 NS 192.0.9.11 in zone shared.example.com" ; should be denied (NS is not in typepat for zone)
        """
        self.client.login(username='titi', password='titi')
        data = {'name': 'test124', 'type': 'NS', 'zone': self.z1.id, 'nameserver': '192.0.9.11',}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_012_api_zonerule_create_name_denied(self):
        """ test rr create / namepat zone rule check by posting to url "/rr/"; "@ A 192.0.9.12 in zone shared.example.com" ; should be denied (@ is not in namepat for zone)
        """
        self.client.login(username='titi', password='titi')
        data = {'name': '@', 'type': 'A', 'zone': self.z1.id, 'a': '192.0.9.12',}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_013_api_zonerule_create_with_admin_ok(self):
        """ test rr create zone rule by posting to url "/rr/"; "@ A 192.0.9.1 in zone shared.example.com" ; should be allowed
        """
        self.client.login(username='admin', password='admin')
        data = {'name': '@', 'type': 'A', 'zone': self.z1.id, 'a': '192.0.9.1',}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_014_api_zonerule_create_with_invalid_data(self):
        """ test rr create zone rule by posting to url "/rr/"; "@ A 192.0.9.1 in zone shared.example.com" ; should be allowed
        """
        self.client.login(username='titi', password='titi')
        data = {'name': '@', 'type': '', 'zone': self.z1.id, 'a': '192.0.9.2',}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_015_api_zonerule_create_with_empty_data(self):
        """ test rr create zone rule by posting to url "/rr/"; "@ A 192.0.9.1 in zone shared.example.com" ; should be allowed
        """
        self.client.login(username='titi', password='titi')
        data = {}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_016_api_zonerule_create_with_invalid_data(self):
        """ test rr create zone rule by posting to url "/rr/"; "@ A 192.0.9.1 in zone shared.example.com" ; should be allowed
        """
        self.client.login(username='titi', password='titi')
        data = {'name': '-caribou', 'type': 'A', 'zone': self.z1.id, 'a': '192.0.9.3',}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
