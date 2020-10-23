from django.test import TestCase
from core.models import Namespace, Zone, Rr
from rest_framework.exceptions import ValidationError

import sys
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

class RrModelValidator(TestCase):
    def setUp(self):
        # Allowed namespace
        n = Namespace.objects.create(name='default')
        n.save()
        # Allowed zone
        self.z = Zone.objects.create(name='example.com',namespace=n)
        self.z.save()

    def test_020_start_with_dash(self):
        name = "-bla"
        r = Rr.objects.create(name = name,  zone = self.z ,type="A", a="192.0.9.1")
        try:
            r.full_clean()
        except ValidationError as e: 
            self.assertEqual(e.detail[0] , f"Relative name '{name}' must not start or end with dash or dot")

    def test_021_absolute_end_with_dot(self):
        r = Rr.objects.create(name = "bla.", zone = self.z, type="A", a="192.0.9.1")
        r.full_clean()
        self.assertEqual(r.name, "bla.")

    def test_022_name_contains_two_successive_dots(self):
        name = "bla..truc"
        r = Rr.objects.create(name = name,  zone = self.z ,type="A", a="192.0.9.1")
        try:
            r.full_clean()
        except ValidationError as e: 
            self.assertEqual(e.detail[0] , f"Relative name '{name}' can not contain two successive dots")

    def test_023_name_component_too_long(self):
        c = "a" * 64 
        name = f"{c}.example.com"
        r = Rr.objects.create(name = name,  zone = self.z ,type="A", a="192.0.9.1")
        try:
            r.full_clean()
        except ValidationError as e: 
            self.assertEqual(e.detail[0] , f"Relative name '{name}' is too long (length must be <= 63)")

    def test_024_name_contains_single_arobase(self):
        name = "@"
        r = Rr.objects.create(name = "bla.", zone = self.z, type="A", a="192.0.9.1")
        r.full_clean()
        self.assertEqual(r.name, "@")

    def test_025_name_contains_invalid_char(self):
        name = "?"
        r = Rr.objects.create(name = name,  zone = self.z ,type="A", a="192.0.9.1")
        try:
            r.full_clean()
        except ValidationError as e: 
            self.assertEqual(e.detail[0], f"Relative name must be '@', '*' or an alpha-numeric string")

    def test_025_name_contains_underscore_not_in_initial_position(self):
        name = "ab_"
        r = Rr.objects.create(name = name,  zone = self.z ,type="A", a="192.0.9.1")
        try:
            r.full_clean()
        except ValidationError as e: 
            self.assertEqual(e.detail[0], f"Relative name must be '@', '*' or an alpha-numeric string")

        raise ValidationError(detail=f"Relative name must be '@', '*' or an alpha-numeric string")
        raise ValidationError(detail=f"Absolute name '{name}' is too long (length must be <= 255)")
