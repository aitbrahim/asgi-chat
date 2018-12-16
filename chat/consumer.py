from starlette.websockets import WebSocket
from . import DEFAULT_CHANNEL_LAYER
from starlette.types import Message, Receive, Scope, Send
from .exceptions import StopConsumer
import functools
from .utils import await_many_dispatch
from .layers import get_channel_layer
import json
import typing
from starlette import status


class WebSocketEndpoint:
    encoding = None  # May be "text", "bytes", or "json".

    def __init__(self, scope: Scope) -> None:
        assert scope["type"] == "websocket"
        self.scope = scope

    channel_layer_alias = DEFAULT_CHANNEL_LAYER

    # ASGI Callable
    async def __call__(self, receive: Receive, send: Send) -> None:

        self.websocket = WebSocket(self.scope, receive=receive, send=send)

        # overridable/Callable by subclasses
        await self.on_connect(self.websocket)

        # save send method
        self.send_base = send

        # Initialize channel layer
        self.channel_layer = get_channel_layer(self.channel_layer_alias)

        if self.channel_layer is not None:

            # create new channel
            self.channel_name = await self.channel_layer.new_channel()

            """
            add the channel to group (broadcat), this it can be imprroved, by taking the group
            name from URLs, See django_channels for example.
            """
            self.room_name = 'asgi_room'
            self.room_group_name = 'chat_%s' % self.room_name

            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            # courotine that waiting for messgage received in self.channel_name
            self.channel_receive = functools.partial(
                self.channel_layer.receive, self.channel_name
            )

            # pass message in from channel layer or client to dispatch method
            try:
                if self.channel_layer is not None:
                    await await_many_dispatch(
                        [receive, self.channel_receive], self.dispatch
                    )
                else:
                    await await_many_dispatch([receive], self.dispatch)
            except StopConsumer:
                # exit cleanly
                pass

    async def dispatch(self, message):
        """
        Works out what to do with a messgae
        """
        handler = getattr(self, get_handler_name(message), None)
        if handler:
            await handler(message)
        else:
            raise ValueError("No handler for message %s" % message["type"])

    async def on_connect(self, websocket: WebSocket) -> None:
        """Override to handle an incoming websocket connection"""
        await websocket.accept()

    async def websocket_receive(self, message):
        """
        Called when a WebSocket frame is received. Decodes it and passes it
        to receive().
        """
        data = await self.decode(self.websocket, message)
        await self.receive(data)

    async def receive(self, data):
        """
        Called with a decoded WebSocket frame.
        """
        pass

    async def send(self, message):
        """
        Overideable/callable by subclasses
        """
        await self.send_base(message)

    async def websocket_disconnect(self, message):
        """
        Called when a WebSocket disconnect.
        """
        await self.on_disconnect(self.websocket, message["code"])

    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        """Override to handle a disconnecting websocket"""

    async def decode(self, websocket: WebSocket, message: Message) -> typing.Any:

        if self.encoding == "text":
            if "text" not in message:
                await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA)
                raise RuntimeError("Expected text websocket messages, but got bytes")
            return message["text"]

        elif self.encoding == "bytes":
            if "bytes" not in message:
                await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA)
                raise RuntimeError("Expected bytes websocket messages, but got text")
            return message["bytes"]

        elif self.encoding == "json":
            try:
                message_json = None
                if "text" in message:
                    message_json = json.loads(message["text"])
                elif message["bytes"]:
                    message_json = json.loads(message["bytes"].decode("utf-8"))
            except json.decoder.JSONDecodeError:
                await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA)
                raise RuntimeError("Malformed JSON data received.")
            else:
                return message_json

        assert (
            self.encoding is None
        ), f"Unsupported 'encoding' attribute {self.encoding}"
        return message["text"] if "text" in message else message["bytes"]


def get_handler_name(message):
    """
    Looks at message, check it has a sensible type, and return the handler name for that type
    """
    if 'type' not in message:
        raise ValueError("Incoming message has no 'type' attribute")
    if message["type"].startswith("_"):
        raise ValueError("Malformed type in message (leading underscore)")

    return message["type"].replace(".", "_")
