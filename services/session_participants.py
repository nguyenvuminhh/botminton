from orms.session_participants import SessionParticipants
from orms.sessions import Sessions
from orms.users import Users
from mongoengine import DoesNotExist, ValidationError, MultipleObjectsReturned, NotUniqueError
from typing import Optional, List, cast
from datetime import date as dt_date
import logging

logger = logging.getLogger(__name__)

class SessionParticipantService:
    """Service class for session participant CRUD operations"""

    @staticmethod
    def create_participant(user_telegram_id: str, session_date: str, additional_participants: int = 0, has_paid: bool = False) -> Optional[SessionParticipants]:
        """Create a new session participant"""
        try:
            # Get user by telegram_id
            user = cast(Users, Users.objects.get(telegram_id=user_telegram_id))
            
            # Get session by date
            session_date_obj = dt_date.fromisoformat(session_date)
            session = cast(Sessions, Sessions.objects.get(date=session_date_obj))
            
            # Check if participant already exists for this session
            existing = SessionParticipantService.get_participant_by_user_and_session(user_telegram_id, session_date)
            if existing:
                logger.warning(f"Participant already exists for user {user_telegram_id} in session {session_date}")
                return existing

            participant = SessionParticipants(
                user=user,
                session=session,
                additional_participants=additional_participants,
                has_paid=has_paid
            )
            participant.save()
            logger.info(f"Created participant for user {user_telegram_id} in session {session_date}")
            return participant

        except DoesNotExist as e:
            logger.error(f"User or session not found: {e}")
            return None
        except ValidationError as e:
            logger.error(f"Validation error creating participant: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to create participant: {e}")
            return None

    @staticmethod
    def get_participant_by_id(participant_id: str) -> Optional[SessionParticipants]:
        """Get a session participant by ID"""
        try:
            participant = cast(SessionParticipants, SessionParticipants.objects.get(id=participant_id))  # type: ignore
            logger.debug(f"Found participant with ID: {participant_id}")
            return participant

        except DoesNotExist:
            logger.info(f"Participant with ID {participant_id} not found")
            return None
        except Exception as e:
            logger.error(f"Error getting participant with ID {participant_id}: {e}")
            return None

    @staticmethod
    def get_participant_by_user_and_session(user_telegram_id: str, session_date: str) -> Optional[SessionParticipants]:
        """Get a session participant by user and session"""
        try:
            user = cast(Users, Users.objects.get(telegram_id=user_telegram_id))
            session_date_obj = dt_date.fromisoformat(session_date)
            session = cast(Sessions, Sessions.objects.get(date=session_date_obj))
            
            participant = cast(SessionParticipants, SessionParticipants.objects.get(user=user, session=session))  # type: ignore
            logger.debug(f"Found participant for user {user_telegram_id} in session {session_date}")
            return participant

        except DoesNotExist:
            logger.info(f"Participant not found for user {user_telegram_id} in session {session_date}")
            return None
        except Exception as e:
            logger.error(f"Error getting participant for user {user_telegram_id} in session {session_date}: {e}")
            return None

    @staticmethod
    def update_participant_by_id(participant_id: str, **kwargs) -> Optional[SessionParticipants]:
        """Update a session participant by ID"""
        try:
            participant = cast(SessionParticipants, SessionParticipants.objects.get(id=participant_id))  # type: ignore
            
            # Update fields
            for field, value in kwargs.items():
                if hasattr(participant, field):
                    setattr(participant, field, value)
                else:
                    logger.warning(f"Field {field} not found in SessionParticipants model")
            
            participant.save()
            logger.info(f"Updated participant with ID: {participant_id}")
            return participant

        except DoesNotExist:
            logger.error(f"Participant with ID {participant_id} not found for update")
            return None
        except ValidationError as e:
            logger.error(f"Validation error updating participant {participant_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to update participant {participant_id}: {e}")
            return None

    @staticmethod
    def update_participant_by_user_and_session(user_telegram_id: str, session_date: str, **kwargs) -> Optional[SessionParticipants]:
        """Update a session participant by user and session"""
        try:
            participant = SessionParticipantService.get_participant_by_user_and_session(user_telegram_id, session_date)
            if not participant:
                logger.error(f"Participant not found for user {user_telegram_id} in session {session_date}")
                return None
            
            return SessionParticipantService.update_participant_by_id(str(participant.id), **kwargs)  # type: ignore

        except Exception as e:
            logger.error(f"Failed to update participant for user {user_telegram_id} in session {session_date}: {e}")
            return None

    @staticmethod
    def delete_participant_by_id(participant_id: str) -> bool:
        """Delete a session participant by ID"""
        try:
            participant = cast(SessionParticipants, SessionParticipants.objects.get(id=participant_id))  # type: ignore
            participant.delete()
            logger.info(f"Deleted participant with ID: {participant_id}")
            return True

        except DoesNotExist:
            logger.error(f"Participant with ID {participant_id} not found for deletion")
            return False
        except Exception as e:
            logger.error(f"Failed to delete participant {participant_id}: {e}")
            return False

    @staticmethod
    def delete_participant_by_user_and_session(user_telegram_id: str, session_date: str) -> bool:
        """Delete a session participant by user and session"""
        try:
            participant = SessionParticipantService.get_participant_by_user_and_session(user_telegram_id, session_date)
            if not participant:
                logger.error(f"Participant not found for user {user_telegram_id} in session {session_date}")
                return False
            
            return SessionParticipantService.delete_participant_by_id(str(participant.id))  # type: ignore

        except Exception as e:
            logger.error(f"Failed to delete participant for user {user_telegram_id} in session {session_date}: {e}")
            return False

    @staticmethod
    def list_participants_by_session(session_date: str) -> List[SessionParticipants]:
        """List all participants for a specific session"""
        try:
            session_date_obj = dt_date.fromisoformat(session_date)
            session = cast(Sessions, Sessions.objects.get(date=session_date_obj))
            
            participants = list(SessionParticipants.objects.filter(session=session))  # type: ignore
            logger.debug(f"Found {len(participants)} participants for session {session_date}")
            return participants

        except DoesNotExist:
            logger.error(f"Session with date {session_date} not found")
            return []
        except Exception as e:
            logger.error(f"Failed to list participants for session {session_date}: {e}")
            return []

    @staticmethod
    def list_participants_by_user(user_telegram_id: str) -> List[SessionParticipants]:
        """List all sessions a user has participated in"""
        try:
            user = cast(Users, Users.objects.get(telegram_id=user_telegram_id))
            
            participants = list(SessionParticipants.objects.filter(user=user))  # type: ignore
            logger.debug(f"Found {len(participants)} session participations for user {user_telegram_id}")
            return participants

        except DoesNotExist:
            logger.error(f"User with telegram_id {user_telegram_id} not found")
            return []
        except Exception as e:
            logger.error(f"Failed to list participations for user {user_telegram_id}: {e}")
            return []

    @staticmethod
    def list_all_participants(limit: int = 100, offset: int = 0) -> List[SessionParticipants]:
        """List all session participants with pagination"""
        try:
            participants = list(SessionParticipants.objects.skip(offset).limit(limit))  # type: ignore
            logger.debug(f"Listed {len(participants)} participants")
            return participants

        except Exception as e:
            logger.error(f"Failed to list all participants: {e}")
            return []

    @staticmethod
    def get_participants_count_by_session(session_date: str) -> int:
        """Get total number of participants (including additional) for a session"""
        try:
            participants = SessionParticipantService.list_participants_by_session(session_date)
            total_count = len(participants)  # Base participants
            additional_count = 0
            for p in participants:
                additional_count += p.additional_participants or 0  # type: ignore
            
            total_participants = total_count + additional_count
            logger.debug(f"Session {session_date} has {total_participants} total participants ({total_count} base + {additional_count} additional)")
            return total_participants

        except Exception as e:
            logger.error(f"Failed to count participants for session {session_date}: {e}")
            return 0

    @staticmethod
    def get_paid_participants_by_session(session_date: str) -> List[SessionParticipants]:
        """Get all participants who have paid for a session"""
        try:
            session_date_obj = dt_date.fromisoformat(session_date)
            session = cast(Sessions, Sessions.objects.get(date=session_date_obj))
            
            paid_participants = list(SessionParticipants.objects.filter(session=session, has_paid=True))  # type: ignore
            logger.debug(f"Found {len(paid_participants)} paid participants for session {session_date}")
            return paid_participants

        except DoesNotExist:
            logger.error(f"Session with date {session_date} not found")
            return []
        except Exception as e:
            logger.error(f"Failed to get paid participants for session {session_date}: {e}")
            return []

    @staticmethod
    def get_unpaid_participants_by_session(session_date: str) -> List[SessionParticipants]:
        """Get all participants who haven't paid for a session"""
        try:
            session_date_obj = dt_date.fromisoformat(session_date)
            session = cast(Sessions, Sessions.objects.get(date=session_date_obj))
            
            unpaid_participants = list(SessionParticipants.objects.filter(session=session, has_paid=False))  # type: ignore
            logger.debug(f"Found {len(unpaid_participants)} unpaid participants for session {session_date}")
            return unpaid_participants

        except DoesNotExist:
            logger.error(f"Session with date {session_date} not found")
            return []
        except Exception as e:
            logger.error(f"Failed to get unpaid participants for session {session_date}: {e}")
            return []

    @staticmethod
    def mark_participant_as_paid(user_telegram_id: str, session_date: str) -> Optional[SessionParticipants]:
        """Mark a participant as paid"""
        try:
            return SessionParticipantService.update_participant_by_user_and_session(
                user_telegram_id, session_date, has_paid=True
            )
        except Exception as e:
            logger.error(f"Failed to mark participant as paid: {e}")
            return None

    @staticmethod
    def mark_participant_as_unpaid(user_telegram_id: str, session_date: str) -> Optional[SessionParticipants]:
        """Mark a participant as unpaid"""
        try:
            return SessionParticipantService.update_participant_by_user_and_session(
                user_telegram_id, session_date, has_paid=False
            )
        except Exception as e:
            logger.error(f"Failed to mark participant as unpaid: {e}")
            return None

    @staticmethod
    def update_additional_participants(user_telegram_id: str, session_date: str, additional_count: int) -> Optional[SessionParticipants]:
        """Update the number of additional participants for a user"""
        try:
            return SessionParticipantService.update_participant_by_user_and_session(
                user_telegram_id, session_date, additional_participants=additional_count
            )
        except Exception as e:
            logger.error(f"Failed to update additional participants: {e}")
            return None

# ------------------------
# ✅ Convenience functions
# ------------------------

def create_participant(user_telegram_id: str, session_date: str, additional_participants: int = 0, has_paid: bool = False) -> Optional[SessionParticipants]:
    """Create a new session participant"""
    return SessionParticipantService.create_participant(user_telegram_id, session_date, additional_participants, has_paid)

def get_participant(participant_id: str) -> Optional[SessionParticipants]:
    """Get a session participant by ID"""
    return SessionParticipantService.get_participant_by_id(participant_id)

def get_participant_by_user_and_session(user_telegram_id: str, session_date: str) -> Optional[SessionParticipants]:
    """Get a session participant by user and session"""
    return SessionParticipantService.get_participant_by_user_and_session(user_telegram_id, session_date)

def update_participant(participant_id: str, **kwargs) -> Optional[SessionParticipants]:
    """Update a session participant by ID"""
    return SessionParticipantService.update_participant_by_id(participant_id, **kwargs)

def update_participant_by_user_and_session(user_telegram_id: str, session_date: str, **kwargs) -> Optional[SessionParticipants]:
    """Update a session participant by user and session"""
    return SessionParticipantService.update_participant_by_user_and_session(user_telegram_id, session_date, **kwargs)

def delete_participant(participant_id: str) -> bool:
    """Delete a session participant by ID"""
    return SessionParticipantService.delete_participant_by_id(participant_id)

def delete_participant_by_user_and_session(user_telegram_id: str, session_date: str) -> bool:
    """Delete a session participant by user and session"""
    return SessionParticipantService.delete_participant_by_user_and_session(user_telegram_id, session_date)

def list_session_participants(session_date: str) -> List[SessionParticipants]:
    """List all participants for a specific session"""
    return SessionParticipantService.list_participants_by_session(session_date)

def list_user_participations(user_telegram_id: str) -> List[SessionParticipants]:
    """List all sessions a user has participated in"""
    return SessionParticipantService.list_participants_by_user(user_telegram_id)

def list_all_participants(limit: int = 100, offset: int = 0) -> List[SessionParticipants]:
    """List all session participants with pagination"""
    return SessionParticipantService.list_all_participants(limit, offset)

def get_session_participant_count(session_date: str) -> int:
    """Get total number of participants (including additional) for a session"""
    return SessionParticipantService.get_participants_count_by_session(session_date)

def get_paid_participants(session_date: str) -> List[SessionParticipants]:
    """Get all participants who have paid for a session"""
    return SessionParticipantService.get_paid_participants_by_session(session_date)

def get_unpaid_participants(session_date: str) -> List[SessionParticipants]:
    """Get all participants who haven't paid for a session"""
    return SessionParticipantService.get_unpaid_participants_by_session(session_date)

def mark_as_paid(user_telegram_id: str, session_date: str) -> Optional[SessionParticipants]:
    """Mark a participant as paid"""
    return SessionParticipantService.mark_participant_as_paid(user_telegram_id, session_date)

def mark_as_unpaid(user_telegram_id: str, session_date: str) -> Optional[SessionParticipants]:
    """Mark a participant as unpaid"""
    return SessionParticipantService.mark_participant_as_unpaid(user_telegram_id, session_date)

def update_additional_participants(user_telegram_id: str, session_date: str, additional_count: int) -> Optional[SessionParticipants]:
    """Update the number of additional participants for a user"""
    return SessionParticipantService.update_additional_participants(user_telegram_id, session_date, additional_count)
