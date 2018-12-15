from starlette.websockets import WebSocket
from . import DEFAULT_CHANNEL_LAYER
from starlette.types import Message, Receive, Scope, Send
from .exceptions import StopConsumer
import functools
from starlette import status
from .utils import await_many_dispatch
from .layers import get_channel_layer



class BaseWebSocketEndpoint:
    encoding = None  # May be "text", "bytes", or "json".

    def __init__(self, scope: Scope) -> None:
        assert scope["type"] == "websocket"
        self.scope = scope

    channel_layer_alias = DEFAULT_CHANNEL_LAYER

    # ASGI Callable
    async def __call__(self, receive: Receive, send: Send) -> None:

        websocket = WebSocket(self.scope, receive=receive, send=send)

        # overridable/Callable by subclasses
        await self.on_connect(websocket)

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

        if message["type"] == "websocket.receive":
            data = await self.decode(websocket, message)
            # await self.on_receive(websocket, data)
        elif message["type"] == "websocket.disconnect":
            close_code = int(message.get("code", status.WS_1000_NORMAL_CLOSURE))

        msg = {
            'type': message["type"],
            'data': data
        }

        print("msg = {}".format(msg))

        handler = getattr(self, get_handler_name(msg), None)
        if handler:
            await handler(msg)
        else:
            raise ValueError("No handler for message %s" % message["type"])

    async def on_connect(self, websocket: WebSocket) -> None:
        """Override to handle an incoming websocket connection"""
        await websocket.accept()


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
            if "bytes" not in message:
                await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA)
                raise RuntimeError(
                    "Expected JSON to be transferred as bytes websocket messages, but got text"
                )
            return json.loads(message["bytes"].decode("utf-8"))

        assert (
            self.encoding is None
        ), f"Unsupported 'encoding' attribute {self.encoding}"
        return message["text"] if "text" in message else message["bytes"]





    async def websocket_receive(self, message):
        """
        Called when a WebSocket frame is received.
        """
        await self.receive(text_data=message["text"])

    async def receive(self, text_data=None, bytes_data=None):
        """
        Called with a decoded WebSocket frame.
        """
        pass

    async def send(self, message):
        """
        Overideable/callable by subclasses
        """
        await self.send_base(message)


def get_handler_name(message):
    """
    Looks at message, check it has a sensible type, and return the handler name for that type
    """
    if 'type' not in message:
        raise ValueError("Incoming message has no 'type' attribute")
    if message["type"].startswith("_"):
        raise ValueError("Malformed type in message (leading underscore)")

    return message["type"].replace(".", "_")
