"""
DriftDater - Large Seeder  (100 users)
Run: python seed_large.py

Creates:
  • All interests
  • 100 users with full profiles (Jamaican context)
  • Mutual likes → ~35 matches
  • 5-12 messages per match
  • Skips rows that already exist
"""

import random
from datetime import date, datetime, timezone, timedelta
from app import app, db
from app.models import User, Profile, Interest, Like, Match, Message

random.seed(42)

# ---------------------------------------------------------------------------
# Reference data
# ---------------------------------------------------------------------------
INTERESTS = [
    'Hiking', 'Photography', 'Cooking', 'Gaming', 'Reading',
    'Travelling', 'Music', 'Movies', 'Sports', 'Fitness',
    'Art', 'Dancing', 'Yoga', 'Coding', 'Gardening',
    'Coffee', 'Wine', 'Volunteering', 'Fashion', 'Foodie',
]

PARISHES = [
    'Kingston', 'St. Andrew', 'St. Thomas', 'Portland', 'St. Mary',
    'St. Ann', 'Trelawny', 'St. James', 'Hanover', 'Westmoreland',
    'St. Elizabeth', 'Manchester', 'Clarendon', 'St. Catherine',
]

CITIES = {
    'Kingston':      ['Kingston'],
    'St. Andrew':    ['Half Way Tree', 'Liguanea', 'Constant Spring'],
    'St. Thomas':    ['Morant Bay', 'Yallahs'],
    'Portland':      ['Port Antonio', 'Buff Bay'],
    'St. Mary':      ['Port Maria', 'Annotto Bay'],
    'St. Ann':       ['Ocho Rios', "St. Ann's Bay", "Brown's Town"],
    'Trelawny':      ['Falmouth', "Clark's Town"],
    'St. James':     ['Montego Bay', 'Rose Hall'],
    'Hanover':       ['Lucea', 'Green Island'],
    'Westmoreland':  ['Savanna-la-Mar', 'Negril'],
    'St. Elizabeth': ['Black River', 'Santa Cruz'],
    'Manchester':    ['Mandeville', 'Christiana'],
    'Clarendon':     ['May Pen', 'Chapelton'],
    'St. Catherine': ['Portmore', 'Spanish Town', 'Old Harbour'],
}

OCCUPATIONS = [
    'Software Developer', 'Nurse', 'Teacher', 'Accountant', 'Chef',
    'Graphic Designer', 'Lawyer', 'Doctor', 'Engineer', 'Pharmacist',
    'Entrepreneur', 'Journalist', 'Police Officer', 'Social Worker',
    'Marketing Manager', 'Electrician', 'Architect', 'Lecturer',
    'Financial Analyst', 'Physical Therapist', 'Student', 'Artist',
    'Musician', 'Photographer', 'Real Estate Agent',
]

EDUCATION_LEVELS = [
    'high_school', 'associate', 'bachelor', 'master', 'doctorate', 'other',
]

FEMALE_FIRST = [
    'Alicia', 'Brianna', 'Camille', 'Danielle', 'Ebony', 'Felicia', 'Gabrielle',
    'Hannah', 'Imani', 'Jade', 'Keisha', 'Latoya', 'Monique', 'Nicole', 'Olivia',
    'Patricia', 'Renee', 'Simone', 'Tamara', 'Ursula', 'Vanessa', 'Whitney',
    'Yolanda', 'Zoe', 'Anika', 'Bernice', 'Candace', 'Deneisha', 'Enid',
    'Farrah', 'Geneva', 'Hyacinth', 'Ingrid', 'Jasmine', 'Karen',
]

MALE_FIRST = [
    'Andre', 'Brandon', 'Calvin', 'Damion', 'Errol', 'Fabian', 'Gregory',
    'Horace', 'Ivan', 'Jermaine', 'Kevin', 'Leroy', 'Marcus', 'Nathaniel',
    'Omar', 'Patrick', 'Quinton', 'Rodney', 'Sheldon', 'Tyrone', 'Ulric',
    'Vernon', 'Wayne', 'Xavier', 'Yvonne', 'Zachariah', 'Aldeen', 'Barrington',
    'Clive', 'Delroy', 'Everton', 'Floyd', 'Garfield', 'Hubert', 'Ike',
]

LAST_NAMES = [
    'Brown', 'Williams', 'Smith', 'Campbell', 'Reid', 'Thompson', 'Clarke',
    'Johnson', 'Robinson', 'Davis', 'Anderson', 'Scott', 'Lewis', 'Wright',
    'Green', 'Hall', 'Walker', 'Allen', 'King', 'Morris', 'Turner', 'Baker',
    'Edwards', 'Mitchell', 'Nelson', 'Carter', 'Graham', 'Stewart', 'Taylor',
    'White', 'Harris', 'Martin', 'Jackson', 'Thomas', 'Moore', 'Wilson',
    'Young', 'Adams', 'Patterson', 'Miller',
]

BIO_TEMPLATES = [
    "Love exploring {parish} and beyond. Looking for someone who enjoys {i1} and {i2}.",
    "{occupation} with a passion for {i1}. Ask me about {i2}!",
    "Life's short — let's make memories. Big fan of {i1} and {i2}.",
    "Raised in {city}, heart full of ambition. Enjoy {i1} in my downtime.",
    "Laid-back {occupation} who loves {i1}, {i2}, and good vibes only.",
    "Searching for my person. I unwind with {i1} and {i2}. You?",
    "Creative soul from {parish}. Passionate about {i1} and always up for {i2}.",
    "Hard-working {occupation} by week, adventure-seeker on weekends. Into {i1}.",
    "Simple and genuine. Love {i1}, good food, and honest conversations.",
    "Fitness and {i1} keep me sane. {occupation} trying to find balance.",
]

MESSAGE_POOL = [
    "Hey! I saw your profile and thought we'd get along great.",
    "Hi there! Love your taste in {interest}!",
    "Hey, how's your day going?",
    "I noticed you're from {parish} too! Small world.",
    "That bio had me laughing — we have so much in common!",
    "What do you usually get up to on weekends?",
    "Just wanted to say hi. Your profile really caught my eye!",
    "I'm a huge fan of {interest} too — any recommendations?",
    "Hope you're having a great day!",
    "Tell me more about yourself!",
    "Do you have a favourite spot in {parish}?",
    "Been to any good {interest} events lately?",
    "Your photos are amazing! Are you into photography?",
    "What's the best part of living in {parish}?",
    "I'd love to hear more about your work as a {occupation}.",
    "We matched! How's life treating you?",
    "Any fun plans coming up this weekend?",
    "I feel like we could have really interesting conversations.",
    "I love {interest} too! We should talk more.",
    "Hey stranger, fancy a chat?",
    "You seem really interesting. What are you passionate about?",
    "Just moved to {parish} — any tips?",
    "Love your vibe. What music are you into?",
    "What's your go-to comfort food?",
    "Chill person here, looking for genuine connection.",
    "Your sense of humour in that bio — love it!",
    "Okay I had to reach out after seeing your profile!",
    "Tell me one random fact about yourself.",
    "Are you more of a beach or mountain person?",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def pick(lst):
    return random.choice(lst)


def rand_date_of_birth(min_age=18, max_age=45):
    today = date.today()
    age = random.randint(min_age, max_age)
    dob_year = today.year - age
    try:
        return date(dob_year, random.randint(1, 12), random.randint(1, 28))
    except ValueError:
        return date(dob_year, 1, 1)


def rand_message(user, other_user):
    template = pick(MESSAGE_POOL)
    interests = [i.name for i in user.profile.interests] if user.profile else ['music']
    interest = pick(interests) if interests else 'music'
    parish = user.profile.parish if user.profile else 'Kingston'
    occupation = user.profile.occupation if user.profile else 'professional'
    return template.format(
        interest=interest,
        parish=parish,
        occupation=occupation,
    )


def rand_dt_within(days=60):
    """Random datetime within the last `days` days."""
    delta = timedelta(seconds=random.randint(0, days * 86400))
    return datetime.now(timezone.utc) - delta


# ---------------------------------------------------------------------------
# Build user data list
# ---------------------------------------------------------------------------
def build_users(n=100):
    used_usernames = set()
    used_emails = set()
    users = []

    female_names = list(FEMALE_FIRST)
    male_names   = list(MALE_FIRST)
    random.shuffle(female_names)
    random.shuffle(male_names)

    for i in range(n):
        gender = 'female' if i % 2 == 0 else 'male'
        first  = (female_names[i // 2 % len(female_names)] if gender == 'female'
                  else male_names[i // 2 % len(male_names)])
        last   = pick(LAST_NAMES)

        base = f"{first.lower()}_{last.lower()}"
        username = base
        suffix = 1
        while username in used_usernames:
            username = f"{base}{suffix}"
            suffix += 1
        used_usernames.add(username)

        email = f"{username}@example.com"
        while email in used_emails:
            email = f"{username}{random.randint(1,99)}@example.com"
        used_emails.add(email)

        parish = pick(PARISHES)
        city   = pick(CITIES[parish])
        occ    = pick(OCCUPATIONS)

        interest_names = random.sample(INTERESTS, random.randint(3, 6))
        bio_tmpl = pick(BIO_TEMPLATES)
        bio = bio_tmpl.format(
            parish=parish, city=city, occupation=occ,
            i1=interest_names[0], i2=interest_names[1] if len(interest_names) > 1 else interest_names[0],
        )

        looking_for = pick(['male', 'female', 'any', 'any'])

        users.append({
            'username': username,
            'email': email,
            'password': 'password123',
            'profile': {
                'first_name': first,
                'last_name': last,
                'date_of_birth': rand_date_of_birth(),
                'gender': gender,
                'looking_for': looking_for,
                'bio': bio,
                'parish': parish,
                'city': city,
                'country': 'Jamaica',
                'occupation': occ,
                'education_level': pick(EDUCATION_LEVELS),
                'interests': interest_names,
            },
        })

    return users


# ---------------------------------------------------------------------------
# Main seeder
# ---------------------------------------------------------------------------
def seed():
    with app.app_context():
        db.create_all()

        # ── Interests ──────────────────────────────────────────────────────
        print("Seeding interests...")
        for name in INTERESTS:
            if not Interest.query.filter_by(name=name).first():
                db.session.add(Interest(name=name))
        db.session.commit()
        all_interests = {i.name: i for i in Interest.query.all()}

        # ── Users + Profiles ───────────────────────────────────────────────
        print("Seeding 100 users...")
        user_data_list = build_users(100)
        created_users = []

        for data in user_data_list:
            if User.query.filter_by(email=data['email']).first():
                print(f"  Skipping {data['email']} (exists)")
                existing = User.query.filter_by(email=data['email']).first()
                created_users.append(existing)
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
                bio=pd['bio'],
                parish=pd['parish'],
                city=pd['city'],
                country=pd['country'],
                occupation=pd['occupation'],
                education_level=pd['education_level'],
            )
            profile.interests = [all_interests[n] for n in pd['interests']
                                  if n in all_interests]
            db.session.add(profile)
            created_users.append(user)

        db.session.commit()
        print(f"  {len(created_users)} users ready.")

        created_users = [db.session.merge(u) for u in created_users]

        # ── Likes & Matches ────────────────────────────────────────────────
        print("Creating likes and matches...")
        match_count = 0
        like_count  = 0

        pairs = list(range(len(created_users)))
        random.shuffle(pairs)
        mutual_pairs = [(pairs[i], pairs[i+1]) for i in range(0, 70, 2)]

        for a_idx, b_idx in mutual_pairs:
            a = created_users[a_idx]
            b = created_users[b_idx]

            for liker, liked in [(a, b), (b, a)]:
                exists = Like.query.filter_by(
                    liker_id=liker.id, liked_id=liked.id).first()
                if not exists:
                    db.session.add(Like(
                        liker_id=liker.id,
                        liked_id=liked.id,
                        action='like',
                    ))
                    like_count += 1

            uid1, uid2 = sorted([a.id, b.id])
            if not Match.query.filter_by(user1_id=uid1, user2_id=uid2).first():
                db.session.add(Match(user1_id=uid1, user2_id=uid2))
                match_count += 1

        db.session.commit()
        print(f"  {like_count} likes, {match_count} matches created.")

        # ── Messages ───────────────────────────────────────────────────────
        print("Creating messages...")
        msg_count = 0
        matches = Match.query.all()

        for match in matches:
            u1 = db.session.get(User, match.user1_id)
            u2 = db.session.get(User, match.user2_id)
            if not u1 or not u2:
                continue

            if Message.query.filter_by(match_id=match.id).first():
                continue

            num_msgs = random.randint(5, 12)
            base_time = rand_dt_within(days=30)

            for j in range(num_msgs):
                sender = u1 if j % 2 == 0 else u2
                other  = u2 if sender == u1 else u1
                body   = rand_message(sender, other)
                msg_time = base_time + timedelta(minutes=j * random.randint(2, 60))
                db.session.add(Message(
                    match_id=match.id,
                    sender_id=sender.id,
                    body=body,
                    created_at=msg_time,
                ))
                msg_count += 1

        db.session.commit()
        print(f"  {msg_count} messages created.")

        print("\nDone! Login with any user: <username>@example.com / password123")
        print("Example: alicia_brown@example.com / password123")


if __name__ == '__main__':
    seed()
