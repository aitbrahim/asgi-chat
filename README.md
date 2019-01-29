# ASGI-chat

add websocket broadcast layer for [Starletter](https://github.com/encode/starlette) using Redis as a backend.

Most of the code inspired from [django-channels](https://github.com/django/channels)

Running application locally:
open two separate terminal to emulate clients sending messages

- The first termial (T-1) will connect to connect to the websocket endpoint and listen for any comming messsages from other client.

```
T-1#> docker-compose build
T-1#> docker-compose up -d
T-1#> docker-compose exec client_1 bash
T-1#> python
>>> import websocket
>>> ws = websocket.WebSocket()
>>> ws.connect("ws://server:8000")
>>> ws.recv()
```

- The second terminal (T-2) will connect to websocket endpoint and send a message.
```
T-2#> docker-compose exec client_2 bash
T-2#> python
>>> import websocket
>>> ws = websocket.WebSocket()
>>> ws.connect("ws://server:8000")
>>> import json
>>> ws.send(json.dumps({"try": "message sent from client_1"}))
```

- Any client listen in the websocket endpoint should receive the message

```
>>> ws.recv()
'{"try": "message sent from client_2"}'
```
