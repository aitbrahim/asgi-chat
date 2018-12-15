import uvicorn
from starlette.websockets import WebSocket
from chat.consumer import WebSocketEndpoint


class App(WebSocketEndpoint):

    async def on_connect(self, websocket: WebSocket) -> None:
        """Override to handle an incoming websocket connection"""
        await websocket.accept()

    async def receive(self, text_data=None, bytes_data=None):
        """Override to handle an incoming websocket message"""

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': text_data
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
