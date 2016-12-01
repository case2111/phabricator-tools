#!/usr/bin/python
"""Chat bot implementation."""

import asyncio
import websockets
import argparse
import conduit
import json
import commands
import os
import time
from multiprocessing import Process, Queue
import threading
from datetime import datetime

async def _proc(ws_socket, ctx, q, debug):
    """Support websockets connection to handle chat in and command exec."""
    rlock = threading.RLock()
    async with websockets.connect(ws_socket) as websocket:
        conph = ctx.get(commands.Context.CONPH)
        room_phid = ctx.get(commands.Context.ROOM_PHID)
        user_phid = ctx.get(commands.Context.BOT_USER_PHID)
        last = ctx.get(commands.Context.LAST_TRANS)
        user = ctx.get(commands.Context.BOT_USER)
        admins = ctx.get(commands.Context.ADMINS)
        connect = {}
        connect["command"] = "subscribe"
        connect["data"] = [room_phid, user_phid]
        room_id = None
        await websocket.send(json.dumps(connect))
        while q.empty():
            raw = await websocket.recv()
            msg = json.loads(raw)
            msg_id = msg["messageID"]
            with rlock:
                all_msgs = conph.querytransaction_by_phid_last(room_phid, last)
                for m in all_msgs:
                    if str(m) == str(msg_id):
                        selected = all_msgs[m]
                        if selected['transactionType'] != "core:comment":
                            continue
                        authored = selected["authorPHID"]
                        if authored == user_phid:
                            continue
                        is_admin = authored in admins
                        comment = selected["transactionComment"]
                        parts = comment.split(" ")
                        if room_id is None:
                            room_id = selected["roomID"]
                        if parts[0] == user:
                            commands.execute(parts[1],
                                             parts[2:],
                                             room_id,
                                             ctx,
                                             debug,
                                             is_admin)


def _bot(host, token, last, lock, debug):
    """Bot setup and prep."""
    if os.path.exists(lock):
        print("{0} already exists...".format(lock))
        return
    os.mknod(lock)
    factory = conduit.Factory()
    factory.host = host
    factory.token = token
    c = factory.create(conduit.Conpherence)
    users = factory.create(conduit.User)
    u = users.whoami()
    admins = []
    a = users.query()
    for check in a:
        if "admin" in check['roles']:
            admins.append(check['phid'])
    u_phid = u["phid"]
    user = u["userName"]
    ws_host = "ws" + host[4:] + "/ws/"
    rooms = c.querythread()
    q = Queue()
    procs = []
    for room in rooms:
        r = rooms[room]
        ctx = commands.Context(factory)
        ctx.set(commands.Context.ROOM_PHID, r["conpherencePHID"])
        ctx.set(commands.Context.BOT_USER_PHID, u_phid)
        ctx.set(commands.Context.BOT_USER, "@" + user)
        ctx.set(commands.Context.LAST_TRANS, last)
        ctx.set(commands.Context.ADMINS, admins)
        ctx.set(commands.Context.LOCK_FILE, lock)
        ctx.set(commands.Context.STARTED, str(datetime.now()))

        def run(ws, context, queued, debugging):
            asyncio.get_event_loop().run_until_complete(_proc(ws,
                                                              context,
                                                              queued,
                                                              debugging))
        proc = Process(target=run, args=((ws_host), (ctx), (q), (debug)))
        proc.daemon = True
        proc.start()
        procs.append(proc)
    while os.path.exists(lock):
        time.sleep(5)
    q.put(1)


def main():
    """main entry."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, required=True)
    parser.add_argument("--token", type=str, required=True)
    parser.add_argument("--last", type=str, required=True)
    parser.add_argument("--lock", type=str, required=True)
    parser.add_argument("--debug", action='store_true')
    args = parser.parse_args()
    _bot(args.host, args.token, args.last, args.lock, args.debug)


if __name__ == '__main__':
    main()
