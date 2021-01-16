from django.shortcuts import render, redirect
from .credentials import REDIRECT_URI, CLIENT_ID, CLIENT_SECRET
from rest_framework.views import APIView
from requests import Request, post
from rest_framework import status
from rest_framework.response import Response
from .util import update_or_create_user_tokens, is_spotify_authenticated

# the flow is: from our frontend, we are going to call AuthURL (API endpoint). Then we take the URL returned to us and then redirect to that page. Then that url, once the user is done authorizing us, we will redirect to the spotify_callback. From said function, we'll send a request for the tokens, store the tokens and then redirect back to the application to the


class AuthURL(APIView):
    def get(self, request, format=None):
        scopes = "user-read-playback-state user-modify-playback-state user-read-currently-playing"

        # preparing a url that we can go to, to authenticate the spotify URL
        url = (
            Request(
                "GET",
                "https://accounts.spotify.com/authorize",
                params={
                    "scope": scopes,
                    "response_type": "code",
                    "redirect_uri": REDIRECT_URI,
                    "client_id": CLIENT_ID,
                },
            )
            .prepare()
            .url
        )

        return Response({"url": url}, status=status.HTTP_200_OK)


# after we send this request to the url we need a callback or url the info gets returned to
# callback gets access and refresh token
def spotify_callback(request, format=None):
    # this code is how we authenticate the user
    code = request.GET.get("code")
    error = request.GET.get("error")

    # send a request back to the spotify account service to get the access token and refresh token
    response = post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
        # response converts to json
    ).json()

    # send a request using a code to get access to the below
    access_token = response.get("access_token")
    token_type = response.get("token_type")
    refresh_token = response.get("refresh_token")
    expires_in = response.get("expires_in")
    error = response.get("error")

    # now we need to store this token (multiple tokens for multiple users) - Create MODEL
    # as soon as we get access to the above we want to store it in the database (SPOTIFYTOKEN MODEL)
    if not request.session.exists(request.session.session_key):
        # if there's no session we must create one or it will create an error
        request.session.create()

    update_or_create_user_tokens(
        request.session.session_key, access_token, token_type, expires_in, refresh_token
    )

    return redirect("frontend:")


class IsAuthenticated(APIView):
    def get(self, request, format=None):
        is_authenticated = is_spotify_authenticated(self.request.session.session_key)

        return Response({"status": is_authenticated}, status=status.HTTP_200_OK)