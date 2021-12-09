
import re
from netaddr import *
import argparse
ip_regex = "^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$"
CIDR_regex = "^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(?:/\d\d?)+$"

def is_range(target):
    ips = target.split("-")
    return len(ips) == 2 and re.search(ip_regex, ips[0]) is not None and re.search(ip_regex, ips[1]) is not None

def parse_targets(raw_targets):
    results = set()
    for target in raw_targets:
        if re.search(CIDR_regex, target):
            ips = set(IPRange(IPNetwork(target).first, IPNetwork(target).last))
            results = results.union(set(map(ip_object_to_string, ips)))
        elif re.search(ip_regex, target):
            results.add(target)
        elif is_range(target):
            try:
                ips = target.split("-")
                ip_start = IPAddress(ips[0])
                ip_end = IPAddress(ips[1])
                results = results.union(set(map(ip_object_to_string, IPRange(ip_start, ip_end))))
            except Exception as e:
                print(e)
                continue
        else:
            results.add(target)
    return results

def check_positive(value):
    integer_value = int(value)
    if integer_value <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return integer_value

def ip_object_to_string(ip):
    return str(ip)
