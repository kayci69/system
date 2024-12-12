from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
import json
from channels.layers import get_channel_layer

connected_superadmins = set()  # In-memory set to track connected superusers

class SuperUserConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        
        if user.is_authenticated and getattr(user, 'account_type', None) == "superadmin":
            print("-----------------------")
            print("CONNECTED  "+user.username)
            print("-----------------------")
            await self.accept()
            connected_superadmins.add(self.channel_name)
        else:
            await self.close()

    async def disconnect(self, close_code):
        print("-----------------------")
        print("DIS CONNECTEDED  ")
        print("-----------------------")
        connected_superadmins.discard(self.channel_name)

    async def broadcast_message(self, event):
        # Send the broadcast message to the WebSocket client
        await self.send(text_data=json.dumps(event["message"]))


# Generic function to broadcast a message
def broadcast_to_superusers(message):
    """
    Broadcast a JSON message to all connected superadmins.
    """
    channel_layer = get_channel_layer()  # Get the channel layer instance
    for channel_name in connected_superadmins:
        async_to_sync(channel_layer.send)(
            channel_name,
            {
                "type": "broadcast_message",
                "message": message
            },
        )