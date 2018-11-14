import random
import sys
import time
import signal

sys.path.append('/Library/Application Support/MWorks/Scripting/Python')

from mworks.conduit import IPCClientConduit

conduit = None


def cbRespond(event):
    global conduit
    enterT = time.clock()

    if event.data == 'ping':
        conduit.send_data(conduit.reverse_codec['messageVar'], 'response')

        print 'Elapsed in cbRespond: %5.3f ms' \
            % (1000*(time.clock() - enterT))
        sys.stdout.flush()

def main():
    if len(sys.argv) > 1:
        # Client-side conduit: resource name is a script argument
        resource_name = sys.argv[1]
    else:
        # Server-side conduit: resource name is set in the experiment
        resource_name = 'server_conduit'

    global conduit

    conduit = IPCClientConduit(resource_name)
    conduit.initialize()

    try:
        # register callback to respond to changes in messageVar
        conduit.register_callback_for_name('messageVar', cbRespond)

        print 'Ready.'
        sys.stdout.flush()
        signal.pause()
                
    except KeyboardInterrupt:
        pass
    finally:
        conduit.finalize()


if __name__ == '__main__':
    main()
