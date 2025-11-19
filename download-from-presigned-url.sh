#!/bin/bash

################################################################################
# Script: download-from-presigned-url.sh
# Description: Télécharge un fichier depuis AWS S3 en utilisant une URL pré-signée
#              Ne nécessite AUCUNE authentification AWS
# Usage: ./download-from-presigned-url.sh <url-presignee> [fichier-destination]
################################################################################

set -e

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction d'aide
show_help() {
    cat << EOF
Usage: ${0##*/} <url-presignee> [fichier-destination] [options]

Télécharge un fichier depuis AWS S3 en utilisant une URL pré-signée.
Aucune authentification AWS n'est requise.

Arguments:
    url-presignee       URL pré-signée S3 générée par l'administrateur (requis)
    fichier-destination Chemin où enregistrer le fichier (optionnel, défaut: nom du fichier extrait de l'URL)

Options:
    -v, --verbose       Mode verbeux - affiche plus de détails
    -h, --help          Affiche cette aide

Exemples:
    ${0##*/} "https://bucket.s3.amazonaws.com/..."
    ${0##*/} "https://bucket.s3.amazonaws.com/..." document.pdf
    ${0##*/} "https://bucket.s3.amazonaws.com/..." ./downloads/rapport.pdf --verbose

Notes:
    - L'URL pré-signée doit être valide (non expirée)
    - Utilisez des guillemets autour de l'URL pour éviter les problèmes
    - Le fichier sera téléchargé dans le répertoire courant si aucun chemin n'est spécifié

EOF
}

# Fonction pour afficher les erreurs
print_error() {
    echo -e "${RED}❌ $1${NC}" >&2
}

# Fonction pour afficher les succès
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Fonction pour afficher les avertissements
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Fonction pour afficher les infos
print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Fonction pour extraire le nom de fichier de l'URL
extract_filename_from_url() {
    local url="$1"

    # Extraire la partie path de l'URL (avant les paramètres de requête)
    local path="${url%%\?*}"

    # Extraire le nom de fichier
    local filename=$(basename "$path")

    # Si le nom de fichier est vide ou trop court, utiliser un défaut
    if [ -z "$filename" ] || [ "${#filename}" -lt 3 ]; then
        filename="downloaded-file-$(date +%Y%m%d-%H%M%S)"
    fi

    echo "$filename"
}

# Fonction pour formater la taille en format lisible
format_size() {
    local bytes=$1

    if [ "$bytes" -lt 1024 ]; then
        echo "${bytes} B"
    elif [ "$bytes" -lt 1048576 ]; then
        echo "$(( bytes / 1024 )) KB"
    elif [ "$bytes" -lt 1073741824 ]; then
        echo "$(( bytes / 1048576 )) MB"
    else
        echo "$(( bytes / 1073741824 )) GB"
    fi
}

# Variables
VERBOSE=false
PRESIGNED_URL=""
OUTPUT_FILE=""

# Parser les arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -*)
            print_error "Option inconnue: $1"
            show_help
            exit 1
            ;;
        *)
            if [ -z "$PRESIGNED_URL" ]; then
                PRESIGNED_URL="$1"
            elif [ -z "$OUTPUT_FILE" ]; then
                OUTPUT_FILE="$1"
            else
                print_error "Trop d'arguments"
                show_help
                exit 1
            fi
            shift
            ;;
    esac
done

# Vérification des arguments requis
if [ -z "$PRESIGNED_URL" ]; then
    print_error "L'argument url-presignee est requis"
    echo ""
    show_help
    exit 1
fi

# Vérifier que curl est installé
if ! command -v curl &> /dev/null; then
    print_error "curl n'est pas installé"
    echo ""
    echo "Installez curl avec:"
    echo "  - Ubuntu/Debian: sudo apt-get install curl"
    echo "  - macOS: brew install curl"
    echo "  - CentOS/RHEL: sudo yum install curl"
    exit 1
fi

# Déterminer le nom du fichier de destination
if [ -z "$OUTPUT_FILE" ]; then
    OUTPUT_FILE=$(extract_filename_from_url "$PRESIGNED_URL")
    print_info "Nom de fichier détecté: $OUTPUT_FILE"
fi

# Vérifier si le fichier existe déjà
if [ -f "$OUTPUT_FILE" ]; then
    print_warning "Le fichier '$OUTPUT_FILE' existe déjà"
    read -p "Voulez-vous le remplacer? (o/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[OoYy]$ ]]; then
        print_info "Téléchargement annulé"
        exit 0
    fi
fi

# Vérifier que le répertoire de destination est accessible en écriture
OUTPUT_DIR=$(dirname "$OUTPUT_FILE")
if [ ! -d "$OUTPUT_DIR" ]; then
    print_error "Le répertoire '$OUTPUT_DIR' n'existe pas"
    exit 1
fi

if [ ! -w "$OUTPUT_DIR" ]; then
    print_error "Le répertoire '$OUTPUT_DIR' n'est pas accessible en écriture"
    exit 1
fi

# Afficher les informations
echo ""
print_info "═══════════════════════════════════════════════════════════"
print_info "Téléchargement depuis S3 (via URL pré-signée)"
print_info "═══════════════════════════════════════════════════════════"
echo ""

if [ "$VERBOSE" = true ]; then
    echo "URL            : ${PRESIGNED_URL:0:80}..."
    echo "Destination    : $OUTPUT_FILE"
    echo ""
fi

print_info "Récupération des informations du fichier..."
echo ""

# Obtenir les informations du fichier (Content-Length, Content-Type)
HEADER_INFO=$(curl -s -I "$PRESIGNED_URL" 2>&1)

if [ $? -ne 0 ]; then
    print_error "Impossible de se connecter au serveur"
    echo ""
    echo "Causes possibles:"
    echo "  • Pas de connexion internet"
    echo "  • L'URL est incorrecte"
    echo "  • Problème réseau"
    exit 1
fi

# Extraire la taille du fichier
CONTENT_LENGTH=$(echo "$HEADER_INFO" | grep -i "content-length:" | tail -1 | awk '{print $2}' | tr -d '\r')
CONTENT_TYPE=$(echo "$HEADER_INFO" | grep -i "content-type:" | tail -1 | cut -d' ' -f2- | tr -d '\r')

if [ -n "$CONTENT_LENGTH" ] && [ "$CONTENT_LENGTH" -gt 0 ]; then
    FILE_SIZE=$(format_size "$CONTENT_LENGTH")
    echo "Taille     : $FILE_SIZE"
fi

if [ -n "$CONTENT_TYPE" ]; then
    echo "Type       : $CONTENT_TYPE"
fi

echo "Destination: $OUTPUT_FILE"
echo ""

print_info "Début du téléchargement..."
echo ""

# Préparer les options curl
CURL_OPTS=(
    --location
    --output "$OUTPUT_FILE"
    --progress-bar
    -w "\n%{http_code}"
)

if [ "$VERBOSE" = true ]; then
    CURL_OPTS+=(--verbose)
else
    CURL_OPTS+=(--silent)
fi

# Effectuer le téléchargement et capturer le code HTTP
HTTP_CODE=$(curl "${CURL_OPTS[@]}" "$PRESIGNED_URL" 2>&1 | tee /dev/stderr | tail -n1)

# Vérifier le résultat
echo ""
echo ""

case $HTTP_CODE in
    200)
        print_success "Téléchargement réussi! (HTTP $HTTP_CODE)"
        echo ""

        # Afficher la taille du fichier téléchargé
        if [ -f "$OUTPUT_FILE" ]; then
            DOWNLOADED_SIZE=$(stat -f%z "$OUTPUT_FILE" 2>/dev/null || stat -c%s "$OUTPUT_FILE" 2>/dev/null)
            if [ -n "$DOWNLOADED_SIZE" ]; then
                DOWNLOADED_SIZE_FORMATTED=$(format_size "$DOWNLOADED_SIZE")
                print_info "Le fichier a été enregistré dans: $OUTPUT_FILE"
                print_info "Taille: $DOWNLOADED_SIZE_FORMATTED"
            fi
        fi
        exit 0
        ;;
    403)
        # Supprimer le fichier partiellement téléchargé
        [ -f "$OUTPUT_FILE" ] && rm -f "$OUTPUT_FILE"

        print_error "Accès refusé (HTTP $HTTP_CODE)"
        echo ""
        echo "Causes possibles:"
        echo "  • L'URL pré-signée a expiré"
        echo "  • L'URL pré-signée est invalide"
        echo "  • Les permissions S3 sont incorrectes"
        echo ""
        echo "Solution: Demandez une nouvelle URL pré-signée à l'administrateur"
        exit 1
        ;;
    404)
        # Supprimer le fichier partiellement téléchargé
        [ -f "$OUTPUT_FILE" ] && rm -f "$OUTPUT_FILE"

        print_error "Fichier non trouvé (HTTP $HTTP_CODE)"
        echo ""
        echo "Le fichier n'existe pas ou a été supprimé du bucket S3"
        exit 1
        ;;
    400)
        # Supprimer le fichier partiellement téléchargé
        [ -f "$OUTPUT_FILE" ] && rm -f "$OUTPUT_FILE"

        print_error "Requête invalide (HTTP $HTTP_CODE)"
        echo ""
        echo "L'URL pré-signée est mal formée"
        exit 1
        ;;
    000)
        # Supprimer le fichier partiellement téléchargé
        [ -f "$OUTPUT_FILE" ] && rm -f "$OUTPUT_FILE"

        print_error "Impossible de se connecter au serveur"
        echo ""
        echo "Causes possibles:"
        echo "  • Pas de connexion internet"
        echo "  • L'URL est incorrecte"
        echo "  • Problème réseau"
        exit 1
        ;;
    *)
        # Supprimer le fichier partiellement téléchargé
        [ -f "$OUTPUT_FILE" ] && rm -f "$OUTPUT_FILE"

        print_error "Téléchargement échoué (HTTP $HTTP_CODE)"
        echo ""
        echo "Une erreur inattendue s'est produite"
        echo "Code HTTP: $HTTP_CODE"
        exit 1
        ;;
esac
