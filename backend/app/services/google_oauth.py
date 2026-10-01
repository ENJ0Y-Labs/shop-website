from authlib.integrations.flask_client import OAuth

from ..errors import APIError
from ..extensions import db
from ..models import User
from .auth_service import sign_in

oauth = OAuth()


def init_google_oauth(app):
    oauth.init_app(app)
    if not app.config.get("GOOGLE_CLIENT_ID") or not app.config.get("GOOGLE_CLIENT_SECRET"):
        return

    oauth.register(
        name="google",
        client_id=app.config["GOOGLE_CLIENT_ID"],
        client_secret=app.config["GOOGLE_CLIENT_SECRET"],
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )


def get_google_client():
    client = oauth.create_client("google")
    if client is None:
        raise APIError("Google sign-in is not configured.", 503, "google_not_configured")
    return client


def handle_google_callback(session):
    client = get_google_client()
    token = client.authorize_access_token()
    userinfo = token.get("userinfo")
    if not userinfo:
        userinfo = client.userinfo(token=token)

    email = (userinfo.get("email") or "").strip().lower()
    if not email or not userinfo.get("email_verified"):
        raise APIError("Google account email could not be verified.", 400, "google_email_unverified")

    google_id = userinfo.get("sub")
    if not google_id:
        raise APIError("Google account identity is missing.", 400, "google_identity_missing")

    user = db.session.query(User).filter_by(google_id=google_id).first()

    if not user:
        user = db.session.query(User).filter_by(email=email).first()
        if user:
            user.google_id = google_id
            user.profile_picture_url = userinfo.get("picture")
            if not user.name:
                user.name = userinfo.get("name") or email.split("@")[0]
        else:
            user = User(
                email=email,
                name=userinfo.get("name") or email.split("@")[0],
                google_id=google_id,
                profile_picture_url=userinfo.get("picture"),
            )
            db.session.add(user)

        db.session.commit()

    sign_in(user, session)
    return user
