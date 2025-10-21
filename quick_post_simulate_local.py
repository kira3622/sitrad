#!/usr/bin/env python
import os
import django
import requests
from decimal import Decimal

# Init Django for ORM access
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beton_project.settings')
django.setup()

from formulas.models import FormuleBeton

BASE_URL = "http://127.0.0.1:8000/cost-calculation/api/simulate/"


def main():
    # Try to fetch a known demo formula, else take the first
    formule = (FormuleBeton.objects.filter(nom="Béton C20/25 Économique").first()
               or FormuleBeton.objects.first())
    if not formule:
        print("Aucune formule disponible en base.")
        return

    payload = {
        'formule_id': str(formule.id),
        'quantite': '10',
        'unite_mesure': 'm3'
    }
    print(f"Post simulation pour formule {formule.nom} (id={formule.id})...")
    try:
        resp = requests.post(BASE_URL, data=payload, timeout=20)
        print("Status:", resp.status_code)
        print(resp.text[:800])
    except Exception as e:
        print("Erreur lors de l'appel:", e)

if __name__ == '__main__':
    main()