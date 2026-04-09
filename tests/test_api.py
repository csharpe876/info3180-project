"""
DriftDater - API Test Suite
Run with: python -m pytest tests/ -v
"""

import json
import pytest
from app import app, db
from app.models import User, Profile, Interest
from datetime import date


@pytest.fixture(scope='function')
def client():
    """Create a test client with a fresh in-memory database."""
    import tempfile, os
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)

    app.config['TESTING']                 = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['WTF_CSRF_ENABLED']        = False

    with app.test_client() as client:
        with app.app_context():
            db.drop_all()
            db.create_all()
            _seed_interests()
            yield client
            db.session.remove()
            db.drop_all()
    os.unlink(db_path)


def _seed_interests():
    for name in ['Hiking', 'Gaming', 'Cooking', 'Music', 'Reading']:
        db.session.add(Interest(name=name))
    db.session.commit()


def _register(client, email='test@test.com', username='testuser',
               password='Pass1234', first_name='Test', last_name='User',
               gender='male', dob='2000-01-01'):
    return client.post('/api/v1/auth/register', json={
        'email': email, 'username': username, 'password': password,
        'first_name': first_name, 'last_name': last_name,
        'date_of_birth': dob, 'gender': gender, 'looking_for': 'any',
    })


def _login(client, email='test@test.com', password='Pass1234'):
    return client.post('/api/v1/auth/login', json={
        'email': email, 'password': password,
    })


def auth_header(token):
    return {'Authorization': f'Bearer {token}'}


# ── Auth Tests ────────────────────────────────────────────────────────────────

class TestAuth:
    def test_register_success(self, client):
        r = _register(client)
        assert r.status_code == 201
        data = json.loads(r.data)
        assert 'token' in data
        assert data['user']['username'] == 'testuser'

    def test_register_duplicate_email(self, client):
        _register(client)
        r = _register(client)
        assert r.status_code == 409

    def test_register_underage(self, client):
        r = _register(client, dob='2015-01-01')
        assert r.status_code == 400

    def test_register_missing_fields(self, client):
        r = client.post('/api/v1/auth/register', json={'email': 'x@x.com'})
        assert r.status_code == 400

    def test_login_success(self, client):
        _register(client)
        r = _login(client)
        assert r.status_code == 200
        assert 'token' in json.loads(r.data)

    def test_login_wrong_password(self, client):
        _register(client)
        r = _login(client, password='wrongpass')
        assert r.status_code == 401

    def test_login_unknown_email(self, client):
        r = _login(client, email='nobody@test.com')
        assert r.status_code == 401

    def test_logout(self, client):
        _register(client)
        token = json.loads(_login(client).data)['token']
        r = client.post('/api/v1/auth/logout', headers=auth_header(token))
        assert r.status_code == 200

    def test_protected_route_no_token(self, client):
        r = client.get('/api/v1/profiles')
        assert r.status_code == 401

    def test_protected_route_bad_token(self, client):
        r = client.get('/api/v1/profiles', headers=auth_header('badtoken'))
        assert r.status_code == 401


# ── Profile Tests ─────────────────────────────────────────────────────────────

class TestProfiles:
    def test_get_own_profile(self, client):
        _register(client)
        data = json.loads(_login(client).data)
        token = data['token']
        uid   = data['user']['id']
        r = client.get(f'/api/v1/profiles/{uid}', headers=auth_header(token))
        assert r.status_code == 200
        body = json.loads(r.data)
        assert body['first_name'] == 'Test'

    def test_update_profile(self, client):
        _register(client)
        data  = json.loads(_login(client).data)
        token = data['token']
        uid   = data['user']['id']
        r = client.put(f'/api/v1/profiles/{uid}', json={
            'bio': 'Hello world', 'parish': 'Kingston',
            'interests': ['Hiking', 'Gaming', 'Music'],
        }, headers=auth_header(token))
        assert r.status_code == 200
        body = json.loads(r.data)
        assert body['profile']['bio'] == 'Hello world'
        assert 'Hiking' in body['profile']['interests']

    def test_update_other_profile_forbidden(self, client):
        _register(client)
        _register(client, email='other@test.com', username='other')
        token = json.loads(_login(client).data)['token']
        other_uid = json.loads(_login(client, email='other@test.com').data)['user']['id']
        r = client.put(f'/api/v1/profiles/{other_uid}',
                       json={'bio': 'hack'}, headers=auth_header(token))
        assert r.status_code == 403

    def test_browse_profiles(self, client):
        _register(client)
        _register(client, email='alice@test.com', username='alice',
                  gender='female', first_name='Alice', last_name='W')
        token = json.loads(_login(client).data)['token']
        r = client.get('/api/v1/profiles', headers=auth_header(token))
        assert r.status_code == 200
        body = json.loads(r.data)
        assert body['total'] >= 1

    def test_browse_excludes_own_profile(self, client):
        _register(client)
        token = json.loads(_login(client).data)['token']
        uid   = json.loads(_login(client).data)['user']['id']
        r = client.get('/api/v1/profiles', headers=auth_header(token))
        body = json.loads(r.data)
        user_ids = [p['user_id'] for p in body['profiles']]
        assert uid not in user_ids


# ── Like / Match Tests ────────────────────────────────────────────────────────

class TestLikesAndMatches:
    def _setup_two_users(self, client):
        """Register A and B, return (token_a, uid_a, token_b, uid_b)."""
        _register(client, email='a@t.com', username='userA', gender='male',   first_name='A', last_name='A')
        _register(client, email='b@t.com', username='userB', gender='female', first_name='B', last_name='B')
        r_a = json.loads(_login(client, email='a@t.com').data)
        r_b = json.loads(_login(client, email='b@t.com').data)
        return r_a['token'], r_a['user']['id'], r_b['token'], r_b['user']['id']

    def test_like_creates_no_match_unilaterally(self, client):
        tok_a, uid_a, tok_b, uid_b = self._setup_two_users(client)
        r = client.post(f'/api/v1/profiles/{uid_b}/like',
                        json={'action': 'like'}, headers=auth_header(tok_a))
        assert r.status_code == 200
        body = json.loads(r.data)
        assert body['is_new_match'] is False

    def test_mutual_like_creates_match(self, client):
        tok_a, uid_a, tok_b, uid_b = self._setup_two_users(client)
        client.post(f'/api/v1/profiles/{uid_b}/like',
                    json={'action': 'like'}, headers=auth_header(tok_a))
        r = client.post(f'/api/v1/profiles/{uid_a}/like',
                        json={'action': 'like'}, headers=auth_header(tok_b))
        body = json.loads(r.data)
        assert body['is_new_match'] is True
        assert body['match'] is not None

    def test_pass_does_not_create_match(self, client):
        tok_a, uid_a, tok_b, uid_b = self._setup_two_users(client)
        client.post(f'/api/v1/profiles/{uid_b}/like',
                    json={'action': 'like'}, headers=auth_header(tok_a))
        r = client.post(f'/api/v1/profiles/{uid_a}/like',
                        json={'action': 'pass'}, headers=auth_header(tok_b))
        body = json.loads(r.data)
        assert body['is_new_match'] is False

    def test_get_matches(self, client):
        tok_a, uid_a, tok_b, uid_b = self._setup_two_users(client)
        client.post(f'/api/v1/profiles/{uid_b}/like',
                    json={'action': 'like'}, headers=auth_header(tok_a))
        client.post(f'/api/v1/profiles/{uid_a}/like',
                    json={'action': 'like'}, headers=auth_header(tok_b))
        r = client.get('/api/v1/matches', headers=auth_header(tok_a))
        body = json.loads(r.data)
        assert body['total'] == 1

    def test_cannot_like_self(self, client):
        _register(client)
        data  = json.loads(_login(client).data)
        r = client.post(f'/api/v1/profiles/{data["user"]["id"]}/like',
                        json={'action': 'like'}, headers=auth_header(data['token']))
        assert r.status_code == 400


# ── Messaging Tests ───────────────────────────────────────────────────────────

class TestMessaging:
    def _create_match(self, client):
        _register(client, email='a@t.com', username='userA', first_name='A', last_name='A', gender='male')
        _register(client, email='b@t.com', username='userB', first_name='B', last_name='B', gender='female')
        r_a = json.loads(_login(client, email='a@t.com').data)
        r_b = json.loads(_login(client, email='b@t.com').data)
        tok_a, uid_a = r_a['token'], r_a['user']['id']
        tok_b, uid_b = r_b['token'], r_b['user']['id']
        client.post(f'/api/v1/profiles/{uid_b}/like',
                    json={'action': 'like'}, headers=auth_header(tok_a))
        r = client.post(f'/api/v1/profiles/{uid_a}/like',
                        json={'action': 'like'}, headers=auth_header(tok_b))
        match_id = json.loads(r.data)['match']['id']
        return tok_a, tok_b, match_id

    def test_send_message(self, client):
        tok_a, tok_b, match_id = self._create_match(client)
        r = client.post(f'/api/v1/matches/{match_id}/messages',
                        json={'body': 'Hello!'}, headers=auth_header(tok_a))
        assert r.status_code == 201
        body = json.loads(r.data)
        assert body['message']['body'] == 'Hello!'

    def test_get_messages(self, client):
        tok_a, tok_b, match_id = self._create_match(client)
        client.post(f'/api/v1/matches/{match_id}/messages',
                    json={'body': 'Hi!'}, headers=auth_header(tok_a))
        r = client.get(f'/api/v1/matches/{match_id}/messages',
                       headers=auth_header(tok_b))
        body = json.loads(r.data)
        assert body['total'] == 1

    def test_non_participant_cannot_message(self, client):
        tok_a, tok_b, match_id = self._create_match(client)
        _register(client, email='c@t.com', username='userC', first_name='C', last_name='C')
        tok_c = json.loads(_login(client, email='c@t.com').data)['token']
        r = client.post(f'/api/v1/matches/{match_id}/messages',
                        json={'body': 'Intruder!'}, headers=auth_header(tok_c))
        assert r.status_code == 403

    def test_empty_message_rejected(self, client):
        tok_a, tok_b, match_id = self._create_match(client)
        r = client.post(f'/api/v1/matches/{match_id}/messages',
                        json={'body': '   '}, headers=auth_header(tok_a))
        assert r.status_code == 400

    def test_conversations_list(self, client):
        tok_a, tok_b, match_id = self._create_match(client)
        client.post(f'/api/v1/matches/{match_id}/messages',
                    json={'body': 'Hey!'}, headers=auth_header(tok_a))
        r = client.get('/api/v1/conversations', headers=auth_header(tok_a))
        body = json.loads(r.data)
        assert len(body['conversations']) == 1
        assert body['conversations'][0]['latest_message']['body'] == 'Hey!'


# ── Favourites Tests ──────────────────────────────────────────────────────────

class TestFavourites:
    def test_add_and_get_favourite(self, client):
        _register(client)
        _register(client, email='alice@t.com', username='alice', first_name='Alice', last_name='A')
        tok = json.loads(_login(client).data)['token']
        # Get alice's profile id
        alice_uid  = json.loads(_login(client, email='alice@t.com').data)['user']['id']
        with app.app_context():
            from app.models import Profile as P
            pid = P.query.filter_by(user_id=alice_uid).first().id
        r = client.post(f'/api/v1/favourites/{pid}', headers=auth_header(tok))
        assert r.status_code == 201
        r2 = client.get('/api/v1/favourites', headers=auth_header(tok))
        assert json.loads(r2.data)['total'] == 1

    def test_remove_favourite(self, client):
        _register(client)
        _register(client, email='bob@t.com', username='bob', first_name='Bob', last_name='B')
        tok = json.loads(_login(client).data)['token']
        bob_uid = json.loads(_login(client, email='bob@t.com').data)['user']['id']
        with app.app_context():
            from app.models import Profile as P
            pid = P.query.filter_by(user_id=bob_uid).first().id
        client.post(f'/api/v1/favourites/{pid}', headers=auth_header(tok))
        r = client.delete(f'/api/v1/favourites/{pid}', headers=auth_header(tok))
        assert r.status_code == 200
        r2 = client.get('/api/v1/favourites', headers=auth_header(tok))
        assert json.loads(r2.data)['total'] == 0


# ── Report & Block Tests ──────────────────────────────────────────────────────

class TestReportAndBlock:
    def _two_users(self, client):
        _register(client, email='a@t.com', username='userA', first_name='A', last_name='A')
        _register(client, email='b@t.com', username='userB', first_name='B', last_name='B')
        r_a = json.loads(_login(client, email='a@t.com').data)
        r_b = json.loads(_login(client, email='b@t.com').data)
        return r_a['token'], r_a['user']['id'], r_b['token'], r_b['user']['id']

    def test_report_user(self, client):
        tok_a, uid_a, tok_b, uid_b = self._two_users(client)
        r = client.post(f'/api/v1/users/{uid_b}/report',
                        json={'reason': 'spam', 'details': 'Sending spam'},
                        headers=auth_header(tok_a))
        assert r.status_code == 201

    def test_block_user(self, client):
        tok_a, uid_a, tok_b, uid_b = self._two_users(client)
        r = client.post(f'/api/v1/users/{uid_b}/block', headers=auth_header(tok_a))
        assert r.status_code == 201

    def test_blocked_user_excluded_from_browse(self, client):
        tok_a, uid_a, tok_b, uid_b = self._two_users(client)
        client.post(f'/api/v1/users/{uid_b}/block', headers=auth_header(tok_a))
        r = client.get('/api/v1/profiles', headers=auth_header(tok_a))
        body = json.loads(r.data)
        user_ids = [p['user_id'] for p in body['profiles']]
        assert uid_b not in user_ids

    def test_unblock_user(self, client):
        tok_a, uid_a, tok_b, uid_b = self._two_users(client)
        client.post(f'/api/v1/users/{uid_b}/block', headers=auth_header(tok_a))
        r = client.delete(f'/api/v1/users/{uid_b}/block', headers=auth_header(tok_a))
        assert r.status_code == 200

    def test_cannot_report_self(self, client):
        _register(client)
        data = json.loads(_login(client).data)
        r = client.post(f'/api/v1/users/{data["user"]["id"]}/report',
                        json={'reason': 'spam'}, headers=auth_header(data['token']))
        assert r.status_code == 400


# ── Interests Tests ───────────────────────────────────────────────────────────

class TestInterests:
    def test_get_interests(self, client):
        r = client.get('/api/v1/interests')
        assert r.status_code == 200
        body = json.loads(r.data)
        assert len(body['interests']) == 5
        names = [i['name'] for i in body['interests']]
        assert 'Hiking' in names
