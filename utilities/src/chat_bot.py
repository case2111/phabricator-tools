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
import shlex

_TYPE_KEY = "type"
_MSG_ID_KEY = "messageID"
_BOT_CALL = "!"


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
        lastMessage = {}
        try:
            await websocket.send(json.dumps(connect))
            conph.updatethread(ctx.bots, "online in: " + room_phid)
            while q.empty():
                raw = await websocket.recv()
                msg = json.loads(raw)
                lastMessage = msg
                if _TYPE_KEY in msg:
                    data_type = msg[_TYPE_KEY]
                    if data_type != "message":
                        continue
                if _MSG_ID_KEY not in msg:
                    print("missing message id")
                    continue
                msg_id = msg[_MSG_ID_KEY]
                with rlock:
                    all_msgs = conph.querytransaction_by_phid_last(room_phid,
                                                                   last)
                    for m in all_msgs:
                        if str(m) == str(msg_id):
                            selected = all_msgs[m]
                            if selected['transactionType'] != "core:comment":
                                continue
                            authored = selected["authorPHID"]
                            is_admin = authored in admins
                            comment = selected["transactionComment"]
                            is_all = comment.startswith(_BOT_CALL + "all ")
                            is_user = False
                            for alias in [user, bot.named]:
                                if comment.startswith(alias + " "):
                                    is_user = True
                                    break
                            if not is_all and not is_user:
                                continue
                            parts = shlex.split(comment)
                            if bot.room is None:
                                bot.room = selected["roomID"]
                            if is_user or (is_admin and is_all):
                                bot.go(parts[1],
                                       parts[2:],
                                       is_admin,
                                       is_all)
        except Exception as e:
            print(str(e))
            print(json.dumps(lastMessage))
            q.put(1)


def _bot(host, token, last, lock, bot_type, controls):
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
        bot.named = _BOT_CALL + bot_type
        print("{0} in rooms {1} {2}".format(bot_type,
                                            str(sorted(rooms.keys())),
                                            bot.id))
        for room in rooms:
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
        while os.path.exists(lock) and q.empty() and controls.empty():
            time.sleep(5)
    except Exception as e:
        print(e)
    if os.path.exists(lock):
        print('deleting lock')
        os.remove(lock)
    q.put(1)
    controls.put(0)


def main():
    """main entry."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, required=True)
    parser.add_argument("--lock", type=str, required=True)
    parser.add_argument("--last", type=str, required=True)
    for item in chat_fxn.Bot.BOT_TYPES:
        parser.add_argument("--" + item, type=str, required=False)
    args = parser.parse_args()
    bots = {}
    if args.monitor:
        bots[chat_fxn.Bot.MON_BOT_TYPE] = args.monitor
    if args.prune:
        bots[chat_fxn.Bot.PRUNE_BOT_TYPE] = args.prune
    if len(bots) == 0:
        print("at least one bot type must be enabled")
        exit(-1)
    q = Queue()

    def start_bot(host, token, last, lock, typed, q):
        _bot(host, token, last, lock + "." + typed, typed, q)
    workers = []
    for bot in bots:
        proc = Process(target=start_bot, args=((args.host),
                                               (bots[bot]),
                                               (args.last),
                                               (args.lock),
                                               (bot),
                                               (q)))
        proc.start()
        workers.append(proc)
    for worker in workers:
        worker.join()

if __name__ == '__main__':
    main()
