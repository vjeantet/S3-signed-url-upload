# S3 Presigned URL Upload & Download

Ce projet contient des scripts pour gérer l'upload et le téléchargement de fichiers vers/depuis AWS S3 via des URLs pré-signées :
- **Pour administrateurs** : Scripts Python pour générer des URLs pré-signées (upload et download)
- **Pour utilisateurs** : Scripts bash pour uploader/télécharger des fichiers sans authentification AWS

## Prérequis

### Pour administrateurs (génération d'URLs)

- **Python 3.6+**
- **boto3** : SDK AWS pour Python
- **Credentials AWS** configurés

### Pour utilisateurs finaux (upload et téléchargement de fichiers)

- **curl** : Outil de transfert de données (généralement pré-installé)
- **Aucune authentification AWS requise**

## Installation

### Pour administrateurs

```bash
# Installer boto3
pip3 install boto3

# Configurer les credentials AWS (si pas déjà fait)
aws configure
# OU définir les variables d'environnement:
# export AWS_ACCESS_KEY_ID=your_access_key
# export AWS_SECRET_ACCESS_KEY=your_secret_key
# export AWS_DEFAULT_REGION=us-east-1
```

### Pour utilisateurs finaux

```bash
# Vérifier que curl est installé
curl --version

# Si curl n'est pas installé:
# Ubuntu/Debian:
sudo apt-get install curl

# macOS (avec Homebrew):
brew install curl

# CentOS/RHEL:
sudo yum install curl
```

## Scripts disponibles

### 1. generate-presigned-upload-url.py (Pour administrateurs AWS)

Script Python pour générer une URL pré-signée permettant l'upload d'un fichier vers un bucket S3.

**Prérequis :** Credentials AWS valides

#### Usage

```bash
./generate-presigned-upload-url.py <bucket-name> [options]
```

#### Options

- **bucket_name** (positionnel, requis) : Nom du bucket S3 cible
- **--object-key, -k** : Chemin/nom du fichier dans S3 (défaut: `uploads/file-YYYYMMDD-HHMMSS`)
- **--expiration, -e** : Durée de validité en secondes (défaut: 3600 = 1 heure)
- **--content-type, -t** : Type MIME du fichier (ex: `image/jpeg`, `application/pdf`)
- **--quiet, -q** : Mode silencieux - affiche uniquement l'URL
- **--help, -h** : Affiche l'aide

#### Exemples

```bash
# Générer une URL avec paramètres par défaut
./generate-presigned-upload-url.py my-bucket

# Spécifier le chemin du fichier dans S3
./generate-presigned-upload-url.py my-bucket --object-key uploads/document.pdf

# Spécifier une expiration de 2 heures (7200 secondes)
./generate-presigned-upload-url.py my-bucket -k uploads/document.pdf -e 7200

# Avec un type MIME spécifique
./generate-presigned-upload-url.py my-bucket -k images/photo.jpg -t image/jpeg

# Mode silencieux (pour scripts)
./generate-presigned-upload-url.py my-bucket -q
```

#### Fonctionnalités

- ✅ Génération d'URL pré-signée pour l'opération PUT
- ✅ Support du Content-Type personnalisé
- ✅ Validation automatique des credentials AWS
- ✅ Affichage coloré et formaté des résultats
- ✅ Mode silencieux pour intégration dans des scripts
- ✅ Gestion d'erreurs complète avec messages explicites
- ✅ Exemples d'utilisation intégrés

---

### 2. upload-to-presigned-url.sh (Pour utilisateurs finaux)

Script bash permettant d'uploader un fichier vers S3 en utilisant une URL pré-signée.

**Prérequis :** Aucune authentification AWS requise, seulement `curl`

#### Usage

```bash
./upload-to-presigned-url.sh <fichier> <url-presignee> [options]
```

#### Options

- **fichier** (positionnel, requis) : Chemin vers le fichier à uploader
- **url-presignee** (positionnel, requis) : URL pré-signée fournie par l'administrateur
- **-v, --verbose** : Mode verbeux - affiche plus de détails
- **-h, --help** : Affiche l'aide

#### Exemples

```bash
# Upload basique
./upload-to-presigned-url.sh document.pdf "https://bucket.s3.amazonaws.com/..."

# Avec mode verbeux
./upload-to-presigned-url.sh photo.jpg "https://bucket.s3.amazonaws.com/..." --verbose

# L'URL doit être entre guillemets
./upload-to-presigned-url.sh rapport.xlsx "https://my-bucket.s3.us-east-1.amazonaws.com/..."
```

#### Fonctionnalités

- ✅ Upload simple sans credentials AWS
- ✅ Détection automatique du type MIME
- ✅ Affichage de la progression
- ✅ Gestion d'erreurs avec messages explicites
- ✅ Validation du fichier avant upload
- ✅ Support de tous les types de fichiers
- ✅ Messages d'erreur détaillés (URL expirée, accès refusé, etc.)

#### Codes de retour

- **0** : Upload réussi
- **1** : Erreur (fichier inexistant, URL expirée, accès refusé, etc.)

---

### 3. generate-presigned-download-url.py (Pour administrateurs AWS)

Script Python pour générer une URL pré-signée permettant le téléchargement d'un fichier depuis un bucket S3.

**Prérequis :** Credentials AWS valides

#### Usage

```bash
./generate-presigned-download-url.py <bucket-name> <object-key> [options]
```

#### Options

- **bucket_name** (positionnel, requis) : Nom du bucket S3 cible
- **object_key** (positionnel, requis) : Chemin/nom du fichier dans S3
- **--expiration, -e** : Durée de validité en secondes (défaut: 3600 = 1 heure)
- **--filename, -f** : Nom de fichier suggéré pour le téléchargement
- **--quiet, -q** : Mode silencieux - affiche uniquement l'URL
- **--no-check** : Ne pas vérifier si le fichier existe (plus rapide)
- **--help, -h** : Affiche l'aide

#### Exemples

```bash
# Générer une URL pour télécharger un fichier existant
./generate-presigned-download-url.py my-bucket uploads/document.pdf

# Spécifier une expiration de 2 heures (7200 secondes)
./generate-presigned-download-url.py my-bucket uploads/document.pdf -e 7200

# Suggérer un nom de fichier pour le téléchargement
./generate-presigned-download-url.py my-bucket data/rapport.xlsx --filename "rapport-2025.xlsx"

# Mode silencieux (pour scripts)
./generate-presigned-download-url.py my-bucket uploads/photo.jpg -q
```

#### Fonctionnalités

- ✅ Génération d'URL pré-signée pour l'opération GET
- ✅ Vérification automatique de l'existence du fichier
- ✅ Affichage des informations du fichier (taille, type, date)
- ✅ Support du nom de fichier suggéré pour le téléchargement
- ✅ Validation automatique des credentials AWS
- ✅ Affichage coloré et formaté des résultats
- ✅ Mode silencieux pour intégration dans des scripts
- ✅ Gestion d'erreurs complète avec messages explicites

---

### 4. download-from-presigned-url.sh (Pour utilisateurs finaux)

Script bash permettant de télécharger un fichier depuis S3 en utilisant une URL pré-signée.

**Prérequis :** Aucune authentification AWS requise, seulement `curl`

#### Usage

```bash
./download-from-presigned-url.sh <url-presignee> [fichier-destination] [options]
```

#### Options

- **url-presignee** (positionnel, requis) : URL pré-signée fournie par l'administrateur
- **fichier-destination** (positionnel, optionnel) : Chemin où enregistrer le fichier
- **-v, --verbose** : Mode verbeux - affiche plus de détails
- **-h, --help** : Affiche l'aide

#### Exemples

```bash
# Téléchargement basique (nom de fichier auto-détecté)
./download-from-presigned-url.sh "https://bucket.s3.amazonaws.com/..."

# Spécifier le nom du fichier de destination
./download-from-presigned-url.sh "https://bucket.s3.amazonaws.com/..." document.pdf

# Avec chemin complet et mode verbeux
./download-from-presigned-url.sh "https://bucket.s3.amazonaws.com/..." ./downloads/rapport.pdf --verbose
```

#### Fonctionnalités

- ✅ Téléchargement simple sans credentials AWS
- ✅ Détection automatique du nom de fichier depuis l'URL
- ✅ Affichage des informations du fichier (taille, type)
- ✅ Affichage de la progression
- ✅ Gestion d'erreurs avec messages explicites
- ✅ Vérification de l'écrasement de fichier existant
- ✅ Nettoyage automatique en cas d'erreur
- ✅ Messages d'erreur détaillés (URL expirée, fichier non trouvé, etc.)

#### Codes de retour

- **0** : Téléchargement réussi
- **1** : Erreur (URL expirée, fichier non trouvé, accès refusé, etc.)

---

### Workflows complets

#### Workflow Upload

#### Étape 1 : Administrateur génère l'URL

```bash
# L'admin génère une URL pré-signée
./generate-presigned-upload-url.py my-bucket -k uploads/rapport.pdf -e 3600

# Sortie : https://my-bucket.s3.amazonaws.com/uploads/rapport.pdf?X-Amz-Algorithm=...
```

#### Étape 2 : Administrateur partage l'URL

L'administrateur envoie l'URL pré-signée à l'utilisateur (email, chat, etc.)

#### Étape 3 : Utilisateur upload le fichier

```bash
# L'utilisateur upload son fichier (sans credentials AWS)
./upload-to-presigned-url.sh rapport.pdf "https://my-bucket.s3.amazonaws.com/..."

# ✓ Upload réussi!
```

#### Workflow Download

#### Étape 1 : Administrateur génère l'URL de téléchargement

```bash
# L'admin génère une URL pré-signée pour télécharger un fichier existant
./generate-presigned-download-url.py my-bucket uploads/rapport.pdf -e 3600

# Sortie : https://my-bucket.s3.amazonaws.com/uploads/rapport.pdf?X-Amz-Algorithm=...
```

#### Étape 2 : Administrateur partage l'URL

L'administrateur envoie l'URL pré-signée à l'utilisateur (email, chat, etc.)

#### Étape 3 : Utilisateur télécharge le fichier

```bash
# L'utilisateur télécharge le fichier (sans credentials AWS)
./download-from-presigned-url.sh "https://my-bucket.s3.amazonaws.com/..." rapport.pdf

# ✓ Téléchargement réussi!
```

---

### Utilisation de l'URL générée (méthodes alternatives)

#### Pour l'upload

Une fois l'URL pré-signée d'upload générée, un utilisateur peut uploader un fichier sans credentials AWS :

**Avec curl:**
```bash
curl -X PUT -T "chemin/vers/fichier.pdf" "URL_PRESIGNEE_UPLOAD"
```

**Avec wget:**
```bash
wget --method=PUT --body-file="chemin/vers/fichier.pdf" "URL_PRESIGNEE_UPLOAD"
```

**Avec Python requests:**
```python
import requests

with open('fichier.pdf', 'rb') as f:
    response = requests.put('URL_PRESIGNEE_UPLOAD', data=f)
    print(f"Status: {response.status_code}")
```

**Avec JavaScript (fetch):**
```javascript
const file = document.getElementById('fileInput').files[0];
fetch('URL_PRESIGNEE_UPLOAD', {
    method: 'PUT',
    body: file
})
.then(response => console.log('Upload réussi:', response.status))
.catch(error => console.error('Erreur:', error));
```

#### Pour le téléchargement

Une fois l'URL pré-signée de téléchargement générée, un utilisateur peut télécharger le fichier sans credentials AWS :

**Avec curl:**
```bash
curl -o "fichier.pdf" "URL_PRESIGNEE_DOWNLOAD"
```

**Avec wget:**
```bash
wget -O "fichier.pdf" "URL_PRESIGNEE_DOWNLOAD"
```

**Avec Python requests:**
```python
import requests

response = requests.get('URL_PRESIGNEE_DOWNLOAD')
with open('fichier.pdf', 'wb') as f:
    f.write(response.content)
print(f"Status: {response.status_code}")
```

**Avec JavaScript (fetch):**
```javascript
fetch('URL_PRESIGNEE_DOWNLOAD')
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'fichier.pdf';
        a.click();
    })
    .catch(error => console.error('Erreur:', error));
```

**Dans un navigateur web:**
```
Il suffit de coller l'URL dans la barre d'adresse pour télécharger le fichier
```

### Utilisation comme module Python

Vous pouvez également importer les scripts dans vos propres applications Python :

#### Pour l'upload

```python
from generate_presigned_upload_url import generate_presigned_url

# Générer une URL pré-signée pour upload
url = generate_presigned_url(
    bucket_name='my-bucket',
    object_key='uploads/file.pdf',
    expiration=3600,
    content_type='application/pdf'
)

if url:
    print(f"URL d'upload générée: {url}")
```

#### Pour le téléchargement

```python
from generate_presigned_download_url import generate_presigned_download_url

# Générer une URL pré-signée pour téléchargement
url = generate_presigned_download_url(
    bucket_name='my-bucket',
    object_key='uploads/file.pdf',
    expiration=3600,
    filename='mon-fichier.pdf'
)

if url:
    print(f"URL de téléchargement générée: {url}")
```

## Permissions AWS requises

Le compte AWS utilisé pour générer les URLs pré-signées doit avoir les permissions suivantes :

### Pour upload et téléchargement

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject"
            ],
            "Resource": "arn:aws:s3:::BUCKET_NAME/*"
        }
    ]
}
```

### Configuration minimale IAM

Pour un utilisateur dédié à la génération d'URLs pré-signées (upload et téléchargement) :

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowPresignedUploadURLs",
            "Effect": "Allow",
            "Action": [
                "s3:PutObject"
            ],
            "Resource": [
                "arn:aws:s3:::my-bucket/uploads/*"
            ]
        },
        {
            "Sid": "AllowPresignedDownloadURLs",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject"
            ],
            "Resource": [
                "arn:aws:s3:::my-bucket/*"
            ]
        }
    ]
}
```

### Permissions séparées (recommandé)

Si vous souhaitez séparer les responsabilités :

**Utilisateur Upload uniquement:**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": ["s3:PutObject"],
            "Resource": "arn:aws:s3:::my-bucket/uploads/*"
        }
    ]
}
```

**Utilisateur Download uniquement:**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": ["s3:GetObject"],
            "Resource": "arn:aws:s3:::my-bucket/*"
        }
    ]
}
```

## Sécurité

### Bonnes pratiques

- ✅ Les URLs pré-signées expirent après la durée spécifiée
- ✅ Utilisez des durées d'expiration courtes (< 1 heure) pour les données sensibles
- ✅ Ne partagez les URLs qu'avec des utilisateurs de confiance
- ✅ Restreignez les permissions IAM au minimum nécessaire
- ✅ Utilisez des préfixes de clés (ex: `uploads/`) pour isoler les uploads
- ✅ Configurez des politiques de bucket pour limiter les types de fichiers
- ⚠️ Les fichiers uploadés héritent des permissions par défaut du bucket
- ⚠️ Considérez l'activation du chiffrement côté serveur (SSE)

### Limitations de sécurité

- Les URLs pré-signées ne peuvent pas restreindre la taille du fichier
- Le Content-Type peut être contourné par l'utilisateur
- Envisagez une validation côté serveur après l'upload

## Dépannage

### Erreur: "Le module boto3 n'est pas installé"
```bash
pip3 install boto3
```

### Erreur: "Credentials AWS non trouvés"
```bash
# Option 1: Configurer AWS CLI
aws configure

# Option 2: Variables d'environnement
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

### Erreur: "Access Denied"

Vérifiez que :
1. Vos credentials AWS sont valides
2. L'utilisateur IAM a les permissions `s3:PutObject` sur le bucket
3. Le nom du bucket est correct
4. La région AWS est correcte

### Le script ne trouve pas Python

```bash
# Vérifier la version de Python
python3 --version

# Si nécessaire, modifier le shebang du script
# De: #!/usr/bin/env python3
# À: #!/usr/bin/python3
```

## Cas d'usage

### Intégration dans une application web

```python
from flask import Flask, jsonify
from generate_presigned_upload_url import generate_presigned_url

app = Flask(__name__)

@app.route('/api/upload-url/<filename>')
def get_upload_url(filename):
    url = generate_presigned_url(
        bucket_name='my-bucket',
        object_key=f'uploads/{filename}',
        expiration=300  # 5 minutes
    )
    return jsonify({'upload_url': url})
```

### Script automatisé

```bash
#!/bin/bash
# Générer une URL et l'envoyer par email

URL=$(./generate-presigned-upload-url.py my-bucket -q)
echo "Voici votre lien d'upload: $URL" | mail -s "Lien d'upload" user@example.com
```

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou soumettre une pull request.

## Licence

MIT
