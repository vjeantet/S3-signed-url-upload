#!/bin/bash

################################################################################
# Script: upload-to-presigned-url.sh
# Description: Upload un fichier vers AWS S3 en utilisant une URL pré-signée
#              Ne nécessite AUCUNE authentification AWS
# Usage: ./upload-to-presigned-url.sh <fichier> <url-presignee>
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
Usage: ${0##*/} <fichier> <url-presignee> [options]

Upload un fichier vers AWS S3 en utilisant une URL pré-signée.
Aucune authentification AWS n'est requise.

Arguments:
    fichier         Chemin vers le fichier à uploader (requis)
    url-presignee   URL pré-signée S3 générée par l'administrateur (requis)

Options:
    -v, --verbose   Mode verbeux - affiche plus de détails
    -h, --help      Affiche cette aide

Exemples:
    ${0##*/} document.pdf "https://bucket.s3.amazonaws.com/..."
    ${0##*/} photo.jpg "https://bucket.s3.amazonaws.com/..." --verbose

Notes:
    - L'URL pré-signée doit être valide (non expirée)
    - Le fichier sera uploadé tel quel
    - Utilisez des guillemets autour de l'URL pour éviter les problèmes

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

# Fonction pour obtenir la taille du fichier en format lisible
get_file_size() {
    local file="$1"
    local size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)

    if [ $? -ne 0 ]; then
        echo "inconnu"
        return
    fi

    if [ "$size" -lt 1024 ]; then
        echo "${size} B"
    elif [ "$size" -lt 1048576 ]; then
        echo "$(( size / 1024 )) KB"
    elif [ "$size" -lt 1073741824 ]; then
        echo "$(( size / 1048576 )) MB"
    else
        echo "$(( size / 1073741824 )) GB"
    fi
}

# Fonction pour détecter le type MIME
detect_mime_type() {
    local file="$1"

    # Essayer avec 'file' command
    if command -v file &> /dev/null; then
        file -b --mime-type "$file" 2>/dev/null
    else
        # Fallback basé sur l'extension
        case "${file##*.}" in
            jpg|jpeg) echo "image/jpeg" ;;
            png) echo "image/png" ;;
            gif) echo "image/gif" ;;
            pdf) echo "application/pdf" ;;
            txt) echo "text/plain" ;;
            json) echo "application/json" ;;
            xml) echo "application/xml" ;;
            zip) echo "application/zip" ;;
            *) echo "application/octet-stream" ;;
        esac
    fi
}

# Variables
VERBOSE=false
FILE_PATH=""
PRESIGNED_URL=""

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
            if [ -z "$FILE_PATH" ]; then
                FILE_PATH="$1"
            elif [ -z "$PRESIGNED_URL" ]; then
                PRESIGNED_URL="$1"
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
if [ -z "$FILE_PATH" ] || [ -z "$PRESIGNED_URL" ]; then
    print_error "Les arguments fichier et url-presignee sont requis"
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

# Vérifier que le fichier existe
if [ ! -f "$FILE_PATH" ]; then
    print_error "Le fichier '$FILE_PATH' n'existe pas"
    exit 1
fi

# Vérifier que le fichier est lisible
if [ ! -r "$FILE_PATH" ]; then
    print_error "Le fichier '$FILE_PATH' n'est pas lisible"
    exit 1
fi

# Obtenir les informations du fichier
FILE_SIZE=$(get_file_size "$FILE_PATH")
FILE_MIME=$(detect_mime_type "$FILE_PATH")
FILE_NAME=$(basename "$FILE_PATH")

# Afficher les informations
echo ""
print_info "═══════════════════════════════════════════════════════════"
print_info "Upload de fichier vers S3 (via URL pré-signée)"
print_info "═══════════════════════════════════════════════════════════"
echo ""
echo "Fichier    : $FILE_NAME"
echo "Taille     : $FILE_SIZE"
echo "Type MIME  : $FILE_MIME"
echo ""

if [ "$VERBOSE" = true ]; then
    echo "Chemin complet : $FILE_PATH"
    echo "URL            : ${PRESIGNED_URL:0:80}..."
    echo ""
fi

print_info "Début de l'upload..."
echo ""

# Préparer les options curl
CURL_OPTS=(
    -X PUT
    -T "$FILE_PATH"
    -H "Content-Type: $FILE_MIME"
    --progress-bar
    -w "\n%{http_code}"
    -o /dev/null
)

if [ "$VERBOSE" = true ]; then
    CURL_OPTS+=(--verbose)
else
    CURL_OPTS+=(--silent)
fi

# Effectuer l'upload et capturer le code HTTP
HTTP_CODE=$(curl "${CURL_OPTS[@]}" "$PRESIGNED_URL" 2>&1 | tee /dev/stderr | tail -n1)

# Vérifier le résultat
echo ""
echo ""

case $HTTP_CODE in
    200)
        print_success "Upload réussi! (HTTP $HTTP_CODE)"
        echo ""
        print_info "Le fichier '$FILE_NAME' a été uploadé avec succès sur S3"
        exit 0
        ;;
    403)
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
    400)
        print_error "Requête invalide (HTTP $HTTP_CODE)"
        echo ""
        echo "Causes possibles:"
        echo "  • L'URL pré-signée est mal formée"
        echo "  • Le Content-Type ne correspond pas à ce qui était attendu"
        echo ""
        exit 1
        ;;
    404)
        print_error "Bucket non trouvé (HTTP $HTTP_CODE)"
        echo ""
        echo "L'URL pré-signée pointe vers un bucket qui n'existe pas"
        exit 1
        ;;
    000)
        print_error "Impossible de se connecter au serveur"
        echo ""
        echo "Causes possibles:"
        echo "  • Pas de connexion internet"
        echo "  • L'URL est incorrecte"
        echo "  • Problème réseau"
        exit 1
        ;;
    *)
        print_error "Upload échoué (HTTP $HTTP_CODE)"
        echo ""
        echo "Une erreur inattendue s'est produite"
        echo "Code HTTP: $HTTP_CODE"
        exit 1
        ;;
esac
