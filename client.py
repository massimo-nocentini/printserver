
import asyncio
import socket
import sys

HOST, PORT = "localhost", 9100
data = " ".join(sys.argv[1:])

async def tcp_echo_client(message, loop):

    reader, writer = await asyncio.open_connection(HOST, PORT, loop=loop)

    print('Send: %r' % message)
    writer.write(message.encode())
    await writer.drain()
    writer.close()

    data = await reader.read()
    print('Received: %r' % data.decode())

    print('Close the socket')
    writer.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(tcp_echo_client(message=data, loop=loop))
loop.close()
