# 

import numpy as np
import SocketServer
from threading import Thread

class service(SocketServer.BaseRequestHandler):
    def handle(self):
        self.data = 'dummy'
        print "Client connected with ", self.client_address
        while len(self.data):
            self.data = self.request.recv(1024).strip()
            print self.data
            self.request.sendall(self.data.upper())

        print "Client exited"
        self.request.close()


x = np.array([[55, 1000, 45], [20, 3, 10]])

class UDP_Interrupt(SocketServer.BaseRequestHandler):

    def setup(self):
        pass

    def handle(self):
        data = self.request[0].strip()
        print data
        socket = self.request[1]
        print "{}{} wrote:".format(self.client_address[0], self.client_address)
        print data
        print x
        socket.sendto(x.tostring('C'), self.client_address)
        #scipy.io.savemat('/Users/empire/Documents/MATLAB/hybridQuadSim/quaternionController/models/mapData.mat', mdict={'mapData': x})

    def finish(self):
        pass

class ThreadedUDPServer(SocketServer.ThreadingMixIn, SocketServer.UDPServer):

    pass


import optparse
parser = optparse.OptionParser()

parser.add_option('-p', '--port', action="store", dest="port",
                  default="1989", help="port no.")
parser.add_option('-h', '--host', action="store", dest="host",
                  default="", help="host IP")

if __name__ == "__main__":
    HOST = 140.247.178.213
    PORT = options.port
    map_server = ThreadedUDPServer((HOST, PORT), UDP_Interrupt)

    # terminate with Ctrl-C
    try:
        server_thread = Thread(target=map_server.serve_forever)
        server_thread.daemon = False
        server_thread.start()
        print "Server loop running in thread:", server_thread.name

    except KeyboardInterrupt:
        sys.exit(0)