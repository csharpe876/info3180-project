"""initial schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2025-01-05 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # users — no FK dependencies
    op.create_table(
        'users',
        sa.Column('id',            sa.Integer(),     nullable=False),
        sa.Column('username',      sa.String(64),    nullable=False),
        sa.Column('email',         sa.String(128),   nullable=False),
        sa.Column('password_hash', sa.String(256),   nullable=False),
        sa.Column('created_at',    sa.DateTime(),    nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email'),
    )
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    op.create_index('ix_users_email',    'users', ['email'],    unique=True)

    # interests — no FK dependencies
    op.create_table(
        'interests',
        sa.Column('id',   sa.Integer(),  nullable=False),
        sa.Column('name', sa.String(64), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )
    op.create_index('ix_interests_name', 'interests', ['name'], unique=True)

    # profiles — FK to users
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
        sa.UniqueConstraint('user_id'),
    )
    op.create_index('ix_profiles_user_id',  'profiles', ['user_id'],          unique=True)
    op.create_index('ix_profiles_location', 'profiles', ['parish', 'country'], unique=False)
    op.create_index('ix_profiles_gender',   'profiles', ['gender'],            unique=False)

    # profile_interests — junction table (FK to profiles and interests)
    op.create_table(
        'profile_interests',
        sa.Column('profile_id',  sa.Integer(), nullable=False),
        sa.Column('interest_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['profile_id'],  ['profiles.id'],  ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['interest_id'], ['interests.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('profile_id', 'interest_id'),
    )

    # likes — FK to users
    op.create_table(
        'likes',
        sa.Column('id',         sa.Integer(),  nullable=False),
        sa.Column('liker_id',   sa.Integer(),  nullable=False),
        sa.Column('liked_id',   sa.Integer(),  nullable=False),
        sa.Column('action',     sa.String(16), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['liker_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['liked_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('liker_id', 'liked_id', name='uq_like_pair'),
    )
    op.create_index('ix_likes_liker', 'likes', ['liker_id'], unique=False)
    op.create_index('ix_likes_liked', 'likes', ['liked_id'], unique=False)

    # matches — FK to users
    op.create_table(
        'matches',
        sa.Column('id',         sa.Integer(), nullable=False),
        sa.Column('user1_id',   sa.Integer(), nullable=False),
        sa.Column('user2_id',   sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user1_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user2_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user1_id', 'user2_id', name='uq_match_pair'),
    )
    op.create_index('ix_matches_user1', 'matches', ['user1_id'], unique=False)
    op.create_index('ix_matches_user2', 'matches', ['user2_id'], unique=False)

    # messages — FK to matches and users
    op.create_table(
        'messages',
        sa.Column('id',         sa.Integer(), nullable=False),
        sa.Column('match_id',   sa.Integer(), nullable=False),
        sa.Column('sender_id',  sa.Integer(), nullable=False),
        sa.Column('body',       sa.Text(),    nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['match_id'],  ['matches.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'],   ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_messages_match_id',   'messages', ['match_id'],   unique=False)
    op.create_index('ix_messages_created_at', 'messages', ['created_at'], unique=False)

    # favourites — FK to users and profiles
    op.create_table(
        'favourites',
        sa.Column('id',         sa.Integer(), nullable=False),
        sa.Column('user_id',    sa.Integer(), nullable=False),
        sa.Column('profile_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'],    ['users.id'],    ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['profile_id'], ['profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'profile_id', name='uq_favourite'),
    )


def downgrade():
    op.drop_table('favourites')
    op.drop_table('messages')
    op.drop_index('ix_matches_user2', table_name='matches')
    op.drop_index('ix_matches_user1', table_name='matches')
    op.drop_table('matches')
    op.drop_index('ix_likes_liked',  table_name='likes')
    op.drop_index('ix_likes_liker',  table_name='likes')
    op.drop_table('likes')
    op.drop_table('profile_interests')
    op.drop_index('ix_profiles_gender',   table_name='profiles')
    op.drop_index('ix_profiles_location', table_name='profiles')
    op.drop_index('ix_profiles_user_id',  table_name='profiles')
    op.drop_table('profiles')
    op.drop_index('ix_interests_name', table_name='interests')
    op.drop_table('interests')
    op.drop_index('ix_users_email',    table_name='users')
    op.drop_index('ix_users_username', table_name='users')
    op.drop_table('users')
