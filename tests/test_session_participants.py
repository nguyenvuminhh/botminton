import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.session_participants import (
    SessionParticipantService, create_participant, get_participant, 
    get_participant_by_user_and_session, update_participant, 
    update_participant_by_user_and_session, delete_participant, 
    delete_participant_by_user_and_session, list_session_participants, 
    list_user_participations, list_all_participants, get_session_participant_count,
    get_paid_participants, get_unpaid_participants, mark_as_paid, mark_as_unpaid,
    update_additional_participants
)
from services.users import create_user, delete_user
from services.sessions import create_session, delete_session
from services.periods import create_period, delete_period
from utils.database import db_manager
from datetime import date as dt_date, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_test_data():
    """Create test users, period, and sessions for testing"""
    try:
        # Create test users
        user1 = create_user(
            telegram_id="test_user_1",
            telegram_user_name="testuser1",
            is_admin=False
        )
        
        user2 = create_user(
            telegram_id="test_user_2", 
            telegram_user_name="testuser2",
            is_admin=True
        )
        
        # Create test period
        today = dt_date.today()
        period_start_date = today.isoformat()
        test_period = create_period(
            start_date=period_start_date,
            end_date=None,
            total_money=1000
        )
        
        # Create test sessions
        tomorrow = today + timedelta(days=1)
        day_after = today + timedelta(days=2)
        
        session1 = create_session(
            date=today.isoformat(),
            period_id=period_start_date,
            courts_price=25.0,
            telegram_poll_message_id="test_poll_1"
        )
        
        session2 = create_session(
            date=tomorrow.isoformat(),
            period_id=period_start_date,
            courts_price=30.0,
            telegram_poll_message_id="test_poll_2"
        )
        
        session3 = create_session(
            date=day_after.isoformat(),
            period_id=period_start_date,
            courts_price=35.0,
            telegram_poll_message_id="test_poll_3"
        )
        
        if all([user1, user2, test_period, session1, session2, session3]):
            return {
                "users": ["test_user_1", "test_user_2"],
                "sessions": [today.isoformat(), tomorrow.isoformat(), day_after.isoformat()],
                "period": period_start_date
            }
        else:
            logger.error("Failed to create test data")
            return None
            
    except Exception as e:
        logger.error(f"Failed to setup test data: {e}")
        return None

def cleanup_test_data(test_data):
    """Clean up test data after testing"""
    if not test_data:
        return
        
    try:
        # Delete test users
        for user_id in test_data["users"]:
            delete_user(user_id)
            
        # Delete test sessions
        for session_date in test_data["sessions"]:
            delete_session(session_date)
            
        # Delete test period
        delete_period(test_data["period"])
        
        logger.info("Cleaned up test data")
        
    except Exception as e:
        logger.error(f"Failed to cleanup test data: {e}")

def test_session_participants_crud():
    """Test all CRUD operations for SessionParticipants model"""
    test_data = None
    try:
        # Connect to database
        db_manager.connect()
        logger.info("✅ Connected to database")
        
        # Setup test data
        test_data = setup_test_data()
        if not test_data:
            print("❌ Failed to setup test data")
            return
        
        user_ids = test_data["users"]
        session_dates = test_data["sessions"]
        participant_ids = []
        
        print("\n🧪 Testing SessionParticipants CRUD Operations")
        print("=" * 60)
        
        # 1. CREATE PARTICIPANTS
        print("\n1️⃣ Creating session participants...")
        
        # User1 participates in session 1 with 2 additional participants
        participant1 = create_participant(
            user_telegram_id=user_ids[0],
            session_date=session_dates[0],
            additional_participants=2,
            has_paid=False
        )
        
        # User2 participates in session 1 with no additional participants, already paid
        participant2 = create_participant(
            user_telegram_id=user_ids[1],
            session_date=session_dates[0],
            additional_participants=0,
            has_paid=True
        )
        
        # User1 participates in session 2
        participant3 = create_participant(
            user_telegram_id=user_ids[0],
            session_date=session_dates[1],
            additional_participants=1,
            has_paid=False
        )
        
        if participant1:
            participant_ids.append(str(participant1.id))  # type: ignore
            print(f"✅ Created participant1: User {user_ids[0]} in session {session_dates[0]}")
            print(f"   Additional participants: {participant1.additional_participants}, Paid: {participant1.has_paid}")
            # Assert participant1 values match expected
            assert participant1.user.telegram_id == user_ids[0], f"Expected user {user_ids[0]}, got {participant1.user.telegram_id}"  # type: ignore
            assert str(participant1.session.date) == session_dates[0], f"Expected session {session_dates[0]}, got {participant1.session.date}"  # type: ignore
            assert participant1.additional_participants == 2, f"Expected additional_participants 2, got {participant1.additional_participants}"
            assert participant1.has_paid == False, f"Expected has_paid False, got {participant1.has_paid}"
        else:
            assert False, "Failed to create participant1"
            
        if participant2:
            participant_ids.append(str(participant2.id))  # type: ignore
            print(f"✅ Created participant2: User {user_ids[1]} in session {session_dates[0]}")
            print(f"   Additional participants: {participant2.additional_participants}, Paid: {participant2.has_paid}")
            # Assert participant2 values match expected
            assert participant2.user.telegram_id == user_ids[1], f"Expected user {user_ids[1]}, got {participant2.user.telegram_id}"  # type: ignore
            assert str(participant2.session.date) == session_dates[0], f"Expected session {session_dates[0]}, got {participant2.session.date}"  # type: ignore
            assert participant2.additional_participants == 0, f"Expected additional_participants 0, got {participant2.additional_participants}"
            assert participant2.has_paid == True, f"Expected has_paid True, got {participant2.has_paid}"
        else:
            assert False, "Failed to create participant2"
            
        if participant3:
            participant_ids.append(str(participant3.id))  # type: ignore
            print(f"✅ Created participant3: User {user_ids[0]} in session {session_dates[1]}")
            # Assert participant3 values match expected
            assert participant3.user.telegram_id == user_ids[0], f"Expected user {user_ids[0]}, got {participant3.user.telegram_id}"  # type: ignore
            assert str(participant3.session.date) == session_dates[1], f"Expected session {session_dates[1]}, got {participant3.session.date}"  # type: ignore
            assert participant3.additional_participants == 1, f"Expected additional_participants 1, got {participant3.additional_participants}"
            assert participant3.has_paid == False, f"Expected has_paid False, got {participant3.has_paid}"
        else:
            assert False, "Failed to create participant3"
        
        # 2. GET PARTICIPANT BY ID
        print("\n2️⃣ Getting participant by ID...")
        if participant_ids:
            retrieved_participant = get_participant(participant_ids[0])
            
            if retrieved_participant:
                print(f"✅ Retrieved participant: {retrieved_participant.user.telegram_id} in session {retrieved_participant.session.date}")  # type: ignore
                print(f"   Additional: {retrieved_participant.additional_participants}, Paid: {retrieved_participant.has_paid}")
                # Assert retrieved values match expected
                assert retrieved_participant.user.telegram_id == user_ids[0], f"Expected user {user_ids[0]}, got {retrieved_participant.user.telegram_id}"  # type: ignore
                assert str(retrieved_participant.session.date) == session_dates[0], f"Expected session {session_dates[0]}, got {retrieved_participant.session.date}"  # type: ignore
                assert retrieved_participant.additional_participants == 2, f"Expected additional_participants 2, got {retrieved_participant.additional_participants}"
                assert retrieved_participant.has_paid == False, f"Expected has_paid False, got {retrieved_participant.has_paid}"
            else:
                assert False, "Participant not found when it should exist"
        
        # 3. GET PARTICIPANT BY USER AND SESSION
        print("\n3️⃣ Getting participant by user and session...")
        retrieved_by_user_session = get_participant_by_user_and_session(user_ids[1], session_dates[0])
        
        if retrieved_by_user_session:
            print(f"✅ Retrieved participant: {retrieved_by_user_session.user.telegram_id} in session {retrieved_by_user_session.session.date}")  # type: ignore
            # Assert retrieved values match expected
            assert retrieved_by_user_session.user.telegram_id == user_ids[1], f"Expected user {user_ids[1]}, got {retrieved_by_user_session.user.telegram_id}"  # type: ignore
            assert str(retrieved_by_user_session.session.date) == session_dates[0], f"Expected session {session_dates[0]}, got {retrieved_by_user_session.session.date}"  # type: ignore
            assert retrieved_by_user_session.has_paid == True, f"Expected has_paid True, got {retrieved_by_user_session.has_paid}"
        else:
            assert False, "Participant not found when it should exist"
        
        # 4. UPDATE PARTICIPANT BY ID
        print("\n4️⃣ Updating participant by ID...")
        if participant_ids:
            updated_participant = update_participant(
                participant_ids[0],
                additional_participants=3,
                has_paid=True
            )
            
            if updated_participant:
                print(f"✅ Updated participant: Additional={updated_participant.additional_participants}, Paid={updated_participant.has_paid}")
                # Assert updated values match expected
                assert updated_participant.additional_participants == 3, f"Expected additional_participants 3, got {updated_participant.additional_participants}"
                assert updated_participant.has_paid == True, f"Expected has_paid True, got {updated_participant.has_paid}"
            else:
                assert False, "Failed to update participant"
        
        # 5. UPDATE PARTICIPANT BY USER AND SESSION
        print("\n5️⃣ Updating participant by user and session...")
        updated_by_user_session = update_participant_by_user_and_session(
            user_ids[0], session_dates[1],
            additional_participants=5
        )
        
        if updated_by_user_session:
            print(f"✅ Updated participant: Additional={updated_by_user_session.additional_participants}")
            # Assert updated values match expected
            assert updated_by_user_session.additional_participants == 5, f"Expected additional_participants 5, got {updated_by_user_session.additional_participants}"
            assert updated_by_user_session.user.telegram_id == user_ids[0], f"Expected user {user_ids[0]}, got {updated_by_user_session.user.telegram_id}"  # type: ignore
        else:
            assert False, "Failed to update participant by user and session"
        
        # 6. LIST PARTICIPANTS BY SESSION
        print("\n6️⃣ Listing participants by session...")
        session1_participants = list_session_participants(session_dates[0])
        session2_participants = list_session_participants(session_dates[1])
        
        print(f"✅ Session {session_dates[0]} has {len(session1_participants)} participants:")
        # Assert we have the expected number of participants for session 1
        assert len(session1_participants) == 2, f"Expected 2 participants for session 1, got {len(session1_participants)}"
        
        for p in session1_participants:
            print(f"   - User {p.user.telegram_id}: +{p.additional_participants} additional, Paid: {p.has_paid}")  # type: ignore
            # Assert each participant belongs to the correct session
            assert str(p.session.date) == session_dates[0], f"Expected session {session_dates[0]}, got {p.session.date}"  # type: ignore
        
        print(f"✅ Session {session_dates[1]} has {len(session2_participants)} participants:")
        # Assert we have the expected number of participants for session 2
        assert len(session2_participants) == 1, f"Expected 1 participant for session 2, got {len(session2_participants)}"
        
        for p in session2_participants:
            print(f"   - User {p.user.telegram_id}: +{p.additional_participants} additional")  # type: ignore
            # Assert participant belongs to the correct session
            assert str(p.session.date) == session_dates[1], f"Expected session {session_dates[1]}, got {p.session.date}"  # type: ignore
        
        # 7. LIST PARTICIPANTS BY USER
        print("\n7️⃣ Listing participants by user...")
        user1_participations = list_user_participations(user_ids[0])
        user2_participations = list_user_participations(user_ids[1])
        
        print(f"✅ User {user_ids[0]} has {len(user1_participations)} participations:")
        # Assert user1 has 2 participations
        assert len(user1_participations) == 2, f"Expected 2 participations for user1, got {len(user1_participations)}"
        
        for p in user1_participations:
            print(f"   - Session {p.session.date}: +{p.additional_participants} additional")  # type: ignore
            # Assert each participation belongs to the correct user
            assert p.user.telegram_id == user_ids[0], f"Expected user {user_ids[0]}, got {p.user.telegram_id}"  # type: ignore
        
        print(f"✅ User {user_ids[1]} has {len(user2_participations)} participations:")
        # Assert user2 has 1 participation
        assert len(user2_participations) == 1, f"Expected 1 participation for user2, got {len(user2_participations)}"
        
        # 8. GET SESSION PARTICIPANT COUNT
        print("\n8️⃣ Getting session participant count...")
        session1_count = get_session_participant_count(session_dates[0])
        session2_count = get_session_participant_count(session_dates[1])
        
        print(f"✅ Session {session_dates[0]} total participants: {session1_count}")
        print(f"✅ Session {session_dates[1]} total participants: {session2_count}")
        
        # Assert counts match expected (base participants + additional)
        # Session 1: 2 base + 3 (user1) + 0 (user2) = 5 total
        expected_session1_count = 2 + 3 + 0
        assert session1_count == expected_session1_count, f"Expected {expected_session1_count} total participants for session 1, got {session1_count}"
        
        # Session 2: 1 base + 5 (user1) = 6 total
        expected_session2_count = 1 + 5
        assert session2_count == expected_session2_count, f"Expected {expected_session2_count} total participants for session 2, got {session2_count}"
        
        # 9. GET PAID AND UNPAID PARTICIPANTS
        print("\n9️⃣ Getting paid and unpaid participants...")
        paid_participants = get_paid_participants(session_dates[0])
        unpaid_participants = get_unpaid_participants(session_dates[0])
        
        print(f"✅ Paid participants in session {session_dates[0]}: {len(paid_participants)}")
        print(f"✅ Unpaid participants in session {session_dates[0]}: {len(unpaid_participants)}")
        
        # Assert we have the expected counts
        # After updates: participant1 (user1) is now paid, participant2 (user2) was already paid
        assert len(paid_participants) == 2, f"Expected 2 paid participants, got {len(paid_participants)}"
        assert len(unpaid_participants) == 0, f"Expected 0 unpaid participants, got {len(unpaid_participants)}"
        
        for p in paid_participants:
            print(f"   - Paid: User {p.user.telegram_id}")  # type: ignore
            assert p.has_paid == True, f"Expected has_paid True for paid participant, got {p.has_paid}"
        
        # 10. MARK AS PAID/UNPAID
        print("\n🔟 Testing mark as paid/unpaid...")
        
        # Mark user1 in session2 as paid
        marked_paid = mark_as_paid(user_ids[0], session_dates[1])
        if marked_paid:
            print(f"✅ Marked user {user_ids[0]} as paid for session {session_dates[1]}")
            assert marked_paid.has_paid == True, f"Expected has_paid True after marking as paid, got {marked_paid.has_paid}"
        else:
            assert False, "Failed to mark participant as paid"
        
        # Mark user2 in session1 as unpaid
        marked_unpaid = mark_as_unpaid(user_ids[1], session_dates[0])
        if marked_unpaid:
            print(f"✅ Marked user {user_ids[1]} as unpaid for session {session_dates[0]}")
            assert marked_unpaid.has_paid == False, f"Expected has_paid False after marking as unpaid, got {marked_unpaid.has_paid}"
        else:
            assert False, "Failed to mark participant as unpaid"
        
        # 11. UPDATE ADDITIONAL PARTICIPANTS
        print("\n1️⃣1️⃣ Testing update additional participants...")
        updated_additional = update_additional_participants(user_ids[1], session_dates[0], 10)
        
        if updated_additional:
            print(f"✅ Updated additional participants for user {user_ids[1]}: {updated_additional.additional_participants}")
            assert updated_additional.additional_participants == 10, f"Expected additional_participants 10, got {updated_additional.additional_participants}"
        else:
            assert False, "Failed to update additional participants"
        
        # 12. TEST DUPLICATE PARTICIPANT CREATION
        print("\n1️⃣2️⃣ Testing duplicate participant creation...")
        duplicate_participant = create_participant(
            user_telegram_id=user_ids[0],
            session_date=session_dates[0],  # Same user and session as participant1
            additional_participants=999,
            has_paid=False
        )
        
        if duplicate_participant:
            print(f"ℹ️  Duplicate handled - returned existing participant")
            print(f"   Original values preserved: Additional={duplicate_participant.additional_participants}")
            # Assert duplicate returns the existing participant with original values
            assert duplicate_participant.user.telegram_id == user_ids[0], f"Expected user {user_ids[0]}, got {duplicate_participant.user.telegram_id}"  # type: ignore
            assert str(duplicate_participant.session.date) == session_dates[0], f"Expected session {session_dates[0]}, got {duplicate_participant.session.date}"  # type: ignore
            # Should have the updated value from step 4, not the new value 999
            assert duplicate_participant.additional_participants == 3, f"Expected original additional_participants 3, got {duplicate_participant.additional_participants}"
        else:
            print("ℹ️  Duplicate creation returned None (also acceptable)")
        
        # 13. TEST NON-EXISTENT OPERATIONS
        print("\n1️⃣3️⃣ Testing non-existent participant operations...")
        
        # Get non-existent participant by ID
        non_existent = get_participant("non_existent_id_123")
        assert non_existent is None, f"Expected None for non-existent participant, got {non_existent}"
        if non_existent is None:
            print("✅ Non-existent participant get properly handled")
        
        # Get non-existent participant by user and session
        non_existent_user_session = get_participant_by_user_and_session("non_existent_user", session_dates[0])
        assert non_existent_user_session is None, f"Expected None for non-existent user, got {non_existent_user_session}"
        if non_existent_user_session is None:
            print("✅ Non-existent user participant get properly handled")
        
        # Update non-existent participant
        non_existent_update = update_participant("non_existent_id_123", has_paid=True)
        assert non_existent_update is None, f"Expected None for non-existent participant update, got {non_existent_update}"
        if non_existent_update is None:
            print("✅ Non-existent participant update properly handled")
        
        # Delete non-existent participant
        non_existent_delete = delete_participant("non_existent_id_123")
        assert non_existent_delete is False, f"Expected False for non-existent participant delete, got {non_existent_delete}"
        if not non_existent_delete:
            print("✅ Non-existent participant delete properly handled")
        
        # 14. DELETE PARTICIPANTS
        print("\n1️⃣4️⃣ Deleting participants...")
        
        # Delete by ID
        deleted_by_id = delete_participant(participant_ids[0])
        assert deleted_by_id is True, f"Expected True for participant deletion by ID, got {deleted_by_id}"
        if deleted_by_id:
            print(f"✅ Deleted participant by ID: {participant_ids[0]}")
        
        # Delete by user and session
        deleted_by_user_session = delete_participant_by_user_and_session(user_ids[1], session_dates[0])
        assert deleted_by_user_session is True, f"Expected True for participant deletion by user/session, got {deleted_by_user_session}"
        if deleted_by_user_session:
            print(f"✅ Deleted participant: User {user_ids[1]} from session {session_dates[0]}")
        
        # Verify deletions
        print("\n🔍 Verifying participant deletion...")
        deleted_check1 = get_participant(participant_ids[0])
        deleted_check2 = get_participant_by_user_and_session(user_ids[1], session_dates[0])
        
        assert deleted_check1 is None, f"Expected None for deleted participant1, got {deleted_check1}"
        assert deleted_check2 is None, f"Expected None for deleted participant2, got {deleted_check2}"
        
        if deleted_check1 is None and deleted_check2 is None:
            print("✅ Participant deletions confirmed")
        
        # Clean up remaining participant
        remaining_participant = get_participant_by_user_and_session(user_ids[0], session_dates[1])
        if remaining_participant:
            delete_result = delete_participant(str(remaining_participant.id))  # type: ignore
            assert delete_result is True, f"Expected True for cleanup deletion, got {delete_result}"
            print("✅ Cleaned up remaining test participant")
        
        print("\n🎉 All SessionParticipants CRUD operations completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"❌ Test failed: {e}")
    
    finally:
        # Cleanup test data
        try:
            if 'test_data' in locals() and test_data:
                cleanup_test_data(test_data)
        except:
            pass
        
        # Disconnect from database
        db_manager.disconnect()
        logger.info("✅ Disconnected from database")

def test_session_participants_edge_cases():
    """Test edge cases and error conditions"""
    test_data = None
    try:
        db_manager.connect()
        logger.info("✅ Connected to database for edge cases")
        
        print("\n🧪 Testing SessionParticipants Edge Cases")
        print("=" * 50)
        
        # Setup minimal test data
        test_data = setup_test_data()
        if not test_data:
            print("❌ Failed to setup test data for edge cases")
            return
        
        user_ids = test_data["users"]
        session_dates = test_data["sessions"]
        
        # Test invalid user/session combinations
        print("\n1️⃣ Testing invalid user/session combinations...")
        
        # Create participant with non-existent user
        invalid_user_participant = create_participant(
            user_telegram_id="non_existent_user_999",
            session_date=session_dates[0],
            additional_participants=1,
            has_paid=False
        )
        
        assert invalid_user_participant is None, f"Expected None for invalid user, got {invalid_user_participant}"
        if invalid_user_participant is None:
            print("✅ Invalid user creation properly handled")
        
        # Create participant with non-existent session
        invalid_session_participant = create_participant(
            user_telegram_id=user_ids[0],
            session_date="2099-12-31",  # Non-existent session
            additional_participants=1,
            has_paid=False
        )
        
        assert invalid_session_participant is None, f"Expected None for invalid session, got {invalid_session_participant}"
        if invalid_session_participant is None:
            print("✅ Invalid session creation properly handled")
        
        # Test edge case values
        print("\n2️⃣ Testing edge case values...")
        
        # Create participant with large additional_participants
        edge_participant = create_participant(
            user_telegram_id=user_ids[0],
            session_date=session_dates[0],
            additional_participants=999,
            has_paid=True
        )
        
        if edge_participant:
            print(f"✅ Created participant with large additional count: {edge_participant.additional_participants}")
            assert edge_participant.additional_participants == 999, f"Expected additional_participants 999, got {edge_participant.additional_participants}"
            assert edge_participant.has_paid == True, f"Expected has_paid True, got {edge_participant.has_paid}"
            
            # Clean up edge case participant
            delete_result = delete_participant(str(edge_participant.id))  # type: ignore
            assert delete_result is True, f"Expected True for edge case cleanup, got {delete_result}"
        
        # Test list operations with empty results
        print("\n3️⃣ Testing empty list operations...")
        
        # List participants for session with no participants
        empty_session_participants = list_session_participants(session_dates[2])  # session3 has no participants
        assert len(empty_session_participants) == 0, f"Expected 0 participants for empty session, got {len(empty_session_participants)}"
        if len(empty_session_participants) == 0:
            print("✅ Empty session participants list properly handled")
        
        # Get count for session with no participants
        empty_session_count = get_session_participant_count(session_dates[2])
        assert empty_session_count == 0, f"Expected 0 count for empty session, got {empty_session_count}"
        if empty_session_count == 0:
            print("✅ Empty session count properly handled")
        
        print("\n🎉 Edge cases testing completed!")
        
    except Exception as e:
        logger.error(f"Edge cases test failed: {e}")
        print(f"❌ Edge cases test failed: {e}")
    
    finally:
        # Cleanup test data
        try:
            if test_data:
                cleanup_test_data(test_data)
        except:
            pass
        
        db_manager.disconnect()
        logger.info("✅ Disconnected from database")

if __name__ == "__main__":
    # Run main CRUD tests
    test_session_participants_crud()
    
    # Run edge cases tests
    test_session_participants_edge_cases()
