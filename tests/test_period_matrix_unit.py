import unittest
from datetime import date
from types import SimpleNamespace as Obj
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.routes import participants as participant_routes
from backend.routes import periods as period_routes
from services import period_matrix as matrix


class PeriodMatrixTest(unittest.TestCase):
    def test_matrix_batches_data_and_preserves_weighted_costs(self):
        period = Obj(id='period', start_date=date(2024, 1, 1), end_date=None)
        users = [Obj(telegram_id=str(i), telegram_user_name=f'user{i}', full_name=f'Player {i}') for i in range(3)]
        sessions = [Obj(id='session', date=date(2024, 1, 5), venue=Obj(price_per_slot=10), slots=3)]
        roster = [Obj(session=sessions[0], user=users[0], additional_participants=1),
                  Obj(session=sessions[0], user=users[1], additional_participants=0)]
        cost = Obj(id='cost', name='Deposit', total_amount=12)
        cost_roster = [Obj(additional_cost=cost, user=users[1], weight=1),
                       Obj(additional_cost=cost, user=users[2], weight=3)]
        uses = [Obj(batch=Obj(total_price=10, tube_count=3), tubes_used=1)]
        with (
            patch.object(matrix, 'list_sessions_by_period', return_value=sessions) as get_sessions,
            patch.object(matrix, 'list_participants_by_sessions', return_value=roster) as get_roster,
            patch.object(matrix, 'list_uses_by_period', return_value=uses) as get_uses,
            patch.object(matrix, 'list_additional_costs_by_period', return_value=[cost]) as get_costs,
            patch.object(matrix, 'list_participants_by_costs', return_value=cost_roster) as get_cost_roster,
            patch.object(matrix, 'list_users_by_telegram_ids', return_value=users),
            patch('services.calculations.UserService.list_users_by_telegram_ids', return_value=users),
            patch('services.calculations.CalculationService.calculate_period_report', side_effect=AssertionError('Must reuse loaded data')),
        ):
            payload = matrix.build_period_matrix(period)
        for loader in (get_sessions, get_roster, get_uses, get_costs, get_cost_roster):
            loader.assert_called_once()
        amounts = {entry['person_id']: entry['period_money'] for entry in payload['personal_report']}
        self.assertEqual(amounts['0'], 22.22)
        self.assertEqual(amounts['1'], 14.11)
        self.assertAlmostEqual(amounts['2'], 9)
        self.assertEqual(payload['total_period_money'], 45.33)
        self.assertEqual(payload['shuttlecock_total'], 3.33)
        self.assertEqual(payload['participants_by_session']['session'][0]['additional_participants'], 1)
        self.assertEqual(payload['additional_costs'][0]['total_weight'], 4)

    def test_matrix_endpoint_requires_period(self):
        app = FastAPI()
        app.include_router(period_routes.router, prefix='/periods')
        app.dependency_overrides[period_routes.require_admin] = lambda: 'admin'
        with patch.object(period_routes, 'get_period', return_value=None):
            self.assertEqual(TestClient(app).get('/periods/2024-01-01/matrix').status_code, 404)

    def test_plus_edit_preserves_participant_and_rejects_invalid_counts(self):
        app = FastAPI()
        app.include_router(participant_routes.router, prefix='/participants')
        app.dependency_overrides[participant_routes.require_admin] = lambda: 'admin'
        client = TestClient(app)
        participant = Obj(id='p1', user=Obj(telegram_id='u1', telegram_user_name='player'),
                          session=Obj(date=date(2024, 1, 5)), additional_participants=2)
        with patch.object(participant_routes, 'update_participant', return_value=participant) as update:
            response = client.put('/participants/p1', json={'additional_participants': 2})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['id'], 'p1')
            update.assert_called_once_with('p1', additional_participants=2)
            for invalid in (-1, 1.5):
                self.assertEqual(client.put('/participants/p1', json={'additional_participants': invalid}).status_code, 422)
            self.assertEqual(update.call_count, 1)


if __name__ == '__main__':
    unittest.main()
