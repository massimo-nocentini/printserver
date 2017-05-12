
import asyncio
import socket
import sys

HOST, PORT = "localhost", 9100
filename = " ".join(sys.argv[1:])

async def tcp_echo_client(message, loop):

    reader, writer = await asyncio.open_connection(HOST, PORT, loop=loop)

    with open(filename, 'rb') as contents:
        data = b''.join(contents)
        size = len(data)
        size_str = ('{} bytes'.format(size) if size < 2**10 
                    else '{} KBytes'.format(size//2**10) if size < 2**20 
                    else '{} MBytes'.format(size//2**20))
        print('Send {} from file {}'.format(size_str, filename))
        #writer.write(message.encode()) # calling method `encode` produces and error for raw binary data such as zip files
        writer.write(data)
        writer.write_eof()
        await writer.drain()

    data = await reader.read(1024)
    print('Received: %r' % data.decode())

    print('Close the socket')
    writer.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(tcp_echo_client(filename, loop=loop))
loop.close()
