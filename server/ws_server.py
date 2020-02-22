import asyncio
from aiohttp import web
import aiohttp
import logging
import ssl
import os
import json
import random
from argparse import ArgumentParser
from argparse import ArgumentDefaultsHelpFormatter

async def send_hallo(ws):
    try:
        await ws.send_str("HELLO")
        return True
    except Exception as e:
        logger.error("exception", e)
        return False

async def recv_id(ws):
    try:
        msg = await ws.receive(timeout=1)
    except asyncio.TimeoutError:
        return False
    logger.debug(f"type={msg.type}")
    if msg.type == aiohttp.WSMsgType.TEXT:
        client_id = msg.data
        logger.debug(f"client_id {cliend_id}")
        return True
    elif msg.type == aiohttp.WSMsgType.ERROR:
        logger.error("ws connection closed with exception {}"
                     .format(ws.exception()))
        return False

async def session(ws):
    msg = json.dumps({
            "x":random.choice(vecs),
            "y":random.choice(vecs),
            "z":random.choice(vecs)
            })
    if opt.debug:
        logger.debug(msg)
    await ws.send_str(msg)
    await asyncio.sleep(1)
    return True

async def ws_handler(request):
    ws = web.WebSocketResponse()
    logger.info("ws session is prepared.")
    await ws.prepare(request)
    logger.info("ws session starts.")
    ret = await send_hallo(ws)
    if ret is not True:
        return
    ret = await recv_id(ws)
    if ret is not True:
        return

    while True:
        result = await session(ws)
        if not result:
            break

    logger.info("ws session closed")
    return ws

ap = ArgumentParser(
        description="a WS server for UnityWSClientTest.",
        epilog="this is the tail story.",
        formatter_class=ArgumentDefaultsHelpFormatter)
ap.add_argument("-s", "--scale",
                action="store", dest="scale", type=float, default=1.,
                help="specify a scale of the vector.")
ap.add_argument("-t", "--interval",
                action="store", dest="interval", type=int, default=1,
                help="specify an interval to publish the data.")
ap.add_argument("--server-cert-key",
                action="store", dest="server_cert_key",
                help="specify a file containing the cert, key and chain.")
ap.add_argument("--client-auth",
                action="store_true", dest="client_auth",
                help="enable to require a client cert.")
ap.add_argument("-d", action="store_true", dest="debug",
                help="enable debug mode.")
opt = ap.parse_args()

logger = logging.getLogger(__name__)
if opt.debug:
    logger_level = logging.DEBUG
else:
    logger_level = logging.INFO
logging.basicConfig(level=logger_level,
                    format="%(asctime)s" + logging.BASIC_FORMAT)

vecs = [-opt.scale,0,opt.scale]

app = web.Application()
app.add_routes([web.get("/ws", ws_handler)])

ssl_context = None
if opt.server_cert_key:
    if opt.client_auth:
        pass
    else:
        ssl_context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(opt.server_cert_key)

loop = asyncio.get_event_loop()
handler = app.make_handler()
f = loop.create_server(handler, "0.0.0.0", 8080, ssl=ssl_context)
srv = loop.run_until_complete(f)
logger.info("serving on", srv.sockets[0].getsockname())
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    loop.run_until_complete(handler.finish_connections(1.0))
    srv.close()
    loop.run_until_complete(srv.wait_closed())
    loop.run_until_complete(app.finish())
loop.close()
