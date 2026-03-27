from mongoengine import DoesNotExist, ValidationError, NotUniqueError
from schemas.venues import Venues
from typing import Optional, List, cast
import logging

logger = logging.getLogger(__name__)


class VenueService:

    @staticmethod
    def create_venue(name: str, location: str, price_per_slot: float) -> Optional[Venues]:
        try:
            existing = VenueService.get_venue_by_name(name)
            if existing:
                logger.warning(f"Venue '{name}' already exists")
                return existing
            venue = Venues(name=name, location=location, price_per_slot=price_per_slot)
            venue.save()
            logger.info(f"Created venue '{name}'")
            return venue
        except NotUniqueError:
            logger.error(f"Venue '{name}' already exists (race condition)")
        except ValidationError as e:
            logger.error(f"Validation error creating venue '{name}': {e}")
        except Exception as e:
            logger.error(f"Failed to create venue '{name}': {e}")
        return None

    @staticmethod
    def get_venue_by_name(name: str) -> Optional[Venues]:
        try:
            return cast(Optional[Venues], Venues.objects.get(name=name))
        except DoesNotExist:
            logger.info(f"Venue '{name}' not found")
        except Exception as e:
            logger.error(f"Error getting venue '{name}': {e}")
        return None

    @staticmethod
    def get_venue_by_id(venue_id: str) -> Optional[Venues]:
        try:
            return cast(Optional[Venues], Venues.objects.get(id=venue_id))
        except DoesNotExist:
            logger.info(f"Venue with id '{venue_id}' not found")
        except Exception as e:
            logger.error(f"Error getting venue by id '{venue_id}': {e}")
        return None

    @staticmethod
    def update_venue(name: str, **kwargs) -> Optional[Venues]:
        try:
            venue = cast(Venues, Venues.objects.get(name=name))
            for field, value in kwargs.items():
                if hasattr(venue, field):
                    setattr(venue, field, value)
                else:
                    logger.warning(f"Field '{field}' not found on Venues")
            venue.save()
            logger.info(f"Updated venue '{name}'")
            return venue
        except DoesNotExist:
            logger.error(f"Venue '{name}' not found for update")
        except ValidationError as e:
            logger.error(f"Validation error updating venue '{name}': {e}")
        except Exception as e:
            logger.error(f"Failed to update venue '{name}': {e}")
        return None

    @staticmethod
    def delete_venue(name: str) -> bool:
        try:
            venue = cast(Venues, Venues.objects.get(name=name))
            venue.delete()
            logger.info(f"Deleted venue '{name}'")
            return True
        except DoesNotExist:
            logger.error(f"Venue '{name}' not found for deletion")
        except Exception as e:
            logger.error(f"Failed to delete venue '{name}': {e}")
        return False

    @staticmethod
    def list_all_venues() -> List[Venues]:
        try:
            return list(Venues.objects.all())  # type: ignore
        except Exception as e:
            logger.error(f"Failed to list venues: {e}")
        return []


def create_venue(name: str, location: str, price_per_slot: float) -> Optional[Venues]:
    return VenueService.create_venue(name, location, price_per_slot)

def get_venue_by_name(name: str) -> Optional[Venues]:
    return VenueService.get_venue_by_name(name)

def get_venue_by_id(venue_id: str) -> Optional[Venues]:
    return VenueService.get_venue_by_id(venue_id)

def update_venue(name: str, **kwargs) -> Optional[Venues]:
    return VenueService.update_venue(name, **kwargs)

def delete_venue(name: str) -> bool:
    return VenueService.delete_venue(name)

def list_all_venues() -> List[Venues]:
    return VenueService.list_all_venues()
