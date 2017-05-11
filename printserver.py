
import socketserver, json, tempfile, subprocess

def make_handler(command_template, association):

    port, printer_name = association

    class TCPPrintHandler(socketserver.BaseRequestHandler):

        def handle(self):
            data = []
            while True:
                chunk = self.request.recv(1024)
                if not chunk: 
                    break
                data.append(chunk)

            data = b''.join(data)

            print("{} wrote:\n{}".format(self.client_address, data.strip()))
            self.do_print(data) # do the processing

            self.request.sendall(b'request accepted, dude!')

        def do_print(self, data):
            with tempfile.NamedTemporaryFile() as temp:
                temp.write(data)
                temp.flush()
                command = command_template.format(filename=temp.name, printer_name=printer_name)
                if port == 9100:
                    subprocess.run(['cat', temp.name])
                else:
                    subprocess.run(command.split(' '))
            
            print('Print command executed: {}'.format(command))

    return TCPPrintHandler # pay attention, the *class* object is required, not an instance of it

#________________________________________________________________________ 


def start_server(HOST="127.0.0.1"):

    with open('printers_conf.json', 'r') as conf_file:
        conf = json.load(conf_file)
        command_template = conf['print_command']
        associations = {line['port']:line['printer'] for line in conf['queues']}
        print('Server configuration:\n{}'.format(json.dumps(conf, indent=4)))

    for port, printer in associations.items():
        with socketserver.TCPServer((HOST, port), make_handler(command_template, (port, printer))) as server:
            server.serve_forever()


if __name__ == "__main__":
    try:
        start_server()
    except KeyboardInterrupt:
        print('server shutdown')



