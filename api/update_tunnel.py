import requests
import time

# Fonction pour récupérer l'URL de ngrok via son API
def get_ngrok_url():
    url = "http://127.0.0.1:4040/api/tunnels"  # API de ngrok pour obtenir les tunnels actifs
    try:
        response = requests.get(url)
        response.raise_for_status()  # Vérifier si la requête a réussi

        # Analyser la réponse JSON pour obtenir l'URL
        tunnels = response.json()
        tunnel_url = tunnels["tunnels"][0]["public_url"]  # Récupérer l'URL du premier tunnel

        # Écrire l'URL dans un fichier
        with open("api/tunnel_url.txt", "w") as f:
            f.write(tunnel_url)
        print(f"URL de tunnel ngrok mise à jour : {tunnel_url}")
        return tunnel_url

    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la récupération de l'URL ngrok : {e}")
        return None

if __name__ == "__main__":
    get_ngrok_url()
