import ast
from urllib3.connectionpool import xrange
from multiprocessing import Process
import json



class ScanInitiator:
    def __init__(self, targets, top_ports, num_of_processes, consider_alive, debug, socket_timeout, client, image_name):
        self.targets = targets
        self.top_ports = top_ports
        self.num_of_processes = num_of_processes
        self.consider_alive = consider_alive
        self.debug = debug
        self.socket_timeout = socket_timeout
        self.client = client
        self.image_name = image_name

    def start(self, is_stopped, processes, final_results, containers):
        for i in xrange(0, len(self.targets), self.num_of_processes):
            if not is_stopped.value:
                batch = self.targets[i:i + self.num_of_processes]
                for address in batch:
                    process = Process(
                        target=runner,
                        args=(
                            address,
                            self.top_ports,
                            self.consider_alive,
                            self.debug,
                            self.socket_timeout,
                            containers,
                            final_results,
                            self.client,
                            self.image_name)
                        )
                    process.start()
                    processes.append(process)
                for processObj in processes:
                    processObj.join()
            processes.clear()
        res = []
        for i in final_results:
            as_dict = ast.literal_eval(i.decode().rstrip())
            res.append(as_dict)
        print(json.dumps(res))

def runner(address, ports_to_scan, consider_alive, debug, socket_timeout, containers, final_results, client, image_name):
    host_scanner = client.containers.run(image_name,
                                         command=f"-t {address} "
                                                 f'{"-a" if consider_alive else ""} '
                                                 f"-st {socket_timeout} "
                                                 f"-r 400 "
                                                 f"{'-d' if debug else ''} "
                                                 f"{'-p' if ports_to_scan else ''} ",
                                         user="root",
                                         mem_limit="128m",
                                         detach=True,
                                         remove=True)
    containers.append(host_scanner.id)
    for line in host_scanner.logs(stream=True):
        if len(line) > 0:
            final_results.append(line)
