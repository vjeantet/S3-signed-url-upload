# S3 Presigned URL Upload & Download

This project contains scripts to manage file uploads and downloads to/from AWS S3 via presigned URLs:
- **For administrators**: Python scripts to generate presigned URLs (upload and download)
- **For users**: Bash scripts to upload/download files without AWS authentication

## Prerequisites

### For administrators (URL generation)

- **Python 3.6+**
- **boto3**: AWS SDK for Python
- **Configured AWS credentials**

### For end users (file upload and download)

- **curl**: Data transfer tool (usually pre-installed)
- **No AWS authentication required**

## Installation

### For administrators

```bash
# Install boto3
pip3 install boto3

# Configure AWS credentials (if not already done)
aws configure
# OR set environment variables:
# export AWS_ACCESS_KEY_ID=your_access_key
# export AWS_SECRET_ACCESS_KEY=your_secret_key
# export AWS_DEFAULT_REGION=us-east-1
```

### For end users

```bash
# Check if curl is installed
curl --version

# If curl is not installed:
# Ubuntu/Debian:
sudo apt-get install curl

# macOS (with Homebrew):
brew install curl

# CentOS/RHEL:
sudo yum install curl
```

## Available Scripts

### 1. generate-presigned-upload-url.py (For AWS administrators)

Python script to generate a presigned URL allowing file upload to an S3 bucket.

**Prerequisites:** Valid AWS credentials

#### Usage

```bash
./generate-presigned-upload-url.py <bucket-name> [options]
```

#### Options

- **bucket_name** (positional, required): Target S3 bucket name
- **--object-key, -k**: File path/name in S3 (default: `uploads/file-YYYYMMDD-HHMMSS`)
- **--expiration, -e**: Validity duration in seconds (default: 3600 = 1 hour)
- **--content-type, -t**: File MIME type (e.g., `image/jpeg`, `application/pdf`)
- **--quiet, -q**: Quiet mode - displays only the URL
- **--help, -h**: Display help

#### Examples

```bash
# Generate a URL with default parameters
./generate-presigned-upload-url.py my-bucket

# Specify the file path in S3
./generate-presigned-upload-url.py my-bucket --object-key uploads/document.pdf

# Specify a 2-hour expiration (7200 seconds)
./generate-presigned-upload-url.py my-bucket -k uploads/document.pdf -e 7200

# With a specific MIME type
./generate-presigned-upload-url.py my-bucket -k images/photo.jpg -t image/jpeg

# Quiet mode (for scripts)
./generate-presigned-upload-url.py my-bucket -q
```

#### Features

- ✅ Presigned URL generation for PUT operation
- ✅ Custom Content-Type support
- ✅ Automatic AWS credentials validation
- ✅ Colored and formatted output display
- ✅ Quiet mode for script integration
- ✅ Complete error handling with explicit messages
- ✅ Built-in usage examples

---

### 2. upload-to-presigned-url.sh (For end users)

Bash script to upload a file to S3 using a presigned URL.

**Prerequisites:** No AWS authentication required, only `curl`

#### Usage

```bash
./upload-to-presigned-url.sh <file> <presigned-url> [options]
```

#### Options

- **file** (positional, required): Path to the file to upload
- **presigned-url** (positional, required): Presigned URL provided by the administrator
- **-v, --verbose**: Verbose mode - displays more details
- **-h, --help**: Display help

#### Examples

```bash
# Basic upload
./upload-to-presigned-url.sh document.pdf "https://bucket.s3.amazonaws.com/..."

# With verbose mode
./upload-to-presigned-url.sh photo.jpg "https://bucket.s3.amazonaws.com/..." --verbose

# The URL must be in quotes
./upload-to-presigned-url.sh report.xlsx "https://my-bucket.s3.us-east-1.amazonaws.com/..."
```

#### Features

- ✅ Simple upload without AWS credentials
- ✅ Automatic MIME type detection
- ✅ Progress display
- ✅ Error handling with explicit messages
- ✅ File validation before upload
- ✅ Support for all file types
- ✅ Detailed error messages (expired URL, access denied, etc.)

#### Return Codes

- **0**: Upload successful
- **1**: Error (file not found, expired URL, access denied, etc.)

---

### 3. generate-presigned-download-url.py (For AWS administrators)

Python script to generate a presigned URL allowing file download from an S3 bucket.

**Prerequisites:** Valid AWS credentials

#### Usage

```bash
./generate-presigned-download-url.py <bucket-name> <object-key> [options]
```

#### Options

- **bucket_name** (positional, required): Target S3 bucket name
- **object_key** (positional, required): File path/name in S3
- **--expiration, -e**: Validity duration in seconds (default: 3600 = 1 hour)
- **--filename, -f**: Suggested filename for download
- **--quiet, -q**: Quiet mode - displays only the URL
- **--no-check**: Don't check if the file exists (faster)
- **--help, -h**: Display help

#### Examples

```bash
# Generate a URL to download an existing file
./generate-presigned-download-url.py my-bucket uploads/document.pdf

# Specify a 2-hour expiration (7200 seconds)
./generate-presigned-download-url.py my-bucket uploads/document.pdf -e 7200

# Suggest a filename for download
./generate-presigned-download-url.py my-bucket data/report.xlsx --filename "report-2025.xlsx"

# Quiet mode (for scripts)
./generate-presigned-download-url.py my-bucket uploads/photo.jpg -q
```

#### Features

- ✅ Presigned URL generation for GET operation
- ✅ Automatic file existence verification
- ✅ File information display (size, type, date)
- ✅ Support for suggested filename for download
- ✅ Automatic AWS credentials validation
- ✅ Colored and formatted output display
- ✅ Quiet mode for script integration
- ✅ Complete error handling with explicit messages

---

### 4. download-from-presigned-url.sh (For end users)

Bash script to download a file from S3 using a presigned URL.

**Prerequisites:** No AWS authentication required, only `curl`

#### Usage

```bash
./download-from-presigned-url.sh <presigned-url> [destination-file] [options]
```

#### Options

- **presigned-url** (positional, required): Presigned URL provided by the administrator
- **destination-file** (positional, optional): Path where to save the file
- **-v, --verbose**: Verbose mode - displays more details
- **-h, --help**: Display help

#### Examples

```bash
# Basic download (auto-detected filename)
./download-from-presigned-url.sh "https://bucket.s3.amazonaws.com/..."

# Specify the destination filename
./download-from-presigned-url.sh "https://bucket.s3.amazonaws.com/..." document.pdf

# With full path and verbose mode
./download-from-presigned-url.sh "https://bucket.s3.amazonaws.com/..." ./downloads/report.pdf --verbose
```

#### Features

- ✅ Simple download without AWS credentials
- ✅ Automatic filename detection from URL
- ✅ File information display (size, type)
- ✅ Progress display
- ✅ Error handling with explicit messages
- ✅ Existing file overwrite verification
- ✅ Automatic cleanup on error
- ✅ Detailed error messages (expired URL, file not found, etc.)

#### Return Codes

- **0**: Download successful
- **1**: Error (expired URL, file not found, access denied, etc.)

---

### Complete Workflows

#### Upload Workflow

#### Step 1: Administrator generates the URL

```bash
# Admin generates a presigned URL
./generate-presigned-upload-url.py my-bucket -k uploads/report.pdf -e 3600

# Output: https://my-bucket.s3.amazonaws.com/uploads/report.pdf?X-Amz-Algorithm=...
```

#### Step 2: Administrator shares the URL

The administrator sends the presigned URL to the user (email, chat, etc.)

#### Step 3: User uploads the file

```bash
# User uploads their file (without AWS credentials)
./upload-to-presigned-url.sh report.pdf "https://my-bucket.s3.amazonaws.com/..."

# ✓ Upload successful!
```

#### Download Workflow

#### Step 1: Administrator generates the download URL

```bash
# Admin generates a presigned URL to download an existing file
./generate-presigned-download-url.py my-bucket uploads/report.pdf -e 3600

# Output: https://my-bucket.s3.amazonaws.com/uploads/report.pdf?X-Amz-Algorithm=...
```

#### Step 2: Administrator shares the URL

The administrator sends the presigned URL to the user (email, chat, etc.)

#### Step 3: User downloads the file

```bash
# User downloads the file (without AWS credentials)
./download-from-presigned-url.sh "https://my-bucket.s3.amazonaws.com/..." report.pdf

# ✓ Download successful!
```

---

### Using the Generated URL (Alternative Methods)

#### For Upload

Once the upload presigned URL is generated, a user can upload a file without AWS credentials:

**With curl:**
```bash
curl -X PUT -T "path/to/file.pdf" "PRESIGNED_UPLOAD_URL"
```

**With wget:**
```bash
wget --method=PUT --body-file="path/to/file.pdf" "PRESIGNED_UPLOAD_URL"
```

**With Python requests:**
```python
import requests

with open('file.pdf', 'rb') as f:
    response = requests.put('PRESIGNED_UPLOAD_URL', data=f)
    print(f"Status: {response.status_code}")
```

**With JavaScript (fetch):**
```javascript
const file = document.getElementById('fileInput').files[0];
fetch('PRESIGNED_UPLOAD_URL', {
    method: 'PUT',
    body: file
})
.then(response => console.log('Upload successful:', response.status))
.catch(error => console.error('Error:', error));
```

#### For Download

Once the download presigned URL is generated, a user can download the file without AWS credentials:

**With curl:**
```bash
curl -o "file.pdf" "PRESIGNED_DOWNLOAD_URL"
```

**With wget:**
```bash
wget -O "file.pdf" "PRESIGNED_DOWNLOAD_URL"
```

**With Python requests:**
```python
import requests

response = requests.get('PRESIGNED_DOWNLOAD_URL')
with open('file.pdf', 'wb') as f:
    f.write(response.content)
print(f"Status: {response.status_code}")
```

**With JavaScript (fetch):**
```javascript
fetch('PRESIGNED_DOWNLOAD_URL')
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'file.pdf';
        a.click();
    })
    .catch(error => console.error('Error:', error));
```

**In a web browser:**
```
Simply paste the URL in the address bar to download the file
```

### Using as a Python Module

You can also import the scripts into your own Python applications:

#### For Upload

```python
from generate_presigned_upload_url import generate_presigned_url

# Generate a presigned URL for upload
url = generate_presigned_url(
    bucket_name='my-bucket',
    object_key='uploads/file.pdf',
    expiration=3600,
    content_type='application/pdf'
)

if url:
    print(f"Upload URL generated: {url}")
```

#### For Download

```python
from generate_presigned_download_url import generate_presigned_download_url

# Generate a presigned URL for download
url = generate_presigned_download_url(
    bucket_name='my-bucket',
    object_key='uploads/file.pdf',
    expiration=3600,
    filename='my-file.pdf'
)

if url:
    print(f"Download URL generated: {url}")
```

## Required AWS Permissions

The AWS account used to generate presigned URLs must have the following permissions:

### For Upload and Download

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

### Minimal IAM Configuration

For a user dedicated to generating presigned URLs (upload and download):

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

### Separate Permissions (Recommended)

If you want to separate responsibilities:

**Upload-only User:**
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

**Download-only User:**
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

## Security

### Best Practices

- ✅ Presigned URLs expire after the specified duration
- ✅ Use short expiration times (< 1 hour) for sensitive data
- ✅ Only share URLs with trusted users
- ✅ Restrict IAM permissions to the minimum necessary
- ✅ Use key prefixes (e.g., `uploads/`) to isolate uploads
- ✅ Configure bucket policies to limit file types
- ⚠️ Uploaded files inherit the bucket's default permissions
- ⚠️ Consider enabling server-side encryption (SSE)

### Security Limitations

- Presigned URLs cannot restrict file size
- Content-Type can be bypassed by the user
- Consider server-side validation after upload

## Troubleshooting

### Error: "The boto3 module is not installed"
```bash
pip3 install boto3
```

### Error: "AWS credentials not found"
```bash
# Option 1: Configure AWS CLI
aws configure

# Option 2: Environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

### Error: "Access Denied"

Verify that:
1. Your AWS credentials are valid
2. The IAM user has `s3:PutObject` permissions on the bucket
3. The bucket name is correct
4. The AWS region is correct

### Script cannot find Python

```bash
# Check Python version
python3 --version

# If necessary, modify the script's shebang
# From: #!/usr/bin/env python3
# To: #!/usr/bin/python3
```

## Use Cases

### Integration in a Web Application

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

### Automated Script

```bash
#!/bin/bash
# Generate a URL and send it by email

URL=$(./generate-presigned-upload-url.py my-bucket -q)
echo "Here is your upload link: $URL" | mail -s "Upload Link" user@example.com
```

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

## License

MIT
