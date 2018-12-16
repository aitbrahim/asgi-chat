import uvicorn
import json
from starlette.websockets import WebSocket
from chat.consumer import WebSocketEndpoint


class App(WebSocketEndpoint):
    encoding = "json"

    async def on_connect(self, websocket: WebSocket) -> None:
        """Override to handle an incoming websocket connection"""
        await websocket.accept()

    async def receive(self, data):
        # Send message to room group
        if self.encoding == 'json':
            data = json.dumps(data)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': data
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        print("Got new chat message")
        message = event['message']

        await self.send({"type": "websocket.send", "text": message})

    # async def disconnect(self, close_code):
    #     # Leave room group
    #     await self.channel_layer.group_discard(
    #         self.room_group_name,
    #         self.channel_name
    #     )


app = App


if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000)
