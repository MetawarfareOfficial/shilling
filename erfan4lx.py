import asyncio
import os
import sys
import pyrogram
from pyrogram import Client
from pyrogram.errors import RPCError, FloodWait

CLIENTS_DIR = './clients'
TEXT_FILENAME = 'text.txt'
CHATS_FILENAME = 'groups.txt'
MAX_EXPORT_COUNT = 5

pyrogram.session.Session.notice_displayed = True


async def send(app, chat_ids, msg):
    for chat_id in chat_ids:
        try:
            await app.join_chat(str(chat_id))
            await app.send_message(str(chat_id), msg)
            print(f' - Client({app.session_name}): send to {chat_id}')
        except FloodWait as e:
            await asyncio.sleep(e.x + 1)
        except Exception as e:
            print(f' - Client({app.session_name}) Error: {e}')
        await asyncio.sleep(0.5)


async def main(t=0):
    if os.path.exists(CHATS_FILENAME):
        with open(CHATS_FILENAME) as file:
            chats = [line.replace("\r", "").replace("\n", "") for line in file.readlines()]
    else:
        return print(f'- File({CHATS_FILENAME}) NOT EXISTS')
    if not chats:
        return print(f'- NO CHAT-ID IN FILE({CHATS_FILENAME})')

    if os.path.exists(TEXT_FILENAME):
        with open(TEXT_FILENAME) as file:
            text = file.read()
    else:
        return print(f'- File({TEXT_FILENAME}) NOT EXISTS')
    if not text:
        return print(f'- NO TEXT IN FILE({TEXT_FILENAME})')

    print('\n- Start Clients:')

    clients = []
    tasks = []
    for f in os.listdir(CLIENTS_DIR):
        if not f.endswith(".session"):
            continue

        session_name = f.replace('.session', '')
        print(f'\n- Client({session_name})')
        client = Client(session_name, workdir=CLIENTS_DIR)
        try:
            await client.start()
            print(f' - Client({session_name}): Started')
        except RPCError as e:
            print(f' - Client({session_name}) Not Started: {e}')
            continue
        clients.append(client)
        tasks.append(asyncio.ensure_future(send(client, chats, text)))

    await asyncio.gather(*tasks)
    await asyncio.gather(*[client.stop() for client in clients])


async def corn_main(sleep_time):
    while True:
        await main()
        print(f'Sleep for {sleep_time} seconds')
        await asyncio.sleep(sleep_time)


async def add_client():
    session_name = input('Input session name: ')
    async with Client(session_name, workdir=CLIENTS_DIR) as new_client:
        print(f'- New Client {new_client.storage.database}')


async def usage():
    print('BAD ARGS')


if __name__ == "__main__":

    if not os.path.exists(CLIENTS_DIR):
        os.mkdir(CLIENTS_DIR)

    if len(sys.argv) == 1:
        func = main()
    elif len(sys.argv) == 2:
        if sys.argv[1].isdigit():
            func = corn_main(int(sys.argv[1]))
        elif sys.argv[1] == '--add':
            func = add_client()
        else:
            func = usage()
    else:
        func = usage()

    print('\nHere we go...\n')

    loop = asyncio.get_event_loop()
    loop.run_until_complete(func)
    loop.close()

    print('\nFinish!\n')
