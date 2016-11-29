#!/usr/bin/python
"""Chat bot implementation."""

import asyncio
import websockets
import argparse
import conduit
import json
import commands


async def _proc(ws_socket, ctx):
    """Support websockets connection to handle chat in and command exec."""
    async with websockets.connect(ws_socket) as websocket:
        conph = ctx.get(commands.Context.CONPH)
        room_phid = ctx.get(commands.Context.BOT_ROOM_PHID)
        user_phid = ctx.get(commands.Context.BOT_USER_PHID)
        last = ctx.get(commands.Context.LAST_TRANS)
        user = ctx.get(commands.Context.BOT_USER)
        connect = {}
        connect["command"] = "subscribe"
        connect["data"] = [room_phid, user_phid]
        await websocket.send(json.dumps(connect))
        while True:
            try:
                raw = await websocket.recv()
                msg = json.loads(raw)
                msg_id = msg["messageID"]
                all_msgs = conph.querytransaction_by_phid_last(room_phid, last)
                for m in all_msgs:
                    if str(m) == str(msg_id):
                        selected = all_msgs[m]
                        if selected["authorPHID"] == user_phid:
                            continue
                        comment = selected["transactionComment"]
                        parts = comment.split(" ")
                        if parts[0] == user:
                            commands.execute(parts[1],
                                             parts[2:],
                                             selected["roomID"],
                                             ctx)
            except KeyboardInterrupt:
                break


def _bot(host, token, room, last):
    """Bot setup and prep."""
    factory = conduit.Factory()
    factory.host = host
    factory.token = token
    c = factory.create(conduit.Conpherence)
    u = factory.create(conduit.User).whoami()
    u_phid = u["phid"]
    user = u["userName"]
    c_phid = c.querythread_by_id(room)[room]["conpherencePHID"]
    ws_host = "ws" + host[4:] + "/ws/"
    ctx = commands.Context()
    ctx.set(commands.Context.CONPH, c)
    ctx.set(commands.Context.BOT_ROOM, room)
    ctx.set(commands.Context.BOT_ROOM_PHID, c_phid)
    ctx.set(commands.Context.BOT_USER_PHID, u_phid)
    ctx.set(commands.Context.BOT_USER, "@" + user)
    ctx.set(commands.Context.LAST_TRANS, last)
    asyncio.get_event_loop().run_until_complete(_proc(ws_host, ctx))


def main():
    """main entry."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--room", type=str, required=True)
    parser.add_argument("--host", type=str, required=True)
    parser.add_argument("--token", type=str, required=True)
    parser.add_argument("--last", type=str, required=True)
    args = parser.parse_args()
    _bot(args.host, args.token, args.room, args.last)

if __name__ == '__main__':
    main()
