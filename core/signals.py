from django.db.models.signals import post_save, post_delete
from core.models import Rr, Zone
from django.dispatch import receiver

@receiver([post_save, post_delete], sender=Rr)
def increment_serial_rr_mod(sender, instance, **kwargs):
    ''' Receiver for rr creation, modification or delete
    '''
    rr = instance
    print(f"rr id={rr.id} rr name={rr.name}")
    rr.zone.serial += 1

@receiver([post_save], sender=Zone)
def increment_serial_zone_mod(sender, instance, **kwargs):
    ''' Receiver for zone modifications
    '''
    zone = instance
    print(f"zone id={zone.id} zone name={zone.name}")
    zone.serial += 1
