from django.contrib.auth.models import User, Group
from rest_framework import status
from rest_framework.test import APITestCase
from core.models import Namespace, Zone, Rr, Zonerule
from guardian.shortcuts import assign_perm

class APIPermTests(APITestCase):
    def setUp(self):
        # Create user 'toto' and put user in group 'gr1'
        u = User.objects.create(username='toto')
        u.set_password('toto')
        u.save()
        g = Group.objects.create(name='gr1') 
        g.save()
        g.user_set.add(u) 

        # Allowed namespace
        n1 = Namespace.objects.create(name='default')
        n1.save()
        # Forbidden namespace
        n2 = Namespace.objects.create(name='other')
        n2.save()
        # Give access to 'default' namespace
        assign_perm('access_namespace', g, n1)

        # Allowed zone
        z1 = Zone.objects.create(name='example.com',namespace=n1)
        z1.save()
        # Forbidden zone
        z2 = Zone.objects.create(name='otherexample.com',namespace=n1)
        z2.save()
        # Allowed zone in forbidden namespace
        z3 = Zone.objects.create(name='example.net',namespace=n2)
        z3.save()
        # Give access to 'example.com' zone
        assign_perm('access_zone', g, z1)
        # Give access to 'example.net' zone
        # (in 'other' namespace whose access is forbidden)
        assign_perm('access_zone', g, z3)

        # Set rules for create
        tpat1 = '^(A|AAAA|CNAME|MX)$'
        npat1='^[-a-zA-Z0-9_.]+$'
        r1 = Zonerule.objects.create(zone=z1,typepat=tpat1,namepat=npat1)
        
        # Login 
        self.client.login(username='toto', password='toto')
            
    def test_001_api_namespace_get_perm_ok(self):
        """ test access permission to an allowed namespace "default" ; should be ok
        """
        # request
        
        n1 = Namespace.objects.get(name="default")
        url = f'/namespace/{str(n1.id)}/'
        # check
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_002_api_namespace_get_perm_denied(self):
        """ test access to a forbidden namespace /namespace/2; should be denied
        """
        # request
        n2 = Namespace.objects.get(name="other")
        url = f'/namespace/{str(n2.id)}/'
        # check
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_003_api_zone_get_perm_ok(self):
        """ test access permission to an allowed zone "example.com" ; should be ok
        """
        id=str(Zone.objects.get(name="example.com").id)
        # request
        url = f'/zone/{id}/'
        # check
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_004_api_zone_get_perm_denied(self):
        """ test access permission to a forbidden zone /zone/2 ; should be denied
        """
        id=str(Zone.objects.get(name="otherexample.com").id)
        # request
        url = f'/zone/{id}/'
        # check
        response =  self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_005_api_zone_get_perm_ok_in_denied_namespace(self):
        """ test access permission 
        """
        id=str(Zone.objects.get(name="example.net").id)
        # request
        url = f'/zone/{id}/'
        # check
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # FIXME: test collection
