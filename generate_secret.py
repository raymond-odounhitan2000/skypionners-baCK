#!/usr/bin/env python3
"""
Script utilitaire pour générer une SECRET_KEY sécurisée pour votre application FastAPI.
Utilisation: python generate_secret.py
"""

import secrets
import sys
import os


def generate_secret_key(length: int = 32) -> str:
    """
    Génère une clé secrète cryptographiquement sécurisée.

    Args:
        length: Longueur de la clé en caractères (32 = 256 bits)

    Returns:
        Clé secrète URL-safe
    """
    return secrets.token_urlsafe(length)


def generate_multiple_keys(count: int = 3) -> list:
    """
    Génère plusieurs clés pour choisir.

    Args:
        count: Nombre de clés à générer

    Returns:
        Liste de clés secrètes
    """
    return [generate_secret_key() for _ in range(count)]


def save_to_env_file(key: str, env_file: str = '.env') -> bool:
    """
    Sauvegarde la clé dans le fichier .env

    Args:
        key: Clé à sauvegarder
        env_file: Chemin du fichier .env

    Returns:
        True si succès, False sinon
    """
    try:
        # Vérifier si le fichier .env existe
        if os.path.exists(env_file):
            # Lire le contenu existant
            with open(env_file, 'r') as f:
                lines = f.readlines()

            # Chercher et remplacer la ligne SECRET_KEY
            secret_key_found = False
            for i, line in enumerate(lines):
                if line.startswith('SECRET_KEY='):
                    lines[i] = f'SECRET_KEY={key}\n'
                    secret_key_found = True
                    break

            # Si SECRET_KEY n'existe pas, l'ajouter
            if not secret_key_found:
                lines.append(f'SECRET_KEY={key}\n')

            # Écrire le fichier
            with open(env_file, 'w') as f:
                f.writelines(lines)
        else:
            # Créer un nouveau fichier .env
            with open(env_file, 'w') as f:
                f.write(f'SECRET_KEY={key}\n')

        print(f"✅ SECRET_KEY sauvegardée dans {env_file}")
        return True

    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde: {e}")
        return False


def main():
    """Fonction principale"""
    print("🔐 Générateur de SECRET_KEY pour FastAPI")
    print("=" * 50)

    # Générer plusieurs options
    keys = generate_multiple_keys(3)

    print("Voici 3 clés sécurisées générées :\n")

    for i, key in enumerate(keys, 1):
        print(f"Option {i}: {key}")

    print(f"\n📏 Longueur: {len(keys[0])} caractères (= 256 bits)")
    print("🔒 Sécurité: Cryptographiquement sécurisée avec secrets.token_urlsafe()")

    # Demander à l'utilisateur de choisir
    while True:
        try:
            choice = input("\nChoisissez une option (1-3) ou 'q' pour quitter: ").strip()

            if choice.lower() == 'q':
                print("👋 Au revoir!")
                return

            choice_num = int(choice)
            if 1 <= choice_num <= 3:
                selected_key = keys[choice_num - 1]
                break
            else:
                print("❌ Veuillez choisir 1, 2, 3 ou 'q'")
        except ValueError:
            print("❌ Entrée invalide. Utilisez 1, 2, 3 ou 'q'")

    # Sauvegarder dans .env
    print(f"\n🔄 Sauvegarde de: {selected_key[:20]}...")
    if save_to_env_file(selected_key):
        print("✅ Clé sauvegardée avec succès!")
        print("\n🚀 Votre SECRET_KEY est maintenant configurée dans .env")
        print("💡 Redémarrez votre serveur FastAPI pour appliquer les changements")
    else:
        print("❌ Échec de la sauvegarde. Vous pouvez copier la clé manuellement:")
        print(f"SECRET_KEY={selected_key}")


if __name__ == "__main__":
    main()
