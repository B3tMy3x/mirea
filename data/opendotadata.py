import requests
import json


def getuserdata(account_id):
    r = f'https://api.opendota.com/api/players/{account_id}'
    r = requests.get(r)
    r = r.text
    r = json.loads(r)
    return [r['profile']['profileurl'], f'/static/ranks/{r["rank_tier"]}.webp', r['profile']['avatarfull']]
