import time
import argparse
import docker
from queue import Queue
import threading
import signal
import multiprocessing
import docker
from bpsInputUtils import check_positive, parse_targets
from scanInitiator.ScanInitiator import ScanInitiator


client = docker.from_env()
manager = multiprocessing.Manager()
containers = manager.list()
final_results = manager.list()
removeQ = Queue()
is_stopped = multiprocessing.Value('i', False)


def remove_threader():
    while True:
        worker = removeQ.get()
        try:
            container = client.containers.get(worker)
            container.stop()
        except:
            pass
        removeQ.task_done()


def signal_handler(signum, frame):
    is_stopped.value = True
    for x in range(num_of_processes):
        t = threading.Thread(target=remove_threader)
        t.daemon = True
        t.start()
    for container in containers:
        print(container)
        removeQ.put(container)
    removeQ.join()

if __name__ == '__main__':
    signal.signal(signal.SIGTERM, signal_handler)
    processes = []
    start_time = time.time()
    parser = argparse.ArgumentParser(description='Usage: Scanner.py -t <targets1> ... <targetN>')
    parser.add_argument('-t', '--targets', help='target URL/IP/CIDR and IP range (IP range should be in the following '
                                                'format: 0.0.0.0-255.255.255.255)', required=True, nargs="+",
                        default=[])
    parser.add_argument('-r', '--rate', help='Integer that indicates the number of threads that will be used',
                        required=False, default=1,
                        type=check_positive)
    parser.add_argument('-a', '--alive', help='Consider hosts as alive, default is true', action='store_true',
                        required=False, default=False)
    parser.add_argument('-m', '--max-retries', help='Number of time to try reconnect to socket on failure',
                        type=check_positive,
                        required=False, default=1)
    parser.add_argument('-d', '--debug', help='Show debug prints',
                        action='store_true',
                        required=False, default=False)
    parser.add_argument('-p', '--top-ports', help='Scan 1000 top ports only. default is all 65535 ports.',
                        required=False, default=False)
    parser.add_argument('-i', '--image-name', help='Image name to run (located in BrunoPortScanner folder)',
                        required=True)
    parser.add_argument('-st', '--socket-timeout', help='Socket connection timeout',
                        type=check_positive,
                        required=False, default=1)

    args = vars(parser.parse_args())
    addresses = list(args['targets'])
    num_of_processes = args['rate']
    consider_alive = args['alive']
    max_retries = args['max_retries']
    top_ports = args['top_ports'] == 'TOP' 
    debug = args['debug']
    socket_timeout = args['socket_timeout']
    image_name = args['image_name']
    initiator = ScanInitiator(
        list(parse_targets(addresses)),
        top_ports,
        num_of_processes,
        consider_alive,
        debug,
        socket_timeout,
        client,
        image_name
    )
    initiator.start(is_stopped, processes, final_results, containers)
    if debug:
        print(f"Scan done in: {(time.time() - start_time)} Seconds")
