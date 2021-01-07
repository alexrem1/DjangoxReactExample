from django.shortcuts import render
from rest_framework import generics, status
from .serializers import RoomSerializer, CreateRoomSerializer
from .models import Room
from rest_framework.views import APIView
from rest_framework.response import Response

# Create your views here.
class RoomView(generics.CreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer


# APIView allows me to override default methods eg get, post, put. When that type of request is sent to the APIView, it'll automatically dispatch it to the correct method.

# when we call GetRoom(APIView) with a get request,we need to pass a parameter in the url called code which is equal to the room that we're trying to get
class GetRoom(APIView):
    serializer_class = RoomSerializer
    lookup_url_kwarg = "code"

    def get(self, request, format=None):
        # looking for "code" parameter in the url to look up room with the code.
        code = request.GET.get(self.lookup_url_kwarg)
        if code != None:
            room = Room.objects.filter(code=code)
            if len(room) > 0:
                # data is a python dictionary extracted from the serialized room
                data = RoomSerializer(room[0]).data
                # host is the session key. If the user requesting the session equals the host of the room they're the host
                data["is_host"] = self.request.session.session_key == room[0].host
                return Response(data, status=status.HTTP_200_OK)

            # if no room found:
            return Response(
                {"Room Not Found": "Invalid Room Code."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {"Bad Request": "Code paramater not found in request"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class JoinRoom(APIView):
    lookup_url_kwarg = "code"

    def post(self, request, format=None):
        # Check if theres an active session
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        # .data because post request
        code = request.data.get(self.lookup_url_kwarg)
        if code != None:
            room_result = Room.objects.filter(code=code)
            if len(room_result) > 0:
                room = room_result[0]
                # make a note on the backend that a user is in the room
                self.request.session["room_code"] = code
                return Response({"message": "Room Joined!"}, status=status.HTTP_200_OK)

        return Response(
            {"Bad Request": "Invalid Room Code"}, status=status.HTTP_400_BAD_REQUEST
        )

        return Response(
            {"Bad Request": "Invalid post data, did not find a code key"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class CreateRoomView(APIView):
    serializer_class = CreateRoomSerializer

    def post(self, request, format=None):
        # if the current request/user has an active session with the web server, if they dont not I will create it, if they do give data to serializer to check if the data sent was valid
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        serializer = self.serializer_class(data=request.data)
        # if the 2 fields we defined in serializers.py, guest_can_pause and votes_to_skip, are valid and are in the data that was sent as part of the post request. Room can then be created.
        if serializer.is_valid():
            guest_can_pause = serializer.data.get("guest_can_pause")
            votes_to_skip = serializer.data.get("votes_to_skip")
            host = self.request.session.session_key
            # Check database to see if there's any rooms that has the same host trying to create another room
            queryset = Room.objects.filter(host=host)
            # if so, grab active room and update settings
            if queryset.exists():
                room = queryset[0]
                room.guest_can_pause = guest_can_pause
                room.votes_to_skip = votes_to_skip
                room.save(update_fields=["guest_can_pause", "votes_to_skip"])
                self.request.session["room_code"] = room.code
            # If room isn't being updated
            else:
                room = Room(
                    host=host,
                    guest_can_pause=guest_can_pause,
                    votes_to_skip=votes_to_skip,
                )
                room.save()
                self.request.session["room_code"] = room.code

            # We still want to return a response to tell whoever sent this to use wether this was valid or not. Response contains the room they created with the extra info eg time created. We need to serialize the room object we created/updated.
            return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)
