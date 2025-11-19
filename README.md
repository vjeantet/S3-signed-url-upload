# S3 Presigned URL Upload

Ce projet contient un script Python pour générer des URLs pré-signées AWS S3 permettant à des utilisateurs non authentifiés d'uploader des fichiers.

## Prérequis

- **Python 3.6+**
- **boto3** : SDK AWS pour Python
- **Credentials AWS** configurés

### Installation

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

## Script principal

### generate-presigned-upload-url.py

Script Python pour générer une URL pré-signée permettant l'upload d'un fichier vers un bucket S3.

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

### Utilisation de l'URL générée

Une fois l'URL pré-signée générée, un utilisateur peut uploader un fichier sans credentials AWS :

**Avec curl:**
```bash
curl -X PUT -T "chemin/vers/fichier.pdf" "URL_PRESIGNEE"
```

**Avec wget:**
```bash
wget --method=PUT --body-file="chemin/vers/fichier.pdf" "URL_PRESIGNEE"
```

**Avec Python requests:**
```python
import requests

with open('fichier.pdf', 'rb') as f:
    response = requests.put('URL_PRESIGNEE', data=f)
    print(f"Status: {response.status_code}")
```

**Avec JavaScript (fetch):**
```javascript
const file = document.getElementById('fileInput').files[0];
fetch('URL_PRESIGNEE', {
    method: 'PUT',
    body: file
})
.then(response => console.log('Upload réussi:', response.status))
.catch(error => console.error('Erreur:', error));
```

### Utilisation comme module Python

Vous pouvez également importer le script dans vos propres applications Python :

```python
from generate_presigned_upload_url import generate_presigned_url

# Générer une URL pré-signée
url = generate_presigned_url(
    bucket_name='my-bucket',
    object_key='uploads/file.pdf',
    expiration=3600,
    content_type='application/pdf'
)

if url:
    print(f"URL générée: {url}")
```

## Permissions AWS requises

Le compte AWS utilisé pour générer les URLs pré-signées doit avoir les permissions suivantes :

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject"
            ],
            "Resource": "arn:aws:s3:::BUCKET_NAME/*"
        }
    ]
}
```

### Configuration minimale IAM

Pour un utilisateur dédié à la génération d'URLs pré-signées :

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowPresignedURLGeneration",
            "Effect": "Allow",
            "Action": [
                "s3:PutObject"
            ],
            "Resource": [
                "arn:aws:s3:::my-bucket/uploads/*"
            ]
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
