"""
DriftDater - SQLAlchemy Models
Tables: User, Profile, Interest, UserInterest, Like, Match, Message, Favourite
"""

from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime, timezone
import bcrypt


# ---------------------------------------------------------------------------
# Association table: Profile <-> Interest  (many-to-many)
# ---------------------------------------------------------------------------
profile_interests = db.Table(
    'profile_interests',
    db.Column('profile_id', db.Integer, db.ForeignKey('profiles.id',
              ondelete='CASCADE'), primary_key=True),
    db.Column('interest_id', db.Integer, db.ForeignKey('interests.id',
              ondelete='CASCADE'), primary_key=True)
)


# ---------------------------------------------------------------------------
# User  (authentication record)
# ---------------------------------------------------------------------------
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email         = db.Column(db.String(128), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at    = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # back-references populated by Profile
    profile       = db.relationship('Profile', back_populates='user',
                                    uselist=False, cascade='all, delete-orphan')

    def set_password(self, plaintext: str) -> None:
        """Hash and store password using bcrypt."""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(
            plaintext.encode('utf-8'), salt
        ).decode('utf-8')

    def check_password(self, plaintext: str) -> bool:
        """Verify a plaintext password against the stored hash."""
        return bcrypt.checkpw(
            plaintext.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ---------------------------------------------------------------------------
# Profile  (user profile details)
# ---------------------------------------------------------------------------
class Profile(db.Model):
    __tablename__ = 'profiles'

    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey('users.id',
                                ondelete='CASCADE'), unique=True, nullable=False, index=True)

    # Basic info
    first_name      = db.Column(db.String(64), nullable=False)
    last_name       = db.Column(db.String(64), nullable=False)
    date_of_birth   = db.Column(db.Date, nullable=False)
    gender          = db.Column(db.String(32), nullable=False)   # male/female/non-binary/other
    looking_for     = db.Column(db.String(32), default='any')    # male/female/any

    # Bio & location
    bio             = db.Column(db.Text)
    parish          = db.Column(db.String(64))                   # e.g. Kingston, St. Andrew
    city            = db.Column(db.String(64))
    country         = db.Column(db.String(64), default='Jamaica')
    latitude        = db.Column(db.Float)
    longitude       = db.Column(db.Float)

    # Preferences
    preferred_age_min = db.Column(db.Integer, default=18)
    preferred_age_max = db.Column(db.Integer, default=99)
    preferred_radius  = db.Column(db.Integer, default=50)        # km

    # Additional custom fields (requirement: min 2 extra)
    occupation      = db.Column(db.String(128))
    education_level = db.Column(db.String(64))                   # e.g. Bachelor's, Master's

    # Profile photo
    photo_filename  = db.Column(db.String(256))
    is_public       = db.Column(db.Boolean, default=True)

    created_at      = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at      = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                                onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user            = db.relationship('User', back_populates='profile')
    interests       = db.relationship('Interest', secondary=profile_interests,
                                      back_populates='profiles', lazy='select')

    # Indexes for frequently queried columns
    __table_args__ = (
        db.Index('ix_profiles_location', 'parish', 'country'),
        db.Index('ix_profiles_gender',   'gender'),
    )

    @property
    def age(self):
        if not self.date_of_birth:
            return None
        today = datetime.now(timezone.utc).date()
        dob = self.date_of_birth
        return today.year - dob.year - (
            (today.month, today.day) < (dob.month, dob.day)
        )

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def to_dict(self, include_private=False):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'age': self.age,
            'gender': self.gender,
            'looking_for': self.looking_for,
            'bio': self.bio,
            'parish': self.parish,
            'city': self.city,
            'country': self.country,
            'occupation': self.occupation,
            'education_level': self.education_level,
            'photo_url': (self.photo_filename
                          if self.photo_filename and self.photo_filename.startswith('http')
                          else (f"/api/v1/uploads/{self.photo_filename}" if self.photo_filename else None)),
            'is_public': self.is_public,
            'interests': [i.name for i in self.interests],
            'preferred_age_min': self.preferred_age_min,
            'preferred_age_max': self.preferred_age_max,
            'preferred_radius': self.preferred_radius,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_private:
            data.update({
                'email': self.user.email if self.user else None,
                'latitude': self.latitude,
                'longitude': self.longitude,
            })
        return data


# ---------------------------------------------------------------------------
# Interest  (predefined + custom interests/hobbies)
# ---------------------------------------------------------------------------
class Interest(db.Model):
    __tablename__ = 'interests'

    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(64), unique=True, nullable=False, index=True)

    profiles = db.relationship('Profile', secondary=profile_interests,
                                back_populates='interests', lazy='select')

    def to_dict(self):
        return {'id': self.id, 'name': self.name}


# ---------------------------------------------------------------------------
# Like  (one user likes or passes on another)
# ---------------------------------------------------------------------------
class Like(db.Model):
    __tablename__ = 'likes'

    id          = db.Column(db.Integer, primary_key=True)
    liker_id    = db.Column(db.Integer, db.ForeignKey('users.id',
                            ondelete='CASCADE'), nullable=False)
    liked_id    = db.Column(db.Integer, db.ForeignKey('users.id',
                            ondelete='CASCADE'), nullable=False)
    action      = db.Column(db.String(16), nullable=False)  # 'like' | 'pass'
    created_at  = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint('liker_id', 'liked_id', name='uq_like_pair'),
        db.Index('ix_likes_liker',  'liker_id'),
        db.Index('ix_likes_liked',  'liked_id'),
    )

    liker = db.relationship('User', foreign_keys=[liker_id])
    liked = db.relationship('User', foreign_keys=[liked_id])


# ---------------------------------------------------------------------------
# Match  (mutual like — created automatically when both users like each other)
# ---------------------------------------------------------------------------
class Match(db.Model):
    __tablename__ = 'matches'

    id          = db.Column(db.Integer, primary_key=True)
    user1_id    = db.Column(db.Integer, db.ForeignKey('users.id',
                            ondelete='CASCADE'), nullable=False)
    user2_id    = db.Column(db.Integer, db.ForeignKey('users.id',
                            ondelete='CASCADE'), nullable=False)
    created_at  = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint('user1_id', 'user2_id', name='uq_match_pair'),
        db.Index('ix_matches_user1', 'user1_id'),
        db.Index('ix_matches_user2', 'user2_id'),
    )

    user1    = db.relationship('User', foreign_keys=[user1_id])
    user2    = db.relationship('User', foreign_keys=[user2_id])
    messages = db.relationship('Message', back_populates='match',
                               cascade='all, delete-orphan',
                               order_by='Message.created_at')

    def other_user(self, current_user_id):
        """Return the other participant in this match."""
        return self.user2 if self.user1_id == current_user_id else self.user1

    def to_dict(self, current_user_id=None):
        other = self.other_user(current_user_id) if current_user_id else None
        return {
            'id': self.id,
            'user1_id': self.user1_id,
            'user2_id': self.user2_id,
            'matched_at': self.created_at.isoformat() if self.created_at else None,
            'other_profile': other.profile.to_dict() if (other and other.profile) else None,
        }


# ---------------------------------------------------------------------------
# Message  (chat messages between matched users)
# ---------------------------------------------------------------------------
class Message(db.Model):
    __tablename__ = 'messages'

    id          = db.Column(db.Integer, primary_key=True)
    match_id    = db.Column(db.Integer, db.ForeignKey('matches.id',
                            ondelete='CASCADE'), nullable=False, index=True)
    sender_id   = db.Column(db.Integer, db.ForeignKey('users.id',
                            ondelete='CASCADE'), nullable=False)
    body        = db.Column(db.Text, nullable=False)
    created_at  = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                            index=True)

    match  = db.relationship('Match', back_populates='messages')
    sender = db.relationship('User', foreign_keys=[sender_id])

    def to_dict(self):
        return {
            'id': self.id,
            'match_id': self.match_id,
            'sender_id': self.sender_id,
            'sender_username': self.sender.username if self.sender else None,
            'body': self.body,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# ---------------------------------------------------------------------------
# Favourite  (bookmarked profiles)
# ---------------------------------------------------------------------------
class Favourite(db.Model):
    __tablename__ = 'favourites'

    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('users.id',
                             ondelete='CASCADE'), nullable=False)
    profile_id   = db.Column(db.Integer, db.ForeignKey('profiles.id',
                             ondelete='CASCADE'), nullable=False)
    created_at   = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint('user_id', 'profile_id', name='uq_favourite'),
    )

    user    = db.relationship('User',    foreign_keys=[user_id])
    profile = db.relationship('Profile', foreign_keys=[profile_id])


# ---------------------------------------------------------------------------
# Report  (optional feature: report/block users)
# ---------------------------------------------------------------------------
class Report(db.Model):
    __tablename__ = 'reports'

    id          = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    reported_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    reason      = db.Column(db.String(64), nullable=False)   # spam/harassment/fake/other
    details     = db.Column(db.Text)
    status      = db.Column(db.String(16), default='pending')  # pending/reviewed/dismissed
    created_at  = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint('reporter_id', 'reported_id', name='uq_report_pair'),
        db.Index('ix_reports_status', 'status'),
    )

    reporter = db.relationship('User', foreign_keys=[reporter_id])
    reported = db.relationship('User', foreign_keys=[reported_id])

    def to_dict(self):
        return {
            'id': self.id,
            'reporter_id': self.reporter_id,
            'reported_id': self.reported_id,
            'reported_username': self.reported.username if self.reported else None,
            'reason': self.reason,
            'details': self.details,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# ---------------------------------------------------------------------------
# Block  (optional feature: block users)
# ---------------------------------------------------------------------------
class Block(db.Model):
    __tablename__ = 'blocks'

    id         = db.Column(db.Integer, primary_key=True)
    blocker_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    blocked_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint('blocker_id', 'blocked_id', name='uq_block_pair'),
        db.Index('ix_blocks_blocker', 'blocker_id'),
    )

    blocker = db.relationship('User', foreign_keys=[blocker_id])
    blocked = db.relationship('User', foreign_keys=[blocked_id])
