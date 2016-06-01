from __future__ import print_function
input = raw_input if hasattr(__builtins__, "raw_input") else input
import requests
import time
import uuid
import sys
import os
import socket

def get(TOKEN, endpoint):
    return requests.get("https://api.digitalocean.com/v2/{}".format(endpoint),
                        headers={"Authorization": "Bearer {}".format(TOKEN)}
                        ).json()

def post(TOKEN, endpoint, json=None):
    return requests.post("https://api.digitalocean.com/v2/{}".format(endpoint),
                         headers={"Authorization": "Bearer {}".format(TOKEN)},
                         json=json
                         ).json()

def delete(TOKEN, endpoint):
    return requests.delete("https://api.digitalocean.com/v2/{}".format(endpoint),
                           headers={"Authorization": "Bearer {}".format(TOKEN)}
                           ).status_code == requests.codes.no_content

def get_token_from_file():
    try:
        with open(os.path.expanduser("~/.DO-token")) as f:
            return f.read().strip()
    except (IOError, FileNotFoundError):
        return None

def get_token():
    try:
        return os.getenv("DO_TOKEN") or get_token_from_file() or input(os.path.expanduser(
"""Please set your DigitalOcean personal access token as either:
* $DO_TOKEN
* ~/.DO-token
* or enter it below as a temporary measure
Use Ctrl-C to exit : """))
    except KeyboardInterrupt:
        print(file=sys.stderr)
        sys.exit(130)

def get_regions(p=False):
    regions = get(get_token(), "/regions")["regions"]
    if p:
        _ = list(regions)
        for region in _:
            region["sizes"] = ",".join(sorted(region["sizes"]))
            region["features"] = "".join(s[0] for s in region["features"])
            print("{slug}: {name} ({features})   \t{sizes}".format(**region) + ("\tX" if not region["available"] else ""), file=sys.stderr)
    return {d["slug"]: d for d in regions}

def get_ssh_keys(p=False):
    keys = get(get_token(), "/account/keys")["ssh_keys"]
    if p:
        for key in keys:
            print("\t{id}: {name} ({fingerprint}):\n{public_key}".format(**key), file=sys.stderr)
    return keys

def get_images(p=False):
    images = get(get_token(), "/images")["images"]
    if p:
        print("Public:", file=sys.stderr)
        for image in [i for i in images if i["public"]]:
            print("{id}: {distribution} {name} ({slug})".format(**image), file=sys.stderr)
        print("Private:", file=sys.stderr)
        for image in [i for i in images if not i["public"]]:
            print("{id}: {distribution} {name}".format(**image), file=sys.stderr)
    return images

def get_action(id, p=False):
    i = 1
    while True:
        action = get(get_token(), "/actions/{}".format(id))["action"]
        if action["status"] == "completed":
            if action["resource_type"] == "droplet":
                break
            return True
        elif action["status"] == "errored":
            return False
        i = i+1 if i < 3 else 1
        if p:
            print("Waiting for action" + ("." * i) + (" " * (3-i)), end="\r", file=sys.stderr)
        time.sleep(3)
    droplet = get(get_token(), "/droplets/{}".format(action["resource_id"]))["droplet"]
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        i = i+1 if i < 3 else 1
        if p:
            print("Waiting for server to finish booting" + ("." * i) + (" " * (3-i)), file=sys.stderr, end="\r")
        if sock.connect_ex((droplet["networks"]["v4"][0]["ip_address"], 22)) == 0:
            break
        time.sleep(1)
    return droplet

def new_droplet(**kwargs):
    """ Arguments: https://developers.digitalocean.com/documentation/v2/#create-a-new-droplet """
    return post(get_token(), "/droplets", json=kwargs)

def delete_droplet(id):
    return delete(get_token(), "/droplets/{}".format(id))
