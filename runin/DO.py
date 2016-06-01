import requests

def get(TOKEN, endpoint):
    return requests.get("https://api.digitalocean.com/v2/{}".format(endpoint),
                        headers={"Authorization": "Bearer {}".format(TOKEN)}
                        ).json()

def post(TOKEN, endpoint, data=None):
    return requests.post("https://api.digitalocean.com/v2/{}".format(endpoint),
                         headers={"Authorization": "Bearer {}".format(TOKEN)},
                         data=data
                         ).json()

def delete(TOKEN, endpoint):
    return requests.delete("https://api.digitalocean.com/v2/{}".format(endpoint),
                           headers={"Authorization": "Bearer {}".format(TOKEN)}
                           ).json()

def get_token_from_file():
    try:
        with open(os.path.expanduser("~/.DO-token")) as f:
            return f.read().strip()
    except (IOError, FileNotFoundError):
        return None

def get_token():
    return os.getenv("DO_TOKEN") or get_token_from_file() or input(os.path.expanduser(
"""Please set your DigitalOcean personal access token as either:
* $DO_TOKEN
* ~/.DO-token
* or enter it below as a temporary measure
Use Ctrl-C to exit : """))

def get_regions():
    return {d["slug"]: d for d in DO_get(TOKEN, "/regions")["regions"]}

def get_ssh_keys():
    return {d["name"] if d["name"] else d["public_key"].split()[-1]: d for d in DO_get(TOKEN, "/account/keys")["ssh_keys"]}
