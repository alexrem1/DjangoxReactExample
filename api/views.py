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
                room.vote_to_skip = votes_to_skip
                room.save(update_fields=["guest_can_pause", "votes_to_skip"])
            # If room isn't being updated
            else:
                room = Room(
                    host=host,
                    guest_can_pause=guest_can_pause,
                    votes_to_skip=votes_to_skip,
                )
                room.save()

            # We still want to return a response to tell whoever sent this to use wether this was valid or not. Response contains the room they created with the extra info eg time created. We need to serialize the room object we created/updated.
            return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)
