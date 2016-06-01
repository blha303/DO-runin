#!/usr/bin/env python
from __future__ import print_function

import os
import subprocess
import argparse
import uuid
import sys
import runin.DO as DO

DEFAULT_IMAGE = "ubuntu-16-04-x64"

def match_keys(inp, p=False):
    """Takes a comma-separated string of key ids or fingerprints and returns a list of key ids"""
    _keys = []
    ssh_keys = DO.get_ssh_keys()
    for k in inp.split(","):
        done = False
        if k.isdigit():
            for _ in [s for s in ssh_keys if s["id"] == int(k)]:
                done = True
                _keys.append(_["fingerprint"])
        else:
            for _ in [s for s in ssh_keys if s["fingerprint"] == k]:
                done = True
                _keys.append(_["fingerprint"])
        if p and not done:
            print("Could not find a match for '{}', skipping".format(k), file=sys.stderr)
    return _keys

def main():
    parser = argparse.ArgumentParser(prog="runin", epilog="You must provide either -R/-S/-I, or -r")
    parser.add_argument("-R", "--list-regions", help="List available regions and exit", action="store_true")
    parser.add_argument("-S", "--list-ssh-keys", help="List available SSH keys and exit", action="store_true")
    parser.add_argument("-I", "--list-images", help="List available images and exit", action="store_true")
    parser.add_argument("-c", "--command", help="Run command. If none specified, opens a shell", default="")
    parser.add_argument("-r", "--region", help="Set region. Required")
    parser.add_argument("--name", help="Set droplet name. If not specified, a temporary name is generated", default=uuid.uuid4().hex)
    parser.add_argument("--size", help="Set droplet size. Defaults to 512mb", default="512mb")
    parser.add_argument("-s", "--ssh-keys", help="Set SSH keys. Comma separated list of numeric IDs or fingerprints. If not specified, a root password will be emailed", default="")
    parser.add_argument("-i", "--image", help="Set image. Defaults to " + DEFAULT_IMAGE, default=DEFAULT_IMAGE)
    parser.add_argument("--ipv6", help="Enable IPv6", action="store_true")
    parser.add_argument("--private-networking", help="Enable private networking", action="store_true")
    parser.add_argument("--shell", help="Run SSH using the less secure os.system, allowing usage of the created droplet in shell mode. Enabled automatically if -c is not provided", action="store_true")
    parser.add_argument("-k", "--keep", help="Keep server after disconnect", action="store_true")
    args = parser.parse_args()
    if args.list_regions:
        r = DO.get_regions(p=True)
        return 0
    if args.list_ssh_keys:
        s = DO.get_ssh_keys(p=True)
        return 0
    if args.list_images:
        i = DO.get_images(p=True)
        return 0
    regions = DO.get_regions()
    if args.region:
        if args.region not in regions:
            print("{} not a valid region. Use -R to list available regions".format(args.region), file=sys.stderr)
            return 1
        _keys = match_keys(args.ssh_keys)
        droplet = DO.new_droplet(region=args.region,
                                 name=args.name,
                                 size=args.size,
                                 ssh_keys=match_keys(args.ssh_keys, p=True),
                                 image=args.image,
                                 ipv6=args.ipv6,
                                 private_networking=args.private_networking)
        action = DO.get_action(droplet["links"]["actions"][0]["id"], p=True)
        if not action:
            print("Droplet creation errored. https://cloud.digitalocean.com/droplets", file=sys.stderr)
            return 2
        droplet["droplet"].update(action)
        ssh = ["ssh", "-oStrictHostKeyChecking=no", "root@" + droplet["droplet"]["networks"]["v4"][0]["ip_address"], args.command]
        if args.shell or not args.command:
            os.system(" ".join(["'{}'".format(a.replace("'", "\\'")) for a in ssh]))
        else:
            print(subprocess.check_output(ssh, shell=False))
        if not args.keep:
            if not DO.delete_droplet(droplet["droplet"]["id"]):
                print("Droplet deletion errored. https://cloud.digitalocean.com/droplets", file=sys.stderr)
                return 2
        else:
            print("Server is accessible at {}".format(droplet["droplet"]["networks"]["v4"][0]["ip_address"]))
        return 0
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())
