#!/usr/bin/env python3

"""
Script: generate-presigned-download-url.py
Description: Génère une URL pré-signée AWS S3 pour permettre le téléchargement
             d'un fichier par un utilisateur non authentifié
Usage: ./generate-presigned-download-url.py <bucket-name> <object-key> [options]
"""

import argparse
import sys
from typing import Optional

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
except ImportError:
    print("Erreur: Le module boto3 n'est pas installé")
    print("Installez-le avec: pip3 install boto3")
    sys.exit(1)


# Codes couleur ANSI
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


def print_error(message: str) -> None:
    """Affiche un message d'erreur en rouge."""
    print(f"{Colors.RED}{message}{Colors.NC}", file=sys.stderr)


def print_success(message: str) -> None:
    """Affiche un message de succès en vert."""
    print(f"{Colors.GREEN}{message}{Colors.NC}")


def print_warning(message: str) -> None:
    """Affiche un message d'avertissement en jaune."""
    print(f"{Colors.YELLOW}{message}{Colors.NC}")


def print_info(message: str) -> None:
    """Affiche un message informatif en bleu."""
    print(f"{Colors.BLUE}{message}{Colors.NC}")


def check_aws_credentials() -> bool:
    """
    Vérifie que les credentials AWS sont configurés correctement.

    Returns:
        bool: True si les credentials sont valides, False sinon
    """
    try:
        sts_client = boto3.client('sts')
        identity = sts_client.get_caller_identity()
        print_success("✓ Credentials AWS valides")
        print(f"  Account: {identity['Account']}")
        print(f"  UserId: {identity['UserId']}")
        print(f"  ARN: {identity['Arn']}")
        return True
    except NoCredentialsError:
        print_error("Erreur: Credentials AWS non trouvés")
        print_warning("Configurez vos credentials avec: aws configure")
        return False
    except ClientError as e:
        print_error(f"Erreur lors de la vérification des credentials: {e}")
        return False
    except Exception as e:
        print_error(f"Erreur inattendue: {e}")
        return False


def check_object_exists(bucket_name: str, object_key: str) -> bool:
    """
    Vérifie si l'objet existe dans le bucket S3.

    Args:
        bucket_name: Nom du bucket S3
        object_key: Clé de l'objet dans S3

    Returns:
        bool: True si l'objet existe, False sinon
    """
    try:
        s3_client = boto3.client('s3')
        s3_client.head_object(Bucket=bucket_name, Key=object_key)
        return True
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        if error_code == '404':
            return False
        print_warning(f"Impossible de vérifier l'existence de l'objet: {e}")
        return True  # Continuer quand même
    except Exception:
        return True  # En cas d'erreur, continuer quand même


def get_object_info(bucket_name: str, object_key: str) -> Optional[dict]:
    """
    Récupère les informations sur l'objet S3.

    Args:
        bucket_name: Nom du bucket S3
        object_key: Clé de l'objet dans S3

    Returns:
        Optional[dict]: Informations sur l'objet ou None
    """
    try:
        s3_client = boto3.client('s3')
        response = s3_client.head_object(Bucket=bucket_name, Key=object_key)

        size_bytes = response.get('ContentLength', 0)

        # Convertir en format lisible
        if size_bytes < 1024:
            size_str = f"{size_bytes} B"
        elif size_bytes < 1048576:
            size_str = f"{size_bytes / 1024:.2f} KB"
        elif size_bytes < 1073741824:
            size_str = f"{size_bytes / 1048576:.2f} MB"
        else:
            size_str = f"{size_bytes / 1073741824:.2f} GB"

        return {
            'size': size_str,
            'content_type': response.get('ContentType', 'unknown'),
            'last_modified': response.get('LastModified', 'unknown')
        }
    except Exception:
        return None


def generate_presigned_download_url(
    bucket_name: str,
    object_key: str,
    expiration: int = 3600,
    filename: Optional[str] = None
) -> Optional[str]:
    """
    Génère une URL pré-signée pour télécharger un objet depuis S3.

    Args:
        bucket_name: Nom du bucket S3
        object_key: Clé/chemin de l'objet dans S3
        expiration: Durée de validité en secondes (défaut: 3600)
        filename: Nom de fichier suggéré pour le téléchargement (optionnel)

    Returns:
        Optional[str]: URL pré-signée ou None en cas d'erreur
    """
    try:
        s3_client = boto3.client('s3')

        # Préparer les paramètres
        params = {
            'Bucket': bucket_name,
            'Key': object_key
        }

        # Ajouter le nom de fichier suggéré si spécifié
        response_content_disposition = None
        if filename:
            response_content_disposition = f'attachment; filename="{filename}"'
            params['ResponseContentDisposition'] = response_content_disposition

        # Générer l'URL pré-signée pour GET
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params=params,
            ExpiresIn=expiration
        )

        return presigned_url

    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        error_message = e.response.get('Error', {}).get('Message', str(e))
        print_error(f"Erreur AWS ({error_code}): {error_message}")
        return None
    except Exception as e:
        print_error(f"Erreur lors de la génération de l'URL: {e}")
        return None


def print_usage_examples(presigned_url: str, expiration: int, object_key: str) -> None:
    """
    Affiche des exemples d'utilisation de l'URL pré-signée.

    Args:
        presigned_url: L'URL pré-signée générée
        expiration: Durée de validité en secondes
        object_key: Clé de l'objet
    """
    print()
    print("━" * 70)
    print_success("URL PRÉ-SIGNÉE DE TÉLÉCHARGEMENT:")
    print(presigned_url)
    print("━" * 70)
    print()

    print_warning("Pour télécharger le fichier avec cette URL:")
    print()
    print("  Avec le script fourni:")
    print(f'  ./download-from-presigned-url.sh "{presigned_url}"')
    print()
    print("  Avec curl:")
    print(f'  curl -o "fichier" "{presigned_url}"')
    print()
    print("  Avec wget:")
    print(f'  wget -O "fichier" "{presigned_url}"')
    print()
    print("  Dans un navigateur web:")
    print("  Collez simplement l'URL dans la barre d'adresse")
    print()
    print("  Avec Python requests:")
    print("  import requests")
    print(f"  response = requests.get('{presigned_url[:50]}...')")
    print("  with open('fichier', 'wb') as f:")
    print("      f.write(response.content)")
    print()

    # Convertir la durée en format lisible
    hours = expiration // 3600
    minutes = (expiration % 3600) // 60
    seconds = expiration % 60

    duration_parts = []
    if hours > 0:
        duration_parts.append(f"{hours} heure{'s' if hours > 1 else ''}")
    if minutes > 0:
        duration_parts.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
    if seconds > 0 or not duration_parts:
        duration_parts.append(f"{seconds} seconde{'s' if seconds > 1 else ''}")

    duration_str = " ".join(duration_parts)
    print_warning(f"L'URL expire dans {duration_str}")
    print()


def main():
    """Fonction principale du script."""
    parser = argparse.ArgumentParser(
        description="Génère une URL pré-signée AWS S3 pour le téléchargement d'un fichier",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  %(prog)s my-bucket uploads/document.pdf
  %(prog)s my-bucket uploads/document.pdf --expiration 7200
  %(prog)s my-bucket uploads/photo.jpg --filename "ma-photo.jpg"
  %(prog)s my-bucket data/rapport.xlsx --expiration 300 --filename "rapport-2025.xlsx"

Prérequis:
  - Python 3 avec boto3 installé (pip3 install boto3)
  - Credentials AWS configurés (aws configure)
  - Permissions S3 pour générer des URLs pré-signées (s3:GetObject)
  - Le fichier doit exister dans le bucket S3
        """
    )

    parser.add_argument(
        'bucket_name',
        help='Nom du bucket S3 (requis)'
    )

    parser.add_argument(
        'object_key',
        help='Clé/chemin de l\'objet dans S3 (requis)'
    )

    parser.add_argument(
        '--expiration', '-e',
        type=int,
        help='Durée de validité en secondes (défaut: 3600 = 1 heure)',
        default=3600
    )

    parser.add_argument(
        '--filename', '-f',
        help='Nom de fichier suggéré pour le téléchargement',
        default=None
    )

    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Mode silencieux - affiche uniquement l\'URL'
    )

    parser.add_argument(
        '--no-check',
        action='store_true',
        help='Ne pas vérifier si le fichier existe (plus rapide)'
    )

    args = parser.parse_args()

    # Validation des arguments
    if args.expiration < 1:
        print_error("Erreur: L'expiration doit être au moins 1 seconde")
        sys.exit(1)

    if args.expiration > 604800:  # 7 jours
        print_warning("Avertissement: L'expiration maximale recommandée est de 7 jours (604800 secondes)")

    if not args.quiet:
        print_warning("Vérification des prérequis...")
        print()

        # Vérifier les credentials AWS
        if not check_aws_credentials():
            sys.exit(1)

        print()
        print_warning("Génération de l'URL pré-signée de téléchargement...")
        print(f"Bucket: {args.bucket_name}")
        print(f"Object Key: {args.object_key}")
        print(f"Expiration: {args.expiration} secondes")
        if args.filename:
            print(f"Nom de fichier suggéré: {args.filename}")
        print()

        # Vérifier si l'objet existe (si non désactivé)
        if not args.no_check:
            print_info("Vérification de l'existence du fichier...")
            if not check_object_exists(args.bucket_name, args.object_key):
                print_error(f"Le fichier '{args.object_key}' n'existe pas dans le bucket '{args.bucket_name}'")
                print_warning("Utilisez --no-check pour ignorer cette vérification")
                sys.exit(1)

            # Afficher les informations sur le fichier
            info = get_object_info(args.bucket_name, args.object_key)
            if info:
                print_success("✓ Fichier trouvé")
                print(f"  Taille: {info['size']}")
                print(f"  Type: {info['content_type']}")
                print(f"  Dernière modification: {info['last_modified']}")
            print()

    # Générer l'URL pré-signée
    presigned_url = generate_presigned_download_url(
        args.bucket_name,
        args.object_key,
        args.expiration,
        args.filename
    )

    if not presigned_url:
        print_error("Échec de la génération de l'URL pré-signée")
        sys.exit(1)

    # Afficher les résultats
    if args.quiet:
        print(presigned_url)
    else:
        print_success("✓ URL pré-signée de téléchargement générée avec succès!")
        print_usage_examples(presigned_url, args.expiration, args.object_key)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()
        print_warning("Opération annulée par l'utilisateur")
        sys.exit(130)
    except Exception as e:
        print_error(f"Erreur fatale: {e}")
        sys.exit(1)
