from .models import SpotifyToken
from django.utils import timezone
from datetime import timedelta
from .credentials import CLIENT_ID, CLIENT_SECRET
from requests import post

# check to see if there's any tokens associated with the user
def get_user_tokens(session_id):
    user_tokens = SpotifyToken.objects.filter(user=session_id)
    if user_tokens.exists():
        return user_tokens[0]
    else:
        return None


# saves our token in a new model or update an existing model with new tokens
def update_or_create_user_tokens(
    session_id, access_token, token_type, expires_in, refresh_token
):
    tokens = get_user_tokens(session_id)
    # expires in will be numeric (3600=1hour) but we need to convert it into a timestap ie current time + an hour
    expires_in = timezone.now() + timedelta(seconds=expires_in)

    # if tokens we will update existing ones
    if tokens:
        tokens.access_token = access_token
        tokens.refresh_token = refresh_token
        tokens.expires_in = expires_in
        tokens.token_type = token_type
        tokens.save(
            update_fields=["access_token", "refresh_token", "expires_in", "token_type"]
        )
    # else we create the new tokens
    else:
        tokens = SpotifyToken(
            user=session_id,
            access_token=access_token,
            refresh_token=refresh_token,
            token_type=token_type,
            expires_in=expires_in,
        )
        tokens.save()


# check if a user authenticated (if the token is expired)
def is_spotify_authenticated(session_id):
    tokens = get_user_tokens(session_id)
    # if the current expiry has passed lets refresh the token
    if tokens:
        expiry = tokens.expires_in
        if expiry <= timezone.now():
            refresh_spotify_token(session_id)

        return True

    # if we dont get anything from the database, we're not authenticated
    return False


def refresh_spotify_token(session_id):
    refresh_token = get_user_tokens(session_id).refresh_token

    response = post(
        "https://accounts.spotify.com/api/token",
        data={
            # we are sending a refresh token
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
    ).json()

    # returns new tokens
    access_token = response.get("access_token")
    token_type = response.get("token_type")
    expires_in = response.get("expires_in")
    refresh_token = response.get("refresh_token")

    update_or_create_user_tokens(
        session_id, access_token, token_type, expires_in, refresh_token
    )
