"""
DriftDater - Database Seeder
Run: python seed.py
Populates the database with sample interests and test users.
"""

from app import app, db
from app.models import User, Profile, Interest
from datetime import date


INTERESTS = [
    'Hiking', 'Photography', 'Cooking', 'Gaming', 'Reading',
    'Travelling', 'Music', 'Movies', 'Sports', 'Fitness',
    'Art', 'Dancing', 'Yoga', 'Coding', 'Gardening',
    'Coffee', 'Wine', 'Volunteering', 'Fashion', 'Foodie',
]

SAMPLE_USERS = [
    {
        'username': 'alice_w',
        'email': 'alice@example.com',
        'password': 'password123',
        'profile': {
            'first_name': 'Alice', 'last_name': 'Wonder',
            'date_of_birth': date(1999, 3, 15),
            'gender': 'female', 'looking_for': 'male',
            'bio': 'Love hiking and adventure! Let\'s explore the world together.',
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
            'bio': 'Software developer by day, photographer by night.',
            'parish': 'Kingston', 'city': 'Kingston', 'country': 'Jamaica',
            'occupation': 'Software Developer', 'education_level': 'bachelor',
            'interests': ['Coding', 'Photography', 'Gaming', 'Hiking'],
        },
    },
    {
        'username': 'grace_gamer',
        'email': 'grace@example.com',
        'password': 'password123',
        'profile': {
            'first_name': 'Grace', 'last_name': 'Gamer',
            'date_of_birth': date(2001, 11, 5),
            'gender': 'female', 'looking_for': 'any',
            'bio': 'Gamer and coffee enthusiast. Let\'s play!',
            'parish': 'St. Andrew', 'city': 'Half Way Tree', 'country': 'Jamaica',
            'occupation': 'Student', 'education_level': 'bachelor',
            'interests': ['Gaming', 'Coffee', 'Movies', 'Music'],
        },
    },
    {
        'username': 'carol_cook',
        'email': 'carol@example.com',
        'password': 'password123',
        'profile': {
            'first_name': 'Carol', 'last_name': 'Cook',
            'date_of_birth': date(2000, 5, 12),
            'gender': 'female', 'looking_for': 'male',
            'bio': 'Chef and coffee lover. Looking for someone to cook for!',
            'parish': 'St. Catherine', 'city': 'Portmore', 'country': 'Jamaica',
            'occupation': 'Chef', 'education_level': 'associate',
            'interests': ['Cooking', 'Foodie', 'Wine', 'Travelling'],
        },
    },
]


def seed():
    with app.app_context():
        print("Creating tables...")
        db.create_all()

        # Seed interests
        print("Seeding interests...")
        for name in INTERESTS:
            if not Interest.query.filter_by(name=name).first():
                db.session.add(Interest(name=name))
        db.session.commit()

        # Seed users
        print("Seeding sample users...")
        all_interests = {i.name: i for i in Interest.query.all()}

        for data in SAMPLE_USERS:
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
            print(f"  Created user: {data['email']}")

        db.session.commit()
        print("Done! Sample credentials: alice@example.com / password123")


if __name__ == '__main__':
    seed()
