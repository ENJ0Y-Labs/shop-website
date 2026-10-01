from flask import Blueprint, current_app, jsonify, redirect, request, session, url_for

from ..errors import APIError
from ..models import User
from ..services.auth_service import authenticate_user, create_email_user, serialize_user, sign_in, sign_out
from ..services.google_oauth import get_google_client, handle_google_callback
from ..utils.validation import require_json, required_string, validate_email, validate_password

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/register")
def register():
    data = require_json(request)
    email = validate_email(required_string(data, "email", 255))
    password = validate_password(data.get("password"))
    name = required_string(data, "name", 255)

    user = create_email_user(email, password, name)
    sign_in(user, session)
    return jsonify({"user": serialize_user(user)}), 201


@auth_bp.post("/login")
def login():
    data = require_json(request)
    email = validate_email(required_string(data, "email", 255))
    password = validate_password(data.get("password"))

    user = authenticate_user(email, password)
    sign_in(user, session)
    return jsonify({"user": serialize_user(user)})


@auth_bp.post("/logout")
def logout():
    sign_out(session)
    return "", 204


@auth_bp.get("/me")
def me():
    user_id = session.get("user_id")
    if not user_id:
        raise APIError("Authentication required.", 401, "unauthenticated")

    user = db_user = User.query.filter_by(id=user_id).first()
    if not db_user:
        sign_out(session)
        raise APIError("Authentication required.", 401, "unauthenticated")

    return jsonify({"user": serialize_user(user)})


@auth_bp.get("/google")
def google_login():
    client = get_google_client()
    redirect_uri = current_app.config["GOOGLE_REDIRECT_URI"]
    return client.authorize_redirect(redirect_uri)


@auth_bp.get("/google/callback")
def google_callback():
    user = handle_google_callback(session)
    frontend_url = current_app.config["CORS_ORIGINS"][0]
    return redirect(f"{frontend_url}/?auth=success")
