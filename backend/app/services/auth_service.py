import uuid

from werkzeug.security import check_password_hash, generate_password_hash

from ..errors import APIError
from ..extensions import db
from ..models import User


def serialize_user(user):
    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "profile_picture_url": user.profile_picture_url,
    }


def authenticate_user(email, password):
    user = db.session.query(User).filter_by(email=email).first()
    if not user or not user.password_hash or not check_password_hash(user.password_hash, password):
        raise APIError("Invalid email or password.", 401, "invalid_credentials")
    return user


def create_email_user(email, password, name):
    if db.session.query(User).filter_by(email=email).first():
        raise APIError("An account with this email already exists.", 409, "email_exists")

    user = User(
        id=uuid.uuid4(),
        email=email,
        password_hash=generate_password_hash(password),
        name=name,
    )
    db.session.add(user)
    db.session.commit()
    return user


def sign_in(user, session):
    session.clear()
    session["user_id"] = str(user.id)
    session["auth_method"] = "email"
    session.permanent = False


def sign_out(session):
    session.clear()
