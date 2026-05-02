"""
DriftDater - Flask REST API Views
All routes are prefixed with /api/v1/
"""

import os
import jwt
import uuid
from datetime import datetime, timezone, timedelta
from functools import wraps

from flask import request, jsonify, send_from_directory, g, current_app
from werkzeug.utils import secure_filename

from app import app, db
from app.models import User, Profile, Interest, Like, Match, Message, Favourite
from app.forms import (
    RegistrationForm, LoginForm, ProfileForm,
    LikeForm, MessageForm, SearchForm
)


# ============================================================
# Helpers
# ============================================================

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_token(user_id: int) -> str:
    payload = {
        'sub': str(user_id),
        'iat': datetime.now(timezone.utc),
        'exp': datetime.now(timezone.utc) + timedelta(hours=app.config['JWT_EXPIRY_HOURS']),
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')


def token_required(f):
    """
    Decorator: require a valid JWT in Authorization header.
    Fixes the 'Subject must be a string' and integer casting issues.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization', '')

        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ', 1)[1]
        
        if not token:
            print("DEBUG: Authentication token is missing.")
            return jsonify({'error': 'Authentication token is missing.'}), 401

        try:
            # Decode using the secret key from app config
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            
            # Extract user_id from 'sub' (JWT standard) or 'user_id' (custom)
            raw_id = data.get('sub') or data.get('user_id')
            
            if not raw_id:
                print(f"DEBUG: No user identity found in token payload: {data}")
                return jsonify({'error': 'Invalid token payload.'}), 401

            # Cast to int to ensure compatibility with Database Primary Key
            g.current_user = db.session.get(User, int(raw_id))
            
            if not g.current_user:
                print(f"DEBUG: User ID {raw_id} not found in database.")
                return jsonify({'error': 'User not found.'}), 401



        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired.'}), 401
        except jwt.InvalidTokenError as e:
            print(f"DEBUG: JWT Validation Error: {str(e)}")
            return jsonify({'error': 'Invalid token.'}), 401
        except Exception as e:
            print(f"DEBUG: Unexpected Auth Error: {str(e)}")
            return jsonify({'error': 'Internal server error.'}), 500

        return f(*args, **kwargs)
    
    return decorated


def form_errors(form):
    """Collect WTForms validation errors into a flat list."""
    errors = []
    for field, errs in form.errors.items():
        label = getattr(form, field).label.text
        for e in errs:
            errors.append(f"Error in '{label}': {e}")
    return errors


def compute_match_score(profile_a: Profile, profile_b: Profile) -> float:
    """
    Simple scoring (0-100) based on:
      - Shared interests (40 pts max)
      - Age within each other's preferred range (30 pts)
      - Location (same parish/country) (20 pts)
      - Gender preference compatibility (10 pts)
    """
    score = 0.0

    # 1. Shared interests
    interests_a = {i.name for i in profile_a.interests}
    interests_b = {i.name for i in profile_b.interests}
    shared = interests_a & interests_b
    total_unique = interests_a | interests_b
    if total_unique:
        score += (len(shared) / len(total_unique)) * 40

    # 2. Age compatibility
    age_a = profile_a.age or 0
    age_b = profile_b.age or 0
    a_ok = (profile_a.preferred_age_min or 18) <= age_b <= (profile_a.preferred_age_max or 99)
    b_ok = (profile_b.preferred_age_min or 18) <= age_a <= (profile_b.preferred_age_max or 99)
    if a_ok and b_ok:
        score += 30
    elif a_ok or b_ok:
        score += 15

    # 3. Location proximity (same parish = 20, same country = 10)
    if profile_a.parish and profile_b.parish and \
       profile_a.parish.lower() == profile_b.parish.lower():
        score += 20
    elif profile_a.country and profile_b.country and \
         profile_a.country.lower() == profile_b.country.lower():
        score += 10

    # 4. Gender/looking-for compatibility
    def wants(pref, gender):
        return pref in ('any', gender)

    if wants(profile_a.looking_for or 'any', profile_b.gender or '') and \
       wants(profile_b.looking_for or 'any', profile_a.gender or ''):
        score += 10

    return round(score, 1)


# ============================================================
# Auth Endpoints
# ============================================================

@app.route('/api/v1/auth/register', methods=['POST'])
def register():
    """Register a new user and create their initial profile stub."""
    data = request.get_json(silent=True) or request.form
    form = RegistrationForm(data=data)

    if not form.validate():
        return jsonify({'errors': form_errors(form)}), 400

    # Check uniqueness
    if User.query.filter_by(email=form.email.data.lower()).first():
        return jsonify({'error': 'Email already registered.'}), 409
    if User.query.filter_by(username=form.username.data).first():
        return jsonify({'error': 'Username already taken.'}), 409

    user = User(
        username=form.username.data,
        email=form.email.data.lower(),
    )
    user.set_password(form.password.data)
    db.session.add(user)
    db.session.flush()  # get user.id before commit

    profile = Profile(
        user_id=user.id,
        first_name=form.first_name.data,
        last_name=form.last_name.data,
        date_of_birth=form.date_of_birth.data,
        gender=form.gender.data,
        looking_for=form.looking_for.data,
    )
    db.session.add(profile)
    db.session.commit()

    token = generate_token(user.id)
    return jsonify({
        'message': 'Registration successful.',
        'token': token,
        'user': user.to_dict(),
    }), 201


@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    """Authenticate user and return JWT."""
    data = request.get_json(silent=True) or request.form
    form = LoginForm(data=data)

    if not form.validate():
        return jsonify({'errors': form_errors(form)}), 400

    user = User.query.filter_by(email=form.email.data.lower()).first()
    if not user or not user.check_password(form.password.data):
        return jsonify({'error': 'Invalid email or password.'}), 401

    token = generate_token(user.id)
    return jsonify({
        'message': 'Login successful.',
        'token': token,
        'user': user.to_dict(),
    }), 200


@app.route('/api/v1/auth/logout', methods=['POST'])
@token_required
def logout():
    """Logout (client-side token removal; endpoint confirms action)."""
    return jsonify({'message': 'Logged out successfully.'}), 200


# ============================================================
# Profile Endpoints
# ============================================================

@app.route('/api/v1/profiles', methods=['GET'])
@token_required
def get_profiles():
    """
    Browse / discover profiles with integrated troubleshooting logs.
    """
    form = SearchForm(data=request.args)
    me = g.current_user


    # Base query: public profiles, not own
    query = Profile.query.filter(
        Profile.user_id != me.id,
        Profile.is_public == True
    )
    

    # Exclude users already liked/passed
    acted_ids = db.session.query(Like.liked_id).filter(Like.liker_id == me.id)
    query = query.filter(~Profile.user_id.in_(acted_ids))
    

    # Exclude blocked users (both directions)
    from app.models import Block as BlockModel
    blocked_by_me = db.session.query(BlockModel.blocked_id).filter(BlockModel.blocker_id == me.id)
    blocking_me   = db.session.query(BlockModel.blocker_id).filter(BlockModel.blocked_id == me.id)
    query = query.filter(~Profile.user_id.in_(blocked_by_me))
    query = query.filter(~Profile.user_id.in_(blocking_me))

    # Text search
    q = request.args.get('q', '').strip()
    if q:
        like_q = f'%{q}%'
        query = query.filter(
            db.or_(
                Profile.first_name.ilike(like_q),
                Profile.last_name.ilike(like_q),
                Profile.bio.ilike(like_q),
                Profile.occupation.ilike(like_q),
            )
        )

    # Location filters
    parish  = request.args.get('parish', '').strip()
    country = request.args.get('country', '').strip()
    if parish:
        query = query.filter(Profile.parish.ilike(f'%{parish}%'))
    if country:
        query = query.filter(Profile.country.ilike(f'%{country}%'))

    # Gender filter
    gender = request.args.get('gender', '').strip()
    if gender:
        query = query.filter(Profile.gender == gender)

    # Interest filter
    interests_raw = request.args.get('interests', '').strip()
    if interests_raw:
        interest_names = [i.strip() for i in interests_raw.split(',') if i.strip()]
        for name in interest_names:
            query = query.filter(
                Profile.interests.any(Interest.name.ilike(f'%{name}%'))
            )

    # Execute query
    profiles = query.all()
    print(f"DEBUG: Profiles returned from Database query: {len(profiles)}")

    # Age filter (computed in Python)
    try:
        age_min = int(request.args.get('age_min', 18))
        age_max = int(request.args.get('age_max', 99))
    except (ValueError, TypeError):
        age_min, age_max = 18, 99

    # Check if age calculation is failing
    final_profiles = []
    for p in profiles:
        if p.age is not None and age_min <= p.age <= age_max:
            final_profiles.append(p)
        else:
            reason = "Age is None" if p.age is None else f"Age {p.age} out of range"
            print(f"DEBUG: Filtering out Profile ID {p.id} ({p.first_name}) because: {reason}")

    # Compute match scores
    my_profile = me.profile
    results = []
    for p in final_profiles:
        d = p.to_dict()
        d['match_score'] = compute_match_score(my_profile, p) if my_profile else 0.0
        results.append(d)

    # Sort
    sort_by = request.args.get('sort', 'match_score')
    if sort_by == 'match_score':
        results.sort(key=lambda x: x['match_score'], reverse=True)
    else:  # newest
        results.sort(key=lambda x: x['created_at'] or '', reverse=True)

    return jsonify({'profiles': results, 'total': len(results)}), 200

@app.route('/api/v1/profiles/<int:user_id>', methods=['GET'])
@token_required
def get_profile(user_id):
    """Get a single user's profile."""
    profile = Profile.query.filter_by(user_id=user_id).first_or_404()
    is_own = (g.current_user.id == user_id)
    if not is_own and not profile.is_public:
        return jsonify({'error': 'This profile is private.'}), 403
    return jsonify(profile.to_dict(include_private=is_own)), 200


@app.route('/api/v1/profiles/<int:user_id>', methods=['PUT'])
@token_required
def update_profile(user_id):
    """Update own profile (includes photo upload)."""
    if g.current_user.id != user_id:
        return jsonify({'error': 'Forbidden.'}), 403

    profile = Profile.query.filter_by(user_id=user_id).first_or_404()

    # Support both JSON and multipart/form-data
    if request.content_type and 'multipart' in request.content_type:
        form = ProfileForm(request.form)
    else:
        form = ProfileForm(data=request.get_json(silent=True) or request.form)

    # Update scalar fields if provided
    fields = [
        'first_name', 'last_name', 'bio', 'parish', 'city', 'country',
        'latitude', 'longitude', 'occupation', 'education_level',
        'preferred_age_min', 'preferred_age_max', 'preferred_radius',
        'looking_for',
    ]
    json_data = request.get_json(silent=True) or {}
    form_data = request.form

    for field in fields:
        value = json_data.get(field) or form_data.get(field)
        if value is not None:
            # Cast numeric fields
            if field in ('latitude', 'longitude'):
                try:
                    value = float(value)
                except (ValueError, TypeError):
                    continue
            elif field in ('preferred_age_min', 'preferred_age_max', 'preferred_radius'):
                try:
                    value = int(value)
                except (ValueError, TypeError):
                    continue
            setattr(profile, field, value)

    # is_public
    is_public_val = json_data.get('is_public') or form_data.get('is_public')
    if is_public_val is not None:
        if isinstance(is_public_val, bool):
            profile.is_public = is_public_val
        else:
            profile.is_public = str(is_public_val).lower() not in ('false', '0', 'no')

    # Interests (comma-separated string or JSON array)
    interests_raw = json_data.get('interests') or form_data.get('interests')
    if interests_raw is not None:
        if isinstance(interests_raw, list):
            names = interests_raw
        else:
            names = [n.strip() for n in interests_raw.split(',') if n.strip()]
        new_interests = []
        for name in names:
            interest = Interest.query.filter_by(name=name).first()
            if not interest:
                interest = Interest(name=name)
                db.session.add(interest)
            new_interests.append(interest)
        profile.interests = new_interests

    # Photo upload — use Cloudinary when credentials are configured (production),
    # fall back to local disk otherwise (development).
    photo = request.files.get('photo')
    if photo and photo.filename and allowed_file(photo.filename):
        if app.config.get('CLOUDINARY_CLOUD_NAME'):
            import cloudinary.uploader
            result = cloudinary.uploader.upload(
                photo,
                folder='driftdater/profiles',
                public_id=f"user_{user_id}",
                overwrite=True,
                resource_type='image',
            )
            profile.photo_filename = result['secure_url']
        else:
            ext = photo.filename.rsplit('.', 1)[1].lower()
            filename = f"user_{user_id}_{uuid.uuid4().hex}.{ext}"
            upload_dir = os.path.abspath(app.config['UPLOAD_FOLDER'])
            os.makedirs(upload_dir, exist_ok=True)
            photo.save(os.path.join(upload_dir, filename))
            profile.photo_filename = filename

    profile.updated_at = datetime.now(timezone.utc)
    db.session.commit()

    return jsonify({
        'message': 'Profile updated.',
        'profile': profile.to_dict(include_private=True),
    }), 200


# ============================================================
# Like / Pass / Matching
# ============================================================

@app.route('/api/v1/profiles/<int:target_user_id>/like', methods=['POST'])
@token_required
def like_or_pass(target_user_id):
    """Like or pass on a profile. Creates a Match if mutual."""
    me = g.current_user

    if me.id == target_user_id:
        return jsonify({'error': 'You cannot like your own profile.'}), 400

    target = db.session.get(User, target_user_id)
    if not target:
        return jsonify({'error': 'User not found.'}), 404

    data = request.get_json(silent=True) or request.form
    action = (data.get('action') or 'like').lower()
    if action not in ('like', 'pass'):
        return jsonify({'error': "action must be 'like' or 'pass'."}), 400

    # Upsert like record
    existing = Like.query.filter_by(liker_id=me.id, liked_id=target_user_id).first()
    if existing:
        existing.action = action
        existing.created_at = datetime.now(timezone.utc)
    else:
        existing = Like(liker_id=me.id, liked_id=target_user_id, action=action)
        db.session.add(existing)

    match_created = False
    match_obj = None

    # Check for mutual match
    if action == 'like':
        reverse = Like.query.filter_by(
            liker_id=target_user_id, liked_id=me.id, action='like'
        ).first()
        if reverse:
            # Ensure canonical order (smaller id first) to avoid duplicates
            u1, u2 = (me.id, target_user_id) if me.id < target_user_id \
                     else (target_user_id, me.id)
            match_obj = Match.query.filter_by(user1_id=u1, user2_id=u2).first()
            if not match_obj:
                match_obj = Match(user1_id=u1, user2_id=u2)
                db.session.add(match_obj)
                match_created = True

    db.session.commit()

    response = {
        'message': f"Action '{action}' recorded.",
        'action': action,
        'match': match_obj.to_dict(me.id) if match_obj else None,
        'is_new_match': match_created,
    }
    return jsonify(response), 200


@app.route('/api/v1/matches', methods=['GET'])
@token_required
def get_matches():
    """Return all mutual matches for the current user."""
    me = g.current_user
    matches = Match.query.filter(
        db.or_(Match.user1_id == me.id, Match.user2_id == me.id)
    ).order_by(Match.created_at.desc()).all()

    return jsonify({
        'matches': [m.to_dict(me.id) for m in matches],
        'total': len(matches),
    }), 200


# ============================================================
# Messages
# ============================================================

@app.route('/api/v1/matches/<int:match_id>/messages', methods=['GET'])
@token_required
def get_messages(match_id):
    """Get message history for a match."""
    me = g.current_user
    match = db.session.get(Match, match_id)
    if not match:
        return jsonify({'error': 'Match not found.'}), 404
    if me.id not in (match.user1_id, match.user2_id):
        return jsonify({'error': 'Forbidden.'}), 403

    messages = Message.query.filter_by(match_id=match_id) \
                             .order_by(Message.created_at.asc()).all()
    return jsonify({
        'messages': [m.to_dict() for m in messages],
        'total': len(messages),
    }), 200


@app.route('/api/v1/matches/<int:match_id>/messages', methods=['POST'])
@token_required
def send_message(match_id):
    """Send a message to a matched user."""
    me = g.current_user
    match = db.session.get(Match, match_id)
    if not match:
        return jsonify({'error': 'Match not found.'}), 404
    if me.id not in (match.user1_id, match.user2_id):
        return jsonify({'error': 'You are not part of this match.'}), 403

    data = request.get_json(silent=True) or request.form
    body = (data.get('body') or '').strip()
    if not body:
        return jsonify({'error': 'Message body cannot be empty.'}), 400
    if len(body) > 2000:
        return jsonify({'error': 'Message too long (max 2000 chars).'}), 400

    msg = Message(match_id=match_id, sender_id=me.id, body=body)
    db.session.add(msg)
    db.session.commit()

    return jsonify({'message': msg.to_dict()}), 201


@app.route('/api/v1/conversations', methods=['GET'])
@token_required
def get_conversations():
    """
    Return a conversation list: each match with the latest message
    and the other user's profile summary.
    """
    me = g.current_user
    matches = Match.query.filter(
        db.or_(Match.user1_id == me.id, Match.user2_id == me.id)
    ).order_by(Match.created_at.desc()).all()

    conversations = []
    for m in matches:
        latest = Message.query.filter_by(match_id=m.id) \
                               .order_by(Message.created_at.desc()).first()
        other = m.other_user(me.id)
        conversations.append({
            'match_id': m.id,
            'matched_at': m.created_at.isoformat() if m.created_at else None,
            'other_profile': other.profile.to_dict() if (other and other.profile) else None,
            'latest_message': latest.to_dict() if latest else None,
        })

    return jsonify({'conversations': conversations}), 200


# ============================================================
# Favourites
# ============================================================

@app.route('/api/v1/favourites', methods=['GET'])
@token_required
def get_favourites():
    """List bookmarked profiles."""
    me = g.current_user
    favs = Favourite.query.filter_by(user_id=me.id) \
                           .order_by(Favourite.created_at.desc()).all()
    return jsonify({
        'favourites': [f.profile.to_dict() for f in favs],
        'total': len(favs),
    }), 200


@app.route('/api/v1/favourites/<int:profile_id>', methods=['POST'])
@token_required
def add_favourite(profile_id):
    """Bookmark a profile."""
    me = g.current_user
    profile = db.session.get(Profile, profile_id)
    if not profile:
        return jsonify({'error': 'Profile not found.'}), 404

    existing = Favourite.query.filter_by(user_id=me.id, profile_id=profile_id).first()
    if existing:
        return jsonify({'message': 'Already in favourites.'}), 200

    fav = Favourite(user_id=me.id, profile_id=profile_id)
    db.session.add(fav)
    db.session.commit()
    return jsonify({'message': 'Added to favourites.'}), 201


@app.route('/api/v1/favourites/<int:profile_id>', methods=['DELETE'])
@token_required
def remove_favourite(profile_id):
    """Remove a bookmarked profile."""
    me = g.current_user
    fav = Favourite.query.filter_by(user_id=me.id, profile_id=profile_id).first()
    if not fav:
        return jsonify({'error': 'Not in favourites.'}), 404

    db.session.delete(fav)
    db.session.commit()
    return jsonify({'message': 'Removed from favourites.'}), 200


# ============================================================
# Interests (reference data)
# ============================================================

@app.route('/api/v1/interests', methods=['GET'])
def get_interests():
    """Return all available interests."""
    interests = Interest.query.order_by(Interest.name).all()
    return jsonify({'interests': [i.to_dict() for i in interests]}), 200


# ============================================================
# File Serving
# ============================================================

@app.route('/api/v1/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded profile photos using absolute path."""
    upload_dir = os.path.abspath(app.config['UPLOAD_FOLDER'])
    return send_from_directory(upload_dir, filename)


# ============================================================
# Utility / SPA catch-all
# ============================================================

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    """Serve the Vue SPA for all non-API routes.

    Flask serves exact static asset paths (JS/CSS chunks, images) directly from
    dist/, and falls back to dist/index.html so Vue Router handles client-side
    navigation.  API routes should never reach here because they are registered
    above with explicit /api/v1/... prefixes.
    """
    from app import DIST_DIR
    # Safety net: if an /api/ path somehow falls through, return 404 JSON.
    if path.startswith('api/'):
        return jsonify({'error': 'Not found.'}), 404

    # dist/ may not exist in pure-API dev mode (no `npm run build` run yet).
    dist_index = os.path.join(DIST_DIR, 'index.html')
    if not os.path.isfile(dist_index):
        return jsonify({'message': 'DriftDater API', 'version': '1.0'}), 200

    # Serve the exact file if it exists (Vite asset chunks, favicon, etc.)
    if path:
        target = os.path.join(DIST_DIR, path)
        if os.path.isfile(target):
            return send_from_directory(DIST_DIR, path)

    # Everything else: hand off to Vue Router via index.html
    return send_from_directory(DIST_DIR, 'index.html')





@app.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Resource not found.'}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({'error': 'Method not allowed.'}), 405


@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error.'}), 500


# ============================================================
# Report & Block  (Optional Feature #1)
# ============================================================

from app.models import Report, Block   # noqa – imported here to avoid circular at top

@app.route('/api/v1/users/<int:target_id>/report', methods=['POST'])
@token_required
def report_user(target_id):
    """Report another user for moderation review."""
    me = g.current_user
    if me.id == target_id:
        return jsonify({'error': 'Cannot report yourself.'}), 400

    target = db.session.get(User, target_id)
    if not target:
        return jsonify({'error': 'User not found.'}), 404

    data   = request.get_json(silent=True) or request.form
    reason  = (data.get('reason') or '').strip()
    details = (data.get('details') or '').strip()

    if reason not in ('spam', 'harassment', 'fake', 'inappropriate', 'other'):
        return jsonify({'error': "reason must be one of: spam, harassment, fake, inappropriate, other"}), 400

    existing = Report.query.filter_by(reporter_id=me.id, reported_id=target_id).first()
    if existing:
        return jsonify({'message': 'Already reported.'}), 200

    report = Report(reporter_id=me.id, reported_id=target_id,
                    reason=reason, details=details)
    db.session.add(report)
    db.session.commit()
    return jsonify({'message': 'Report submitted. Our team will review it.'}), 201


@app.route('/api/v1/users/<int:target_id>/block', methods=['POST'])
@token_required
def block_user(target_id):
    """Block a user — they won't appear in browse or be able to message you."""
    me = g.current_user
    if me.id == target_id:
        return jsonify({'error': 'Cannot block yourself.'}), 400

    existing = Block.query.filter_by(blocker_id=me.id, blocked_id=target_id).first()
    if existing:
        return jsonify({'message': 'Already blocked.'}), 200

    block = Block(blocker_id=me.id, blocked_id=target_id)
    db.session.add(block)
    db.session.commit()
    return jsonify({'message': 'User blocked.'}), 201


@app.route('/api/v1/users/<int:target_id>/block', methods=['DELETE'])
@token_required
def unblock_user(target_id):
    """Unblock a previously blocked user."""
    me = g.current_user
    block = Block.query.filter_by(blocker_id=me.id, blocked_id=target_id).first()
    if not block:
        return jsonify({'error': 'Not blocked.'}), 404
    db.session.delete(block)
    db.session.commit()
    return jsonify({'message': 'User unblocked.'}), 200


@app.route('/api/v1/blocks', methods=['GET'])
@token_required
def get_blocks():
    """List all users you have blocked."""
    me     = g.current_user
    blocks = Block.query.filter_by(blocker_id=me.id).all()
    return jsonify({
        'blocked': [
            {'user_id': b.blocked_id,
             'username': b.blocked.username if b.blocked else None,
             'blocked_at': b.created_at.isoformat() if b.created_at else None}
            for b in blocks
        ]
    }), 200


# ============================================================
# Admin Dashboard  (Optional Feature #2)
# ============================================================

def admin_required(f):
    """Simple admin guard: user with id=1 is considered admin (demo)."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not g.current_user or g.current_user.id != 1:
            return jsonify({'error': 'Admin access required.'}), 403
        return f(*args, **kwargs)
    return decorated


@app.route('/api/v1/admin/stats', methods=['GET'])
@token_required
@admin_required
def admin_stats():
    """Site-wide statistics for admin dashboard."""
    total_users    = User.query.count()
    total_profiles = Profile.query.count()
    total_matches  = Match.query.count()
    total_messages = Message.query.count()
    total_reports  = Report.query.filter_by(status='pending').count()
    total_likes    = Like.query.filter_by(action='like').count()

    # New users last 7 days
    from datetime import timedelta
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    new_users = User.query.filter(User.created_at >= week_ago).count()

    return jsonify({
        'total_users':    total_users,
        'total_profiles': total_profiles,
        'total_matches':  total_matches,
        'total_messages': total_messages,
        'pending_reports': total_reports,
        'total_likes':    total_likes,
        'new_users_7d':   new_users,
    }), 200


@app.route('/api/v1/admin/reports', methods=['GET'])
@token_required
@admin_required
def admin_reports():
    """List all reports for moderation."""
    status  = request.args.get('status', 'pending')
    reports = Report.query.filter_by(status=status)\
                          .order_by(Report.created_at.desc()).all()
    return jsonify({'reports': [r.to_dict() for r in reports]}), 200


@app.route('/api/v1/admin/reports/<int:report_id>', methods=['PUT'])
@token_required
@admin_required
def update_report(report_id):
    """Update a report status (reviewed/dismissed)."""
    report = db.session.get(Report, report_id)
    if not report:
        return jsonify({'error': 'Report not found.'}), 404

    data   = request.get_json(silent=True) or {}
    status = data.get('status', '').strip()
    if status not in ('reviewed', 'dismissed'):
        return jsonify({'error': "status must be 'reviewed' or 'dismissed'"}), 400

    report.status = status
    db.session.commit()
    return jsonify({'message': f'Report marked as {status}.', 'report': report.to_dict()}), 200


@app.route('/api/v1/admin/users', methods=['GET'])
@token_required
@admin_required
def admin_users():
    """List all users with profile summaries."""
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify({
        'users': [
            {**u.to_dict(),
             'profile': u.profile.to_dict() if u.profile else None}
            for u in users
        ]
    }), 200


@app.route('/api/v1/admin/users/<int:uid>', methods=['DELETE'])
@token_required
@admin_required
def admin_delete_user(uid):
    """Delete a user and all their data (admin only)."""
    if uid == g.current_user.id:
        return jsonify({'error': 'Cannot delete your own admin account.'}), 400
    user = db.session.get(User, uid)
    if not user:
        return jsonify({'error': 'User not found.'}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': f'User {uid} deleted.'}), 200