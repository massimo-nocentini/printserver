
# a simple reworking of https://docs.python.org/3/library/asyncio-stream.html

import socketserver, json, tempfile, subprocess
from collections import defaultdict
import asyncio
from contextlib import suppress

def make_handler(command_template, association):

    port, printer_name = association

    queue = defaultdict(list)

    async def handler(reader, writer):

        while True:

            data = await reader.read(1024)
            client = writer.get_extra_info('peername')

            if data:
                queue[client].append(data)
                print("Received chunk{} from {}".format(data.decode(), client))
            else:
                whole_message = b''.join(queue[client])
                message = whole_message.decode()
                print("Complete data {} from {}".format(message, client))

                del queue[client]
                do_print(whole_message)

                writer.write(b'Request processed, bye')
                await writer.drain()

                break
                


    def do_print(data):
        with tempfile.NamedTemporaryFile() as temp:
            temp.write(data)
            temp.flush()
            command = command_template.format(filename=temp.name, printer_name=printer_name)
            if port == 9100:
                subprocess.run(['cat', temp.name])
            else:
                subprocess.run(command.split(' '))
        
        print('Print command executed: {}'.format(command))

    return handler

#________________________________________________________________________ 

def make_queues(loop):

    with open('printers_conf.json', 'r') as conf_file:
        conf = json.load(conf_file)
        command_template = conf['print_command']
        host = conf['host']
        associations = {line['port']:line['printer'] for line in conf['queues']}
        print('Server configuration:\n{}'.format(json.dumps(conf, indent=4)))

    return asyncio.gather(*[asyncio.start_server(make_handler(command_template, (port, printer)), host, port, loop=loop) 
                          for port, printer in associations.items()])

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    coros_pool = make_queues(loop)
    servers = loop.run_until_complete(coros_pool)

    # Serve requests until Ctrl+C is pressed
    print('Serving on sockets {}'.format(', '.join(str(s.sockets[0].getsockname()) for s in servers)))
    with suppress(KeyboardInterrupt):
        loop.run_forever()

    # Close the server
    for server in servers:
        server.close()
        loop.run_until_complete(server.wait_closed())

    loop.close()
    print("Server down.")



