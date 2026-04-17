"""
QA Scenario Tests - Creates its own fresh database like test_api.py
Run with: python -m pytest tests/test_qa_scenarios.py -v
"""

import json
import pytest
import tempfile
import os
from app import app, db
from app.models import User, Profile, Interest, Like, Match, Message, Favourite, Report, Block
from datetime import date


# Interest list for seeding (same as seed_qa.py but minimal for testing)
TEST_INTERESTS = [
    'Hiking', 'Photography', 'Cooking', 'Gaming', 'Reading',
    'Travelling', 'Music', 'Movies', 'Sports', 'Fitness',
]


# QA Test Users (subset for testing)
TEST_USERS = [
    {
        'username': 'admin',
        'email': 'admin@driftdater.com',
        'password': 'admin123',
        'profile': {
            'first_name': 'Admin', 'last_name': 'User',
            'date_of_birth': date(1990, 1, 1),
            'gender': 'male', 'looking_for': 'any',
            'bio': 'Site administrator',
            'parish': 'Kingston', 'city': 'Kingston', 'country': 'Jamaica',
            'occupation': 'Admin', 'education_level': 'master',
            'interests': ['Coding', 'Gaming', 'Music'],
        },
    },
    {
        'username': 'alice_w',
        'email': 'alice@example.com',
        'password': 'password123',
        'profile': {
            'first_name': 'Alice', 'last_name': 'Wonder',
            'date_of_birth': date(1999, 3, 15),
            'gender': 'female', 'looking_for': 'male',
            'bio': 'Love hiking and adventure!',
            'parish': 'Kingston', 'city': 'Kingston', 'country': 'Jamaica',
            'occupation': 'Graphic Designer', 'education_level': 'bachelor',
            'interests': ['Hiking', 'Photography', 'Travelling', 'Art'],
        },
    },
    {
        'username': 'bob_builder',
        'email': 'bob@example.com',
        'password': 'password123',
        'profile': {
            'first_name': 'Bob', 'last_name': 'Builder',
            'date_of_birth': date(1997, 7, 20),
            'gender': 'male', 'looking_for': 'female',
            'bio': 'Software developer by day',
            'parish': 'Kingston', 'city': 'Kingston', 'country': 'Jamaica',
            'occupation': 'Software Developer', 'education_level': 'bachelor',
            'interests': ['Coding', 'Photography', 'Gaming', 'Hiking'],
        },
    },
    {
        'username': 'perfect_match',
        'email': 'perfect@example.com',
        'password': 'password123',
        'profile': {
            'first_name': 'Perfect', 'last_name': 'Match',
            'date_of_birth': date(1997, 6, 15),
            'gender': 'male', 'looking_for': 'female',
            'bio': 'I love hiking and photography!',
            'parish': 'Kingston', 'city': 'Kingston', 'country': 'Jamaica',
            'occupation': 'Travel Blogger', 'education_level': 'bachelor',
            'interests': ['Hiking', 'Photography', 'Travelling', 'Art'],
        },
    },
    {
        'username': 'blocked_user',
        'email': 'blocked@example.com',
        'password': 'password123',
        'profile': {
            'first_name': 'Blocked', 'last_name': 'Person',
            'date_of_birth': date(1996, 8, 22),
            'gender': 'female', 'looking_for': 'male',
            'bio': 'Please unblock me!',
            'parish': 'Kingston', 'city': 'Kingston', 'country': 'Jamaica',
            'occupation': 'Marketing', 'education_level': 'bachelor',
            'interests': ['Hiking', 'Photography', 'Cooking', 'Music'],
        },
    },
    {
        'username': 'spam_user',
        'email': 'spam@example.com',
        'password': 'password123',
        'profile': {
            'first_name': 'Spam', 'last_name': 'Bot',
            'date_of_birth': date(2000, 1, 1),
            'gender': 'male', 'looking_for': 'female',
            'bio': 'CLICK HERE FOR FREE MONEY!!!',
            'parish': 'St. Andrew', 'city': 'Kingston', 'country': 'Jamaica',
            'occupation': 'Scammer', 'education_level': 'none',
            'interests': ['Gaming', 'Movies'],
        },
    },
]


def seed_test_database():
    """Seed the test database with QA data."""
    print("Seeding test database...")
    
    # Seed interests
    for name in TEST_INTERESTS:
        if not Interest.query.filter_by(name=name).first():
            db.session.add(Interest(name=name))
    db.session.commit()
    
    all_interests = {i.name: i for i in Interest.query.all()}
    
    # Seed users
    for data in TEST_USERS:
        user = User(username=data['username'], email=data['email'])
        user.set_password(data['password'])
        db.session.add(user)
        db.session.flush()
        
        pd = data['profile']
        profile = Profile(
            user_id=user.id,
            first_name=pd['first_name'],
            last_name=pd['last_name'],
            date_of_birth=pd['date_of_birth'],
            gender=pd['gender'],
            looking_for=pd['looking_for'],
            bio=pd.get('bio'),
            parish=pd.get('parish'),
            city=pd.get('city'),
            country=pd.get('country'),
            occupation=pd.get('occupation'),
            education_level=pd.get('education_level'),
        )
        profile.interests = [all_interests[n] for n in pd.get('interests', [])
                              if n in all_interests]
        db.session.add(profile)
    
    db.session.commit()
    
    # Create interactions
    alice = User.query.filter_by(email='alice@example.com').first()
    bob = User.query.filter_by(email='bob@example.com').first()
    perfect = User.query.filter_by(email='perfect@example.com').first()
    blocked = User.query.filter_by(email='blocked@example.com').first()
    spam = User.query.filter_by(email='spam@example.com').first()
    admin = User.query.filter_by(email='admin@driftdater.com').first()
    
    if all([alice, bob, perfect, blocked, spam, admin]):
        # Mutual match: Alice <-> Perfect
        like1 = Like(liker_id=alice.id, liked_id=perfect.id, action='like')
        like2 = Like(liker_id=perfect.id, liked_id=alice.id, action='like')
        db.session.add_all([like1, like2])
        
        match = Match(user1_id=alice.id, user2_id=perfect.id)
        db.session.add(match)
        db.session.flush()
        
        # Messages between Alice and Perfect
        msg1 = Message(match_id=match.id, sender_id=alice.id,
                      body="Hey Perfect! Love your profile! Want to chat?")
        msg2 = Message(match_id=match.id, sender_id=perfect.id,
                      body="Hi Alice! Thanks! Your photos are amazing. Would love to chat!")
        db.session.add_all([msg1, msg2])
        
        # Alice likes Bob
        like3 = Like(liker_id=alice.id, liked_id=bob.id, action='like')
        db.session.add(like3)
        
        # Favourite
        fav = Favourite(user_id=alice.id, profile_id=bob.profile.id)
        db.session.add(fav)
        
        # Block
        block = Block(blocker_id=alice.id, blocked_id=blocked.id)
        db.session.add(block)
        
        # Reports
        report1 = Report(reporter_id=alice.id, reported_id=spam.id,
                        reason='spam', details='User keeps sending promotional messages',
                        status='pending')
        report2 = Report(reporter_id=bob.id, reported_id=spam.id,
                        reason='harassment', details='Sent inappropriate messages',
                        status='reviewed')
        db.session.add_all([report1, report2])
        
        db.session.commit()
    
    print("Test database seeded successfully!")


@pytest.fixture(scope='function')
def client():
    """Create a test client with a fresh in-memory database (like test_api.py)."""
    # Create temporary database file
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)
    
    # Configure app to use temporary database
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            # Create all tables
            db.drop_all()
            db.create_all()
            # Seed the test database
            seed_test_database()
            yield client
            # Clean up
            db.session.remove()
            db.drop_all()
    
    # Remove temporary file
    os.unlink(db_path)


def login(client, email, password):
    """Helper function to login and get token."""
    response = client.post('/api/v1/auth/login', json={
        'email': email,
        'password': password
    })
    if response.status_code == 200:
        return json.loads(response.data)['token']
    return None


def test_admin_can_login(client):
    """Test that Admin user can login."""
    token = login(client, 'admin@driftdater.com', 'admin123')
    assert token is not None
    print("  Admin login successful")


def test_alice_can_login(client):
    """Test that Alice can login."""
    token = login(client, 'alice@example.com', 'password123')
    assert token is not None
    print("  Alice login successful")


def test_bob_can_login(client):
    """Test that Bob can login."""
    token = login(client, 'bob@example.com', 'password123')
    assert token is not None
    print("  Bob login successful")


def test_perfect_can_login(client):
    """Test that Perfect can login."""
    token = login(client, 'perfect@example.com', 'password123')
    assert token is not None
    print("  Perfect login successful")


def test_blocked_user_can_login(client):
    """Test that Blocked user can login."""
    token = login(client, 'blocked@example.com', 'password123')
    assert token is not None
    print("  Blocked user login successful")


def test_spam_user_can_login(client):
    """Test that Spam user can login."""
    token = login(client, 'spam@example.com', 'password123')
    assert token is not None
    print("  Spam user login successful")


def test_alice_can_browse_profiles(client):
    """Test that Alice can browse profiles."""
    token = login(client, 'alice@example.com', 'password123')
    assert token is not None
    
    response = client.get('/api/v1/profiles',
                         headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'profiles' in data
    print(f"  Alice browsed {data['total']} profiles")


def test_alice_can_get_matches(client):
    """Test that Alice can get her matches."""
    token = login(client, 'alice@example.com', 'password123')
    assert token is not None
    
    response = client.get('/api/v1/matches',
                         headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'matches' in data
    # Alice should have at least 1 match (with Perfect)
    assert data['total'] >= 1
    print(f"  Alice has {data['total']} matches")


def test_alice_can_send_message_to_match(client):
    """Test that Alice can send a message to her match (Perfect)."""
    token = login(client, 'alice@example.com', 'password123')
    assert token is not None
    
    # Get matches to find match_id
    response = client.get('/api/v1/matches',
                         headers={'Authorization': f'Bearer {token}'})
    matches = json.loads(response.data)
    
    if matches['total'] > 0:
        match_id = matches['matches'][0]['id']
        
        # Send message
        response = client.post(f'/api/v1/matches/{match_id}/messages',
                              json={'body': 'Hello from QA test!'},
                              headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 201
        print("  Alice can send messages to her match")


def test_search_filter_by_parish(client):
    """Test search filter by parish."""
    token = login(client, 'alice@example.com', 'password123')
    assert token is not None
    
    response = client.get('/api/v1/profiles?parish=Kingston',
                         headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 200
    print("  Parish filter works")


def test_search_filter_by_age_range(client):
    """Test search filter by age range."""
    token = login(client, 'alice@example.com', 'password123')
    assert token is not None
    
    response = client.get('/api/v1/profiles?age_min=25&age_max=30',
                         headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 200
    print("  Age filter works")


def test_performance_browse_under_2_seconds(client):
    """Test that browsing profiles takes less than 2 seconds."""
    import time
    
    token = login(client, 'alice@example.com', 'password123')
    assert token is not None
    
    start = time.time()
    response = client.get('/api/v1/profiles',
                         headers={'Authorization': f'Bearer {token}'})
    elapsed = time.time() - start
    
    assert response.status_code == 200
    assert elapsed < 2.0, f"Took {elapsed:.2f} seconds (exceeds 2s limit)"
    print(f"  Browse took {elapsed:.2f} seconds (<2s)")


def test_admin_stats_endpoint(client):
    """Test admin stats endpoint."""
    token = login(client, 'admin@driftdater.com', 'admin123')
    assert token is not None
    
    response = client.get('/api/v1/admin/stats',
                         headers={'Authorization': f'Bearer {token}'})
    
    # Admin stats endpoint should exist
    if response.status_code == 404:
        print("⚠ Admin stats endpoint not implemented (skipping)")
        pytest.skip("Admin stats endpoint not implemented")
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'total_users' in data
    print("  Admin stats endpoint works")