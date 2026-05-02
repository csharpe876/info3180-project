"""Initial schema — creates all core tables

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-05-01 00:00:00.000000

This migration creates the eight core tables that were originally built via
db.create_all() and therefore never tracked by Alembic.  The subsequent
migration (471eb4a0b156) adds blocks and reports on top of this baseline.
"""

from alembic import op
import sqlalchemy as sa


# ---------------------------------------------------------------------------
# Revision identifiers
# ---------------------------------------------------------------------------
revision = '0001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ------------------------------------------------------------------
    # 1. users
    # ------------------------------------------------------------------
    op.create_table(
        'users',
        sa.Column('id',            sa.Integer(),     nullable=False),
        sa.Column('username',      sa.String(64),    nullable=False),
        sa.Column('email',         sa.String(128),   nullable=False),
        sa.Column('password_hash', sa.String(256),   nullable=False),
        sa.Column('created_at',    sa.DateTime(),    nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email',    name='uq_users_email'),
        sa.UniqueConstraint('username', name='uq_users_username'),
    )
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_index('ix_users_email',    ['email'],    unique=True)
        batch_op.create_index('ix_users_username', ['username'], unique=True)

    # ------------------------------------------------------------------
    # 2. interests
    # ------------------------------------------------------------------
    op.create_table(
        'interests',
        sa.Column('id',   sa.Integer(),   nullable=False),
        sa.Column('name', sa.String(64),  nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', name='uq_interests_name'),
    )
    with op.batch_alter_table('interests', schema=None) as batch_op:
        batch_op.create_index('ix_interests_name', ['name'], unique=True)

    # ------------------------------------------------------------------
    # 3. profiles  (depends on users)
    # ------------------------------------------------------------------
    op.create_table(
        'profiles',
        sa.Column('id',                sa.Integer(),    nullable=False),
        sa.Column('user_id',           sa.Integer(),    nullable=False),
        sa.Column('first_name',        sa.String(64),   nullable=False),
        sa.Column('last_name',         sa.String(64),   nullable=False),
        sa.Column('date_of_birth',     sa.Date(),       nullable=False),
        sa.Column('gender',            sa.String(32),   nullable=False),
        sa.Column('looking_for',       sa.String(32),   nullable=True),
        sa.Column('bio',               sa.Text(),       nullable=True),
        sa.Column('parish',            sa.String(64),   nullable=True),
        sa.Column('city',              sa.String(64),   nullable=True),
        sa.Column('country',           sa.String(64),   nullable=True),
        sa.Column('latitude',          sa.Float(),      nullable=True),
        sa.Column('longitude',         sa.Float(),      nullable=True),
        sa.Column('preferred_age_min', sa.Integer(),    nullable=True),
        sa.Column('preferred_age_max', sa.Integer(),    nullable=True),
        sa.Column('preferred_radius',  sa.Integer(),    nullable=True),
        sa.Column('occupation',        sa.String(128),  nullable=True),
        sa.Column('education_level',   sa.String(64),   nullable=True),
        sa.Column('photo_filename',    sa.String(256),  nullable=True),
        sa.Column('is_public',         sa.Boolean(),    nullable=True),
        sa.Column('created_at',        sa.DateTime(),   nullable=True),
        sa.Column('updated_at',        sa.DateTime(),   nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', name='uq_profiles_user_id'),
    )
    with op.batch_alter_table('profiles', schema=None) as batch_op:
        batch_op.create_index('ix_profiles_user_id',  ['user_id'],          unique=True)
        batch_op.create_index('ix_profiles_location', ['parish', 'country'], unique=False)
        batch_op.create_index('ix_profiles_gender',   ['gender'],            unique=False)

    # ------------------------------------------------------------------
    # 4. profile_interests  (depends on profiles + interests)
    # ------------------------------------------------------------------
    op.create_table(
        'profile_interests',
        sa.Column('profile_id',  sa.Integer(), nullable=False),
        sa.Column('interest_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['interest_id'], ['interests.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['profile_id'],  ['profiles.id'],  ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('profile_id', 'interest_id'),
    )

    # ------------------------------------------------------------------
    # 5. likes  (depends on users)
    # ------------------------------------------------------------------
    op.create_table(
        'likes',
        sa.Column('id',         sa.Integer(),   nullable=False),
        sa.Column('liker_id',   sa.Integer(),   nullable=False),
        sa.Column('liked_id',   sa.Integer(),   nullable=False),
        sa.Column('action',     sa.String(16),  nullable=False),
        sa.Column('created_at', sa.DateTime(),  nullable=True),
        sa.ForeignKeyConstraint(['liked_id'],  ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['liker_id'],  ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('liker_id', 'liked_id', name='uq_like_pair'),
    )
    with op.batch_alter_table('likes', schema=None) as batch_op:
        batch_op.create_index('ix_likes_liker', ['liker_id'], unique=False)
        batch_op.create_index('ix_likes_liked', ['liked_id'], unique=False)

    # ------------------------------------------------------------------
    # 6. matches  (depends on users)
    # ------------------------------------------------------------------
    op.create_table(
        'matches',
        sa.Column('id',         sa.Integer(),  nullable=False),
        sa.Column('user1_id',   sa.Integer(),  nullable=False),
        sa.Column('user2_id',   sa.Integer(),  nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user1_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user2_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user1_id', 'user2_id', name='uq_match_pair'),
    )
    with op.batch_alter_table('matches', schema=None) as batch_op:
        batch_op.create_index('ix_matches_user1', ['user1_id'], unique=False)
        batch_op.create_index('ix_matches_user2', ['user2_id'], unique=False)

    # ------------------------------------------------------------------
    # 7. messages  (depends on matches + users)
    # ------------------------------------------------------------------
    op.create_table(
        'messages',
        sa.Column('id',         sa.Integer(),  nullable=False),
        sa.Column('match_id',   sa.Integer(),  nullable=False),
        sa.Column('sender_id',  sa.Integer(),  nullable=False),
        sa.Column('body',       sa.Text(),     nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['match_id'],  ['matches.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'],   ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('messages', schema=None) as batch_op:
        batch_op.create_index('ix_messages_match_id',   ['match_id'],   unique=False)
        batch_op.create_index('ix_messages_created_at', ['created_at'], unique=False)

    # ------------------------------------------------------------------
    # 8. favourites  (depends on users + profiles)
    # ------------------------------------------------------------------
    op.create_table(
        'favourites',
        sa.Column('id',         sa.Integer(),  nullable=False),
        sa.Column('user_id',    sa.Integer(),  nullable=False),
        sa.Column('profile_id', sa.Integer(),  nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['profile_id'], ['profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'],    ['users.id'],    ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'profile_id', name='uq_favourite'),
    )


def downgrade():
    op.drop_table('favourites')
    op.drop_table('messages')
    op.drop_table('matches')
    op.drop_table('likes')
    op.drop_table('profile_interests')
    op.drop_table('profiles')
    op.drop_table('interests')
    op.drop_table('users')
