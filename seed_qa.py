"""
DriftDater - QA Database Seeder
Run: python seed_qa.py
Populates database with test users and interactions for QA testing.
"""

from app import app, db
from app.models import User, Profile, Interest, Like, Match, Message, Favourite, Report, Block
from datetime import date

# Interests list
INTERESTS = [
    'Hiking', 'Photography', 'Cooking', 'Gaming', 'Reading',
    'Travelling', 'Music', 'Movies', 'Sports', 'Fitness',
    'Art', 'Dancing', 'Yoga', 'Coding', 'Gardening',
    'Coffee', 'Wine', 'Volunteering', 'Fashion', 'Foodie',
]

# QA Test Users
QA_USERS = [
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


def seed_qa():
    with app.app_context():
        print("=== DriftDater QA Seeder ===\n")
        db.create_all()

        # Seed interests
        print("Seeding interests")
        for name in INTERESTS:
            if not Interest.query.filter_by(name=name).first():
                db.session.add(Interest(name=name))
        db.session.commit()
        print(f"  {Interest.query.count()} interests available")

        # Seed users
        print("\nSeeding users")
        all_interests = {i.name: i for i in Interest.query.all()}

        for data in QA_USERS:
            if User.query.filter_by(email=data['email']).first():
                print(f"  Skipping {data['email']} (already exists)")
                continue

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
            print(f"  Created: {data['email']} (pwd: {data['password']})")

        db.session.commit()

        # Create interactions (likes, matches, messages, etc.)
        print("\nCreating test interactions...")

        alice = User.query.filter_by(email='alice@example.com').first()
        bob = User.query.filter_by(email='bob@example.com').first()
        perfect = User.query.filter_by(email='perfect@example.com').first()
        blocked = User.query.filter_by(email='blocked@example.com').first()
        spam = User.query.filter_by(email='spam@example.com').first()
        admin = User.query.filter_by(email='admin@driftdater.com').first()

        if not all([alice, bob, perfect, blocked, spam, admin]):
            print("  WARNING: Some users missing, skipping interactions")
        else:
            # 1. Mutual match: Alice <-> Perfect
            print("  Creating mutual match between Alice and Perfect...")

            # Alice likes Perfect
            like1 = Like(liker_id=alice.id, liked_id=perfect.id, action='like')
            db.session.add(like1)

            # Perfect likes Alice (mutual!)
            like2 = Like(liker_id=perfect.id, liked_id=alice.id, action='like')
            db.session.add(like2)
            db.session.flush()

            # Create match record
            match = Match(user1_id=alice.id, user2_id=perfect.id)
            db.session.add(match)
            db.session.flush()

            # Messages between Alice and Perfect
            msg1 = Message(
                match_id=match.id,
                sender_id=alice.id,
                body="Hey Perfect! Love your profile! Want to chat?"
            )
            msg2 = Message(
                match_id=match.id,
                sender_id=perfect.id,
                body="Hi Alice! Thanks! Your photos are amazing. Would love to chat!"
            )
            db.session.add_all([msg1, msg2])
            print("     Match and messages created")

            # 2. Alice likes Bob (not mutual yet)
            print("  Creating one-way like: Alice -> Bob...")
            like3 = Like(liker_id=alice.id, liked_id=bob.id, action='like')
            db.session.add(like3)
            print("     Like created")

            # 3. Favourites (bookmarks)
            print("  Create favourites")
            fav = Favourite(user_id=alice.id, profile_id=bob.profile.id)
            db.session.add(fav)
            print("    Alice bookmarked Bob")

            # 4. Block: Alice blocks blocked_user
            print("  Create block: Alice blocks blocked_user")
            block = Block(blocker_id=alice.id, blocked_id=blocked.id)
            db.session.add(block)
            print("    Block created")

            # 5. Reports: Spam user reported
            print("  Create reports for spam user")
            report1 = Report(
                reporter_id=alice.id,
                reported_id=spam.id,
                reason='spam',
                details='User keeps sending promotional messages',
                status='pending'
            )
            report2 = Report(
                reporter_id=bob.id,
                reported_id=spam.id,
                reason='harassment',
                details='Sent inappropriate messages',
                status='reviewed'
            )
            db.session.add_all([report1, report2])
            print("2 reports created")

            db.session.commit()

        # Summary
        print(f"\n=== Seeding Complete ===")
        print(f"Users: {User.query.count()}")
        print(f"Profiles: {Profile.query.count()}")
        print(f"Interests: {Interest.query.count()}")
        print(f"Likes: {Like.query.count()}")
        print(f"Matches: {Match.query.count()}")
        print(f"Messages: {Message.query.count()}")
        print(f"Favourites: {Favourite.query.count()}")
        print(f"Reports: {Report.query.count()}")
        print(f"Blocks: {Block.query.count()}")

        print("\nTest Accounts:")
        print("  Admin:    admin@driftdater.com / admin123")
        print("  Alice:    alice@example.com / password123")
        print("  Bob:      bob@example.com / password123")
        print("  Perfect:  perfect@example.com / password123 (mutual match with Alice)")
        print("  Blocked:  blocked@example.com / password123 (blocked by Alice)")
        print("  Spam:     spam@example.com / password123 (reported user)")

        print("\nTest Scenarios Ready:")
        print("Mutual match: Alice and Perfect")
        print("Messages between matched users")
        print("One-way like: Alice liked Bob")
        print("Favourite: Alice bookmarked Bob")
        print("Block: Alice blocked BlockedUser")
        print("Reports: SpamUser reported by Alice and Bob")


if __name__ == '__main__':
    seed_qa()