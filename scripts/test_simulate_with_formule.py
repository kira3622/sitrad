#!/usr/bin/env python
import json
import ssl
import urllib.request
import urllib.parse
from urllib.error import HTTPError

BASE_URL = "http://127.0.0.1:8001/cost-calculation/api"


def http_json(method: str, url: str, data: dict | None = None):
    ctx = ssl.create_default_context()
    if data is not None:
        body = urllib.parse.urlencode(data).encode("utf-8")
    else:
        body = None
    req = urllib.request.Request(url, data=body, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
    try:
        with urllib.request.urlopen(req, context=ctx) as resp:
            txt = resp.read().decode(resp.headers.get_content_charset() or "utf-8")
            return resp.status, json.loads(txt)
    except HTTPError as e:
        txt = e.read().decode("utf-8", errors="replace")
        print(f"HTTPError {e.code} on {url}:\n{txt[:800]}")
        raise


def pick_formule_id_from_orders():
    status, data = http_json("GET", f"{BASE_URL}/ordres-production/")
    if status != 200:
        raise RuntimeError(f"Failed to get orders: status={status}")
    if isinstance(data, list):
        orders = data
    elif isinstance(data, dict):
        orders = data.get("data", [])
    else:
        raise RuntimeError(f"Unexpected orders payload type: {type(data)}")
    for o in orders:
        fid = o.get("formule_id")
        if fid:
            return fid, o.get("formule_nom")
    raise RuntimeError("No formule_id found in orders list")


def main():
    formule_id, formule_nom = pick_formule_id_from_orders()
    print(f"Using formule from orders: {formule_nom} (id={formule_id})")
    status, data = http_json("POST", f"{BASE_URL}/simulate/", {
        "formule_id": formule_id,
        "quantite": 1,
        "unite_mesure": "m3"
    })
    print("Status:", status)
    print("Response:", json.dumps(data, ensure_ascii=False, indent=2)[:1200])
    if isinstance(data, dict) and data.get('success') and isinstance(data.get('calcul'), dict):
        calc = data['calcul']
        total = calc.get('cout_total')
        unit = calc.get('cout_unitaire')
        print(f"Total: {total} € | Unitaire: {unit} €/m3")
    else:
        raise RuntimeError("Unexpected response structure")


if __name__ == "__main__":
    main()