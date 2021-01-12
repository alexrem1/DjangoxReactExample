from django.shortcuts import render
from rest_framework import generics, status
from .serializers import RoomSerializer, CreateRoomSerializer, UpdateRoomSerializer
from .models import Room
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse

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


# send get request to endpoint to find if the user is in a room to get the code
class UserInRoom(APIView):
    def get(self, request, format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        # takes a python dictionary and serializes it using a json serializer and sends it back in the request
        data = {"code": self.request.session.get("room_code")}
        return JsonResponse(data, status=status.HTTP_200_OK)


class LeaveRoom(APIView):
    def post(self, request, format=None):
        # when user leaves the room I check to see if the room code's in the session. If it is I delete the room code from the user session and then check to see if they are hosting a room. If they are the room is deleted
        if "room_code" in self.request.session:
            self.request.session.pop("room_code")
            host_id = self.request.session.session_key
            room_results = Room.objects.filter(host=host_id)
            if len(room_results) > 0:
                room = room_results[0]
                room.delete()

        return Response({"Message": "Success"}, status=status.HTTP_200_OK)


class UpdateRoom(APIView):
    serializer_class = UpdateRoomSerializer

    def patch(self, request, format=None):
        # Check if theres an active session
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        # passing our data to the serializer to check if its valid
        serializer = self.serializer_class(data=request.data)
        # if data is valid we want to grab this information from the serializer
        if serializer.is_valid():
            guest_can_pause = serializer.data.get("guest_can_pause")
            votes_to_skip = serializer.data.get("votes_to_skip")
            code = serializer.data.get("code")

            # find room with code obtained above
            queryset = Room.objects.filter(code=code)
            # no room found
            if not queryset.exists():
                return Response(
                    {"Message": "Room not found."}, status=status.HTTP_404_NOT_FOUND
                )

            # if there is a room, we need to make sure the person updating the room is the host.
            room = queryset[0]
            user_id = self.request.session.session_key
            if room.host != user_id:
                return Response(
                    {"msg": "You are not the host of this room."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # if the user_id = room.host
            room.guest_can_pause = guest_can_pause
            room.votes_to_skip = votes_to_skip
            room.save(update_fields=["guest_can_pause", "votes_to_skip"])
            return Response(RoomSerializer().data, status=status.HTTP_201_CREATED)

        return Response(
            {"Bad Request": "Invalid Data..."}, status=status.HTTP_400_BAD_REQUEST
        )
