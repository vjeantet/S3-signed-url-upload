# S3 Presigned URL Upload

Ce projet contient des scripts pour générer des URLs pré-signées AWS S3 permettant à des utilisateurs non authentifiés d'uploader des fichiers.

## Prérequis

- **AWS CLI** configuré avec des credentials valides
- **Python 3** avec le module `boto3` installé
- **Permissions AWS S3** appropriées pour générer des URLs pré-signées

### Installation des prérequis

```bash
# Installer AWS CLI (si nécessaire)
pip install awscli

# Configurer AWS CLI
aws configure

# Installer boto3
pip3 install boto3
```

## Scripts disponibles

### 1. generate-presigned-upload-url.sh

Génère une URL pré-signée pour permettre l'upload d'un fichier vers un bucket S3.

#### Usage

```bash
./generate-presigned-upload-url.sh <bucket-name> [object-key] [expiration]
```

#### Paramètres

- **bucket-name** (requis) : Nom du bucket S3 cible
- **object-key** (optionnel) : Chemin/nom du fichier dans S3 (défaut: `uploads/file-YYYYMMDD-HHMMSS`)
- **expiration** (optionnel) : Durée de validité en secondes (défaut: 3600 = 1 heure)

#### Exemples

```bash
# Générer une URL avec paramètres par défaut
./generate-presigned-upload-url.sh my-bucket

# Spécifier le chemin du fichier dans S3
./generate-presigned-upload-url.sh my-bucket uploads/document.pdf

# Spécifier une expiration de 2 heures (7200 secondes)
./generate-presigned-upload-url.sh my-bucket uploads/document.pdf 7200
```

#### Utilisation de l'URL générée

Une fois l'URL pré-signée générée, un utilisateur peut uploader un fichier sans credentials AWS :

**Avec curl:**
```bash
curl -X PUT -T "chemin/vers/fichier.pdf" "URL_PRESIGNEE"
```

**Avec wget:**
```bash
wget --method=PUT --body-file="chemin/vers/fichier.pdf" "URL_PRESIGNEE"
```

**Avec Python:**
```python
import requests

with open('fichier.pdf', 'rb') as f:
    response = requests.put('URL_PRESIGNEE', data=f)
    print(f"Status: {response.status_code}")
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

## Sécurité

- Les URLs pré-signées expirent après la durée spécifiée
- Ne partagez les URLs qu'avec des utilisateurs de confiance
- Considérez l'utilisation de durées d'expiration courtes pour plus de sécurité
- Les fichiers uploadés héritent des permissions par défaut du bucket

## Dépannage

### Erreur: AWS CLI n'est pas configuré
```bash
aws configure
```
Entrez vos credentials AWS (Access Key ID, Secret Access Key, région).

### Erreur: boto3 n'est pas installé
```bash
pip3 install boto3
```

### Erreur: Access Denied
Vérifiez que vos credentials AWS ont les permissions nécessaires pour le bucket S3 cible.

## Licence

MIT
