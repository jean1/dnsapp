from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase
from core.models import Namespace, Zone, Rr, Zonerule, PermNamespace, PermZone, User

class APIPermNamespaceZoneTests(APITestCase):
    def setUp(self):
        # Create default group
        defgrp = Group.objects.create(name='defgrp') 
        defgrp.save()
        # Create user 'admin' and make it superuser
        admin = User.objects.create(username='admin', default_pref=defgrp)
        admin.set_password('admin')
        admin.is_superuser = True
        admin.save()

    def test_000_api_namespace_get_all_allowed_namespace(self):
        """ test access permission to all allowed namespace "default" 
            must get 3 namespaces
        """
        # Create group, user
        group000 = Group.objects.create(name='group000') 
        group000.save()
        user000 = User.objects.create(username='user000', default_pref=group000)
        user000.set_password('user000')
        user000.save()
        # Put user in group
        group000.user_set.add(user000) 

        # Create namespaces and permissions
        namespace000_1 = Namespace.objects.create(name='namespace000_1')
        namespace000_1.save()
        namespace000_2 = Namespace.objects.create(name='namespace000_2')
        namespace000_2.save()
        namespace000_3 = Namespace.objects.create(name='namespace000_3')
        namespace000_3.save()
        perm000_1 = PermNamespace(action = 'r', group = group000, obj = namespace000_1) 
        perm000_1.save()
        perm000_2 = PermNamespace(action = 'rw', group = group000, obj = namespace000_2) 
        perm000_2.save()
        perm000_3 = PermNamespace(action = 'rwc', group = group000, obj = namespace000_3) 
        perm000_3.save()

        # request
        url = f'/namespace/'
        # check
        self.client.login(username='user000', password='user000')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        number_of_namespace = len(response.data)
        self.assertEqual(number_of_namespace, 3)
        # Cleanup
        namespace000_1.delete()
        namespace000_2.delete()
        namespace000_3.delete()
    
    def test_001_api_namespace_get_perm_ok(self):
        """ test access permission to an allowed namespace 
             must be ok
        """
        # Create group, user
        group001 = Group.objects.create(name='group001') 
        group001.save()
        user001 = User.objects.create(username='user001', default_pref=group001)
        user001.set_password('user001')
        user001.save()
        # Put user in group
        group001.user_set.add(user001) 

        # Create namespaces and permissions
        namespace001 = Namespace.objects.create(name='namespace001')
        namespace001.save()
        perm001 = PermNamespace(action = 'r', group = group001, obj = namespace001) 
        perm001.save()

        # request
        url = f'/namespace/{namespace001.id}/'
        # check
        self.client.login(username='user001', password='user001')
        response = self.client.get(url)
        self.assertTrue(status.is_success(response.status_code))
        # Cleanup
        namespace001.delete()

    def test_002_api_namespace_get_perm_denied(self):
        """ test access to a forbidden namespace /namespace/2
             must be denied
        """
        # Create group, user
        group002 = Group.objects.create(name='group002') 
        group002.save()
        user002 = User.objects.create(username='user002', default_pref=group002)
        user002.set_password('user002')
        user002.save()
        # Put user in group
        group002.user_set.add(user002) 
        # Create namespace but no permission
        namespace002 = Namespace.objects.create(name='namespace002')
        namespace002.save()

        # request
        url = f'/namespace/{namespace002.id}/'
        # check
        self.client.login(username='user002', password='user002')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Cleanup
        namespace002.delete()

    def test_003_api_namespace_nonadmin_delete_denied(self):
        """ test delete to a namespace for non-admin user
            must be denied
        """
        # Create group, user
        group003 = Group.objects.create(name='group003') 
        group003.save()
        user003 = User.objects.create(username='user003', default_pref=group003)
        user003.set_password('user003')
        user003.save()
        # Put user in group
        group003.user_set.add(user003) 
        # Create namespace and permission
        namespace003 = Namespace.objects.create(name='namespace003')
        namespace003.save()
        perm003 = PermNamespace(action = 'rwc', group = group003, obj = namespace003) 
        perm003.save()

        url = f'/namespace/{namespace003.id}/'
        # check
        self.client.login(username='user003', password='user003')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Cleanup
        namespace003.delete()

    def test_004_api_namespace_admin_delete_allow(self):
        """ test delete to a namespace for admin user
            must be allowed
        """
        # Create namespace and no permission
        namespace004 = Namespace.objects.create(name='namespace004')
        namespace004.save()
        url = f'/namespace/{namespace004.id}/'
        self.client.login(username='admin', password='admin')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_005_api_namespace_nonadmin_create_denied(self):
        """ test create of a namespace by non-admin user
            must be denied
        """
        # Create group, user
        group004 = Group.objects.create(name='group004') 
        group004.save()
        user004 = User.objects.create(username='user004', default_pref=group004)
        user004.set_password('user004')
        user004.save()
        # Put user in group
        group004.user_set.add(user004) 

        url = f'/namespace/'
        self.client.login(username='user004', password='user004')
        data = {'name': 'foobar'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) 

    def test_006_api_namespace_admin_create_allow(self):
        """ test create of a namespace by admin user
            must be allowed
        """
        url = f'/namespace/'
        self.client.login(username='admin', password='admin')
        data = {'name': 'namespace006'}
        response = self.client.post(url, data)
        self.assertTrue(status.is_success(response.status_code))
        # cleanup
        namespace006 = Namespace.objects.get(name='namespace006')
        namespace006.delete

    def test_007_api_namespace_get_all_namespace_as_admin(self):
        """ test admin access to all allowed namespaces
            must get 3 namespaces
        """

        # Create namespaces
        namespace007_1 = Namespace.objects.create(name='namespace007_1')
        namespace007_1.save()
        namespace007_2 = Namespace.objects.create(name='namespace007_2')
        namespace007_2.save()
        namespace007_3 = Namespace.objects.create(name='namespace007_3')
        namespace007_3.save()

        # request
        url = f'/namespace/'
        # check
        self.client.login(username='admin', password='admin')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        number_of_namespace = len(response.data)
        self.assertEqual(number_of_namespace, 3)
        # Cleanup
        namespace007_1.delete()
        namespace007_2.delete()
        namespace007_3.delete()

    def test_010_api_zone_get_perm_ok(self):
        """ test access permission to an allowed zone "example.com" 
             must be ok
        """
        # Create group, user
        group010 = Group.objects.create(name='group010') 
        group010.save()
        user010 = User.objects.create(username='user010', default_pref=group010)
        user010.set_password('user010')
        user010.save()
        # Put user in group
        group010.user_set.add(user010) 
        # Create namespace and permission
        namespace010 = Namespace.objects.create(name='namespace010')
        namespace010.save()
        namespace010perm = PermNamespace(action = 'rwc', group = group010, obj = namespace010) 
        namespace010perm.save()
        # Create zone
        zone010 = Zone.objects.create(name='zone010.example.com',namespace=namespace010, nsmaster='ns1.example.com', mail='hostmaster.example.com')
        zone010.save()
        # Create zone permission
        zone010perm = PermZone(action='r', group = group010, obj = zone010)
        zone010perm.save()

        # request
        url = f'/zone/{zone010.id}/'
        # check
        self.client.login(username='user010', password='user010')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Cleanup
        zone010.delete()
        namespace010.delete()

    def test_011_api_zone_get_perm_denied(self):
        """ test access permission to a zone with no permission
             must be denied
        """
        # Create group, user
        group011 = Group.objects.create(name='group011') 
        group011.save()
        user011 = User.objects.create(username='user011', default_pref=group011)
        user011.set_password('user011')
        user011.save()
        # Put user in group
        group011.user_set.add(user011) 
        # Create namespace and permission
        namespace011 = Namespace.objects.create(name='namespace011')
        namespace011.save()
        namespace011perm = PermNamespace(action = 'rwc', group = group011, obj = namespace011) 
        namespace011perm.save()
        # Create zone without permission
        zone011 = Zone.objects.create(name='zone011.example.com',namespace=namespace011, nsmaster='ns1.example.com', mail='hostmaster.example.com')
        zone011.save()

        # request
        url = f'/zone/{zone011.id}/'
        # check
        self.client.login(username='user011', password='user011')
        response =  self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Cleanup
        zone011.delete()
        namespace011.delete()

    def test_012_api_zone_get_perm_ok_in_denied_namespace(self):
        """ test access permission : zone allowed under unallowed namespace
            must be ok
        """
        # Create group, user
        group012 = Group.objects.create(name='group012') 
        group012.save()
        user012 = User.objects.create(username='user012', default_pref=group012)
        user012.set_password('user012')
        user012.save()
        # Put user in group
        group012.user_set.add(user012) 
        # Create namespace without any permission
        namespace012 = Namespace.objects.create(name='namespace012')
        namespace012.save()
        # Create zone
        zone012 = Zone.objects.create(name='zone012.example.com',namespace=namespace012, nsmaster='ns1.example.com', mail='hostmaster.example.com')
        zone012.save()
        # Create zone permission
        zone012perm = PermZone(action='r', group = group012, obj = zone012)
        zone012perm.save()

        # request
        url = f'/zone/{zone012.id}/'
        # check
        self.client.login(username='user012', password='user012')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Cleanup
        zone012.delete()
        namespace012.delete()

    def test_013_api_zone_get_allowed_zones(self):
        """ test access to list of allowed zones
            only 3 zones must be retrieved
        """

        # Create group, user
        group013 = Group.objects.create(name='group013') 
        group013.save()
        user013 = User.objects.create(username='user013', default_pref=group013)
        user013.set_password('user013')
        user013.save()
        # Put user in group
        group013.user_set.add(user013) 
        # Create namespace without any permission
        namespace013 = Namespace.objects.create(name='namespace013')
        namespace013.save()
        # Create zones
        zone013_1 = Zone.objects.create(name='zone013-1.example.com',namespace=namespace013, nsmaster='ns1.example.com', mail='hostmaster.example.com')
        zone013_1.save()
        zone013_2 = Zone.objects.create(name='zone013-2.example.com',namespace=namespace013, nsmaster='ns1.example.com', mail='hostmaster.example.com')
        zone013_2.save()
        zone013_3 = Zone.objects.create(name='zone013-3.example.com',namespace=namespace013, nsmaster='ns1.example.com', mail='hostmaster.example.com')
        zone013_3.save()
        # Create zone permission
        zone013perm_1 = PermZone(action='r', group = group013, obj = zone013_1)
        zone013perm_1.save()
        zone013perm_2 = PermZone(action='rw', group = group013, obj = zone013_2)
        zone013perm_2.save()
        zone013perm_3 = PermZone(action='rwc', group = group013, obj = zone013_3)
        zone013perm_3.save()

        # request
        url = f'/zone/'
        self.client.login(username='user013', password='user013')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        number_of_zones = len(response.data)
        self.assertEqual(number_of_zones, 3)

        # Cleanup
        zone013_1.delete()
        zone013_2.delete()
        zone013_3.delete()
        namespace013.delete()

    def test_014_api_zone_delete_allowed_zone(self):
        """ test delete allowed zone
            must be ok
        """
        # Create group, user
        group014 = Group.objects.create(name='group014') 
        group014.save()
        user014 = User.objects.create(username='user014', default_pref=group014)
        user014.set_password('user014')
        user014.save()
        # Put user in group
        group014.user_set.add(user014) 
        # Create namespace without any permission
        namespace014 = Namespace.objects.create(name='namespace014')
        namespace014.save()
        # Create zones
        zone014 = Zone.objects.create(name='zone014.example.com',namespace=namespace014, nsmaster='ns1.example.com', mail='hostmaster.example.com')
        zone014.save()
        # Create zone permission
        zone014perm = PermZone(action='rw', group = group014, obj = zone014)
        zone014perm.save()

        # Request
        url = f'/zone/{zone014.id}/'
        self.client.login(username='user014', password='user014')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Cleanup
        zone014.delete()

    def test_015_api_zone_delete_denied_zone(self):
        """ Test delete allowed zone.
            Must be denied
        """
        # Create group, user
        group015 = Group.objects.create(name='group015') 
        group015.save()
        user015 = User.objects.create(username='user015', default_pref=group015)
        user015.set_password('user015')
        user015.save()
        # Put user in group
        group015.user_set.add(user015) 
        # Create namespace without any permission
        namespace015 = Namespace.objects.create(name='namespace015')
        namespace015.save()
        # Create zones
        zone015 = Zone.objects.create(name='zone015.example.com',namespace=namespace015, nsmaster='ns1.example.com', mail='hostmaster.example.com')
        zone015.save()
        # Create zone read-only permission
        zone015perm = PermZone(action='r', group = group015, obj = zone015)
        zone015perm.save()

        # Request
        url = f'/zone/{zone015.id}/'
        self.client.login(username='user015', password='user015')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Cleanup
        zone015.delete()
        namespace015.delete()

    def test_016_api_zone_update_allowed_zone(self):
        """ test update allowed zone
            Must be ok
        """
        # Create group, user
        group016 = Group.objects.create(name='group016') 
        group016.save()
        user016 = User.objects.create(username='user016', default_pref=group016)
        user016.set_password('user016')
        user016.save()
        # Put user in group
        group016.user_set.add(user016) 
        # Create namespace without any permission
        namespace016 = Namespace.objects.create(name='namespace016')
        namespace016.save()
        # Create zones
        zone016 = Zone.objects.create(name='zone016.example.com', namespace=namespace016, nsmaster='ns1.example.com', mail='hostmaster.example.com')
        zone016.save()
        # Create zone read-write permission
        zone016perm = PermZone(action='rw', group = group016, obj = zone016)
        zone016perm.save()
        # Request
        url = f'/zone/{zone016.id}/'
        self.client.login(username='user016', password='user016')
        #import ipdb; ipdb.set_trace()
        data = {'name': 'zone016updated.example.com', 'namespace': namespace016.id, 'nsmaster': 'ns2.example.com', 'mail': 'hostmaster6.example.com'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Cleanup
        zone016.delete()

    def test_017_api_zone_update_denied_zone(self):
        """ Test update allowed zone
            Must be denied
        """
        # Create group, user
        group017 = Group.objects.create(name='group017') 
        group017.save()
        user017 = User.objects.create(username='user017', default_pref=group017)
        user017.set_password('user017')
        user017.save()
        # Put user in group
        group017.user_set.add(user017) 
        # Create namespace without any permission
        namespace017 = Namespace.objects.create(name='namespace017')
        namespace017.save()
        # Create zones
        zone017 = Zone.objects.create(name='zone017.example.com', namespace=namespace017, nsmaster='ns1.example.com', mail='hostmaster.example.com')
        zone017.save()
        # Add read-only zone permission
        zone017perm = PermZone(action='rc', group = group017, obj = zone017)
        zone017perm.save()

        # Request
        url = f'/zone/{zone017.id}/'
        self.client.login(username='user017', password='user017')
        data = {'name': 'zone017updated.example.com', 'namespace': namespace017.id, 'nsmaster': 'ns2.example.com', 'mail': 'hostmaster6.example.com'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Cleanup
        zone017.delete()
        namespace017.delete()

    def test_018_api_zone_create_denied(self):
        """ test create of a zone in namespace without zone creation permission
            (ie. no permission "c" for group for namespace)
            Must be denied
        """

        # Create group, user
        group018 = Group.objects.create(name='group018') 
        group018.save()
        user018 = User.objects.create(username='user018', default_pref=group018)
        user018.set_password('user018')
        user018.save()
        # Put user in group
        group018.user_set.add(user018) 
        # Create namespace without any permission
        namespace018 = Namespace.objects.create(name='namespace018')
        namespace018.save()
        
        # Request
        url = f'/zone/'
        self.client.login(username='user018', password='user018')
        data = {'name': 'zone018.example.com', 'namespace': namespace018.id, 'nsmaster': 'ns1.example.com', 'mail': 'hostmaster.example.com'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Cleanup
        namespace018.delete()

    def test_019_api_zone_create_allow(self):
        """ create of a zone in namespace
            zone creation permission for namespace is set
            must be ok
        """
        # Create group, user
        group019 = Group.objects.create(name='group019') 
        group019.save()
        user019 = User.objects.create(username='user019', default_pref=group019)
        user019.set_password('user019')
        user019.save()
        # Put user in group
        group019.user_set.add(user019) 
        # Create namespace without any permission
        namespace019 = Namespace.objects.create(name='namespace019')
        namespace019.save()
        # Create zone permission
        namespace019perm = PermNamespace(action = 'rwc', group = group019, obj = namespace019) 
        namespace019perm.save()
        
        # Request
        url = f'/zone/'
        self.client.login(username='user019', password='user019')
        data = {'name': 'zone019.example.com', 'namespace': namespace019.id, 'nsmaster': 'ns1.example.com', 'mail': 'hostmaster.example.com'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Cleanup
        zone019 = Zone.objects.get(name='zone019.example.com')
        zone019.delete()
        namespace019.delete()

