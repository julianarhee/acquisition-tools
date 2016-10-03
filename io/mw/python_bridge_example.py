import signal
import sys


# mworks
try:
    sys.path.append('/Library/Application Support/MWorks/Scripting/Python')
    #import mworks.data as mw
    from mworks.conduit import IPCClientConduit
except Exception as e:
    print("Please install mworks...")
    print e



def handle_event(event):
    sys.stdout.write('Got an event: code = %s, data = %r\n' %
                     (event.code, event.data))
    sys.stdout.flush()


def main():
    conduit_resource_name = sys.argv[1]

    client = IPCClientConduit(conduit_resource_name)
    client.initialize()
    try:
        client.register_callback_for_name('#announceStimulus', handle_event)
        signal.pause()  # Other threads are working; this one can sleep
    finally:
        client.finalize()


if __name__ == '__main__':
    main()