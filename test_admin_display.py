#!/usr/bin/env python
"""
Script pour tester l'affichage des statistiques sur l'interface d'administration
"""
import requests
from bs4 import BeautifulSoup

def test_admin_display():
    """Test de l'affichage des statistiques sur l'interface d'administration"""
    try:
        # Faire une requête à l'interface d'administration
        response = requests.get('http://localhost:8000/admin/', timeout=10)
        
        if response.status_code == 200:
            print("✅ Interface d'administration accessible")
            
            # Parser le HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Chercher les éléments avec la classe stat-value
            stat_values = soup.find_all(class_='stat-value')
            
            if stat_values:
                print(f"📊 Trouvé {len(stat_values)} statistiques:")
                for i, stat in enumerate(stat_values):
                    value = stat.get_text().strip()
                    print(f"   Statistique {i+1}: {value}")
            else:
                print("❌ Aucune statistique trouvée avec la classe 'stat-value'")
                
                # Chercher d'autres patterns
                print("\n🔍 Recherche d'autres patterns...")
                
                # Chercher les divs avec des classes contenant 'stat'
                stat_divs = soup.find_all('div', class_=lambda x: x and 'stat' in x)
                if stat_divs:
                    print(f"Trouvé {len(stat_divs)} divs avec 'stat' dans la classe:")
                    for div in stat_divs[:5]:
                        print(f"   - {div.get('class')}: {div.get_text().strip()[:50]}")
                
                # Chercher les h2
                h2_elements = soup.find_all('h2')
                if h2_elements:
                    print(f"Trouvé {len(h2_elements)} éléments h2:")
                    for h2 in h2_elements[:5]:
                        print(f"   - {h2.get('class')}: {h2.get_text().strip()}")
                
                # Chercher les mots-clés dans le contenu
                content = response.text
                keywords = ['Clients actifs', 'Commandes ce mois', 'Productions en cours', 'Livraisons prévues']
                for keyword in keywords:
                    if keyword in content:
                        print(f"✅ Trouvé '{keyword}' dans le contenu")
                    else:
                        print(f"❌ '{keyword}' non trouvé dans le contenu")
                        
            # Chercher les labels des statistiques
            stat_labels = soup.find_all(class_='stat-label')
            if stat_labels:
                print(f"\n🏷️ Labels trouvés:")
                for label in stat_labels:
                    text = label.get_text().strip()
                    print(f"   - {text}")
                    
        else:
            print(f"❌ Erreur d'accès: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_admin_display()