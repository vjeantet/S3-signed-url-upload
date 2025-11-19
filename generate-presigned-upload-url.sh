#!/bin/bash

################################################################################
# Script: generate-presigned-upload-url.sh
# Description: Génère une URL pré-signée AWS S3 pour permettre l'upload
#              d'un fichier par un utilisateur non authentifié
# Usage: ./generate-presigned-upload-url.sh <bucket-name> [object-key] [expiration]
################################################################################

set -e

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction d'aide
show_help() {
    cat << EOF
Usage: ${0##*/} <bucket-name> [object-key] [expiration]

Génère une URL pré-signée AWS S3 pour l'upload d'un fichier.

Arguments:
    bucket-name     Nom du bucket S3 (requis)
    object-key      Clé/nom de l'objet dans S3 (optionnel, défaut: fichier avec timestamp)
    expiration      Durée de validité en secondes (optionnel, défaut: 3600 = 1 heure)

Exemples:
    ${0##*/} my-bucket
    ${0##*/} my-bucket uploads/document.pdf
    ${0##*/} my-bucket uploads/document.pdf 7200

Prérequis:
    - AWS CLI configuré avec les credentials appropriés
    - Python 3 avec boto3 installé
    - Permissions S3 pour générer des URLs pré-signées

EOF
}

# Vérification des arguments
if [ $# -lt 1 ]; then
    echo -e "${RED}Erreur: Le nom du bucket est requis${NC}"
    show_help
    exit 1
fi

if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
    show_help
    exit 0
fi

# Paramètres
BUCKET_NAME="$1"
OBJECT_KEY="${2:-uploads/file-$(date +%Y%m%d-%H%M%S)}"
EXPIRATION="${3:-3600}"

# Vérification des prérequis
echo -e "${YELLOW}Vérification des prérequis...${NC}"

# Vérifier AWS CLI
if ! command -v aws &> /dev/null; then
    echo -e "${RED}Erreur: AWS CLI n'est pas installé${NC}"
    exit 1
fi

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Erreur: Python 3 n'est pas installé${NC}"
    exit 1
fi

# Vérifier boto3
if ! python3 -c "import boto3" 2>/dev/null; then
    echo -e "${RED}Erreur: boto3 n'est pas installé${NC}"
    echo -e "${YELLOW}Installez-le avec: pip3 install boto3${NC}"
    exit 1
fi

# Vérifier la configuration AWS
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}Erreur: AWS CLI n'est pas configuré correctement${NC}"
    echo -e "${YELLOW}Configurez-le avec: aws configure${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Tous les prérequis sont satisfaits${NC}"
echo ""

# Générer l'URL pré-signée
echo -e "${YELLOW}Génération de l'URL pré-signée...${NC}"
echo "Bucket: $BUCKET_NAME"
echo "Object Key: $OBJECT_KEY"
echo "Expiration: $EXPIRATION secondes"
echo ""

# Utiliser Python avec boto3 pour générer l'URL pré-signée
PRESIGNED_URL=$(python3 << EOF
import boto3
from botocore.exceptions import ClientError
import sys

try:
    s3_client = boto3.client('s3')

    # Générer l'URL pré-signée pour PUT
    presigned_url = s3_client.generate_presigned_url(
        'put_object',
        Params={
            'Bucket': '${BUCKET_NAME}',
            'Key': '${OBJECT_KEY}'
        },
        ExpiresIn=${EXPIRATION}
    )

    print(presigned_url)

except ClientError as e:
    print(f"Erreur AWS: {e}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"Erreur: {e}", file=sys.stderr)
    sys.exit(1)
EOF
)

# Vérifier si la génération a réussi
if [ $? -ne 0 ]; then
    echo -e "${RED}Erreur lors de la génération de l'URL pré-signée${NC}"
    exit 1
fi

# Afficher les résultats
echo -e "${GREEN}✓ URL pré-signée générée avec succès!${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}URL PRÉ-SIGNÉE:${NC}"
echo "$PRESIGNED_URL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${YELLOW}Pour uploader un fichier avec cette URL, utilisez:${NC}"
echo ""
echo "  curl -X PUT -T \"chemin/vers/fichier\" \"$PRESIGNED_URL\""
echo ""
echo -e "${YELLOW}Ou avec wget:${NC}"
echo ""
echo "  wget --method=PUT --body-file=\"chemin/vers/fichier\" \"$PRESIGNED_URL\""
echo ""
echo -e "${YELLOW}L'URL expire dans ${EXPIRATION} secondes${NC}"
echo ""
