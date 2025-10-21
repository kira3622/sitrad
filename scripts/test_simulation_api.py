import json
import ssl
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8001/cost-calculation/api"

payload = {
    "ciment_kg": 350,
    "prix_ciment_t": 120,
    "sable_kg": 700,
    "prix_sable_t": 20,
    "gravier_kg": 1100,
    "prix_gravier_t": 25,
    "eau_l": 180,
    "prix_eau_l": 0.002,
    "adjuvant_l": 2,
    "prix_adjuvant_l": 3,
    "kwh": 4,
    "prix_kwh": 0.18,
    "diesel_l": 0.25,
    "prix_diesel_l": 1.8,
    "heures": 0.03,
    "taux_horaire": 20,
    "maintenance": 1.5,
    "amortissement": 2.0,
    "frais_generaux": 3.0,
    "transport_interne": 1.0
}


def http_json(url: str, method: str = "GET", data: dict | None = None):
    headers = {"Content-Type": "application/json"}
    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, context=ctx) as resp:
            charset = resp.headers.get_content_charset() or "utf-8"
            txt = resp.read().decode(charset)
            return resp.status, json.loads(txt)
    except urllib.error.HTTPError as e:
        try:
            payload = e.read().decode("utf-8")
        except Exception:
            payload = str(e)
        return e.code, {"error": True, "message": payload}
    except Exception as e:
        return 0, {"error": True, "message": str(e)}


def expected_total(p: dict) -> float:
    # Convert kg to tonnes for unit prices per tonne
    ciment = (p["ciment_kg"] / 1000) * p["prix_ciment_t"]
    sable = (p["sable_kg"] / 1000) * p["prix_sable_t"]
    gravier = (p["gravier_kg"] / 1000) * p["prix_gravier_t"]
    eau = p["eau_l"] * p["prix_eau_l"]
    adjuvants = p["adjuvant_l"] * p["prix_adjuvant_l"]
    matieres = ciment + sable + gravier + eau + adjuvants

    energie = (p["kwh"] * p["prix_kwh"]) + (p["diesel_l"] * p["prix_diesel_l"])
    main_oeuvre = p["heures"] * p["taux_horaire"]
    fixes = p["maintenance"] + p["amortissement"] + p["frais_generaux"] + p["transport_interne"]

    return round(matieres + energie + main_oeuvre + fixes, 2)


if __name__ == "__main__":
    print("== Test: GET default-costs ==")
    status, data = http_json(f"{BASE_URL}/default-costs/")
    print("Status:", status)
    print("Response:", json.dumps(data, ensure_ascii=False, indent=2)[:1000])

    print("\n== Test: POST simulation ==")
    status, data = http_json(f"{BASE_URL}/simulation/", method="POST", data=payload)
    print("Status:", status)
    print("Response:", json.dumps(data, ensure_ascii=False, indent=2)[:1200])

    exp = expected_total(payload)
    got = None
    # Try to read a common field name used by the API for the total
    for key in ("total", "total_m3", "cout_total", "cout_de_revient", "cout_de_revient_m3"):
        if isinstance(data, dict) and key in data and isinstance(data[key], (int, float)):
            got = float(data[key])
            break
    print(f"\nExpected total (calc): {exp} €")
    if got is not None:
        print(f"API total: {got:.2f} €")
        diff = round(got - exp, 2)
        print(f"Diff: {diff} €")
        if abs(diff) <= 0.5:
            print("Result: OK (within tolerance)")
        else:
            print("Result: WARNING (outside tolerance)")
    else:
        print("API total not found in response. Keys:", list(data.keys()) if isinstance(data, dict) else type(data))