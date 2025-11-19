#!/usr/bin/env python3

"""
Script: generate-presigned-upload-url.py
Description: Génère une URL pré-signée AWS S3 pour permettre l'upload
             d'un fichier par un utilisateur non authentifié
Usage: ./generate-presigned-upload-url.py <bucket-name> [options]
"""

import argparse
import sys
from datetime import datetime
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


def generate_default_object_key() -> str:
    """
    Génère une clé d'objet par défaut avec timestamp.

    Returns:
        str: Clé d'objet avec format uploads/file-YYYYMMDD-HHMMSS
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"uploads/file-{timestamp}"


def generate_presigned_url(
    bucket_name: str,
    object_key: str,
    expiration: int = 3600,
    content_type: Optional[str] = None
) -> Optional[str]:
    """
    Génère une URL pré-signée pour uploader un objet vers S3.

    Args:
        bucket_name: Nom du bucket S3
        object_key: Clé/chemin de l'objet dans S3
        expiration: Durée de validité en secondes (défaut: 3600)
        content_type: Type MIME du fichier (optionnel)

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

        # Ajouter le Content-Type si spécifié
        if content_type:
            params['ContentType'] = content_type

        # Générer l'URL pré-signée pour PUT
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
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


def print_usage_examples(presigned_url: str, expiration: int) -> None:
    """
    Affiche des exemples d'utilisation de l'URL pré-signée.

    Args:
        presigned_url: L'URL pré-signée générée
        expiration: Durée de validité en secondes
    """
    print()
    print("━" * 70)
    print_success("URL PRÉ-SIGNÉE:")
    print(presigned_url)
    print("━" * 70)
    print()

    print_warning("Pour uploader un fichier avec cette URL, utilisez:")
    print()
    print("  Avec curl:")
    print(f'  curl -X PUT -T "chemin/vers/fichier" "{presigned_url}"')
    print()
    print("  Avec wget:")
    print(f'  wget --method=PUT --body-file="chemin/vers/fichier" "{presigned_url}"')
    print()
    print("  Avec Python requests:")
    print("  import requests")
    print("  with open('fichier', 'rb') as f:")
    print(f"      response = requests.put('{presigned_url[:50]}...', data=f)")
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
        description="Génère une URL pré-signée AWS S3 pour l'upload d'un fichier",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  %(prog)s my-bucket
  %(prog)s my-bucket --object-key uploads/document.pdf
  %(prog)s my-bucket --object-key uploads/document.pdf --expiration 7200
  %(prog)s my-bucket --object-key image.jpg --content-type image/jpeg

Prérequis:
  - Python 3 avec boto3 installé (pip3 install boto3)
  - Credentials AWS configurés (aws configure)
  - Permissions S3 pour générer des URLs pré-signées
        """
    )

    parser.add_argument(
        'bucket_name',
        help='Nom du bucket S3 (requis)'
    )

    parser.add_argument(
        '--object-key', '-k',
        help='Clé/nom de l\'objet dans S3 (défaut: uploads/file-YYYYMMDD-HHMMSS)',
        default=None
    )

    parser.add_argument(
        '--expiration', '-e',
        type=int,
        help='Durée de validité en secondes (défaut: 3600 = 1 heure)',
        default=3600
    )

    parser.add_argument(
        '--content-type', '-t',
        help='Type MIME du fichier (ex: image/jpeg, application/pdf)',
        default=None
    )

    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Mode silencieux - affiche uniquement l\'URL'
    )

    args = parser.parse_args()

    # Validation des arguments
    if args.expiration < 1:
        print_error("Erreur: L'expiration doit être au moins 1 seconde")
        sys.exit(1)

    if args.expiration > 604800:  # 7 jours
        print_warning("Avertissement: L'expiration maximale recommandée est de 7 jours (604800 secondes)")

    # Générer la clé d'objet si non fournie
    object_key = args.object_key if args.object_key else generate_default_object_key()

    if not args.quiet:
        print_warning("Vérification des prérequis...")
        print()

        # Vérifier les credentials AWS
        if not check_aws_credentials():
            sys.exit(1)

        print()
        print_warning("Génération de l'URL pré-signée...")
        print(f"Bucket: {args.bucket_name}")
        print(f"Object Key: {object_key}")
        print(f"Expiration: {args.expiration} secondes")
        if args.content_type:
            print(f"Content-Type: {args.content_type}")
        print()

    # Générer l'URL pré-signée
    presigned_url = generate_presigned_url(
        args.bucket_name,
        object_key,
        args.expiration,
        args.content_type
    )

    if not presigned_url:
        print_error("Échec de la génération de l'URL pré-signée")
        sys.exit(1)

    # Afficher les résultats
    if args.quiet:
        print(presigned_url)
    else:
        print_success("✓ URL pré-signée générée avec succès!")
        print_usage_examples(presigned_url, args.expiration)


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
