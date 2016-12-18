#!/usr/bin/python
"""Chat bot implementation."""

import asyncio
import websockets
import argparse
import conduit
import json
import chat_fxn
import os
import time
from multiprocessing import Process, Queue
import threading
from datetime import datetime

async def _proc(ws_socket, ctx, q, bot):
    """Support websockets connection to handle chat and command exec."""
    rlock = threading.RLock()
    async with websockets.connect(ws_socket) as websocket:
        conph = ctx.get(chat_fxn.Context.CONPH)
        room_phid = ctx.get(chat_fxn.Context.ROOM_PHID)
        user_phid = ctx.get(chat_fxn.Context.BOT_USER_PHID)
        last = ctx.get(chat_fxn.Context.LAST_TRANS)
        user = ctx.get(chat_fxn.Context.BOT_USER)
        admins = ctx.get(chat_fxn.Context.ADMINS)
        connect = {}
        connect["command"] = "subscribe"
        connect["data"] = [room_phid, user_phid]
        try:
            await websocket.send(json.dumps(connect))
            conph.updatethread(ctx.bots, "online in: " + room_phid)
            while q.empty():
                raw = await websocket.recv()
                msg = json.loads(raw)
                msg_id = msg["messageID"]
                with rlock:
                    all_msgs = conph.querytransaction_by_phid_last(room_phid,
                                                                   last)
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
                            if bot.room is None:
                                bot.room = selected["roomID"]
                            uname = parts[0]
                            is_all = uname == "!all"
                            if uname == user or (is_admin and is_all):
                                bot.go(parts[1],
                                       parts[2:],
                                       is_admin,
                                       is_all)
        except Exception as e:
            print(str(e))
            q.put(1)


def _bot(host, token, last, lock, bot_type):
    """Bot setup and prep."""
    q = Queue()
    try:
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
            roles = check['roles']
            if "admin" in roles or "agent" in roles:
                admins.append(check['phid'])
        u_phid = u["phid"]
        user = u["userName"]
        ws_host = "ws" + host[4:] + "/ws/"
        rooms = c.querythread()
        procs = []
        bot = chat_fxn.bot(bot_type)
        print(bot_type)
        for room in rooms:
            print(room)
            r = rooms[room]
            ctx = chat_fxn.Context(factory)
            ctx.set(chat_fxn.Context.ROOM_PHID, r["conpherencePHID"])
            ctx.set(chat_fxn.Context.BOT_USER_PHID, u_phid)
            ctx.set(chat_fxn.Context.BOT_USER, "@" + user)
            ctx.set(chat_fxn.Context.LAST_TRANS, last)
            ctx.set(chat_fxn.Context.ADMINS, admins)
            ctx.set(chat_fxn.Context.STARTED, str(datetime.now()))
            ctx.set(chat_fxn.Context.LOCK, lock)
            bot.ctx = ctx

            def run(ws, context, queued, bot_obj):
                asyncio.get_event_loop().run_until_complete(_proc(ws,
                                                                  context,
                                                                  queued,
                                                                  bot_obj))
            proc = Process(target=run, args=((ws_host),
                                             (ctx),
                                             (q),
                                             (bot)))
            proc.daemon = True
            proc.start()
            procs.append(proc)
        while os.path.exists(lock) and q.empty():
            time.sleep(5)
    except Exception as e:
        print(e)
    if os.path.exists(lock):
        print('deleting lock')
        os.remove(lock)
    q.put(1)


def main():
    """main entry."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, required=True)
    parser.add_argument("--token", type=str, required=True)
    parser.add_argument("--lock", type=str, required=True)
    parser.add_argument("--last", type=str, required=True)
    parser.add_argument("--type", type=str, required=True)
    args = parser.parse_args()
    _bot(args.host, args.token, args.last, args.lock, args.type)

if __name__ == '__main__':
    main()
