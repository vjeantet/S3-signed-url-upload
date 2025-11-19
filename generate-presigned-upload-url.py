#!/usr/bin/env python3

"""
Script: generate-presigned-upload-url.py
Description: Generates an AWS S3 presigned URL to allow file upload
             by an unauthenticated user
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
    print("Error: The boto3 module is not installed")
    print("Install it with: pip3 install boto3")
    sys.exit(1)


# ANSI color codes
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


def print_error(message: str) -> None:
    """Displays an error message in red."""
    print(f"{Colors.RED}{message}{Colors.NC}", file=sys.stderr)


def print_success(message: str) -> None:
    """Displays a success message in green."""
    print(f"{Colors.GREEN}{message}{Colors.NC}")


def print_warning(message: str) -> None:
    """Displays a warning message in yellow."""
    print(f"{Colors.YELLOW}{message}{Colors.NC}")


def print_info(message: str) -> None:
    """Displays an info message in blue."""
    print(f"{Colors.BLUE}{message}{Colors.NC}")


def check_aws_credentials() -> bool:
    """
    Verifies that AWS credentials are configured correctly.

    Returns:
        bool: True if credentials are valid, False otherwise
    """
    try:
        sts_client = boto3.client('sts')
        identity = sts_client.get_caller_identity()
        print_success("✓ Valid AWS credentials")
        print(f"  Account: {identity['Account']}")
        print(f"  UserId: {identity['UserId']}")
        print(f"  ARN: {identity['Arn']}")
        return True
    except NoCredentialsError:
        print_error("Error: AWS credentials not found")
        print_warning("Configure your credentials with: aws configure")
        return False
    except ClientError as e:
        print_error(f"Error verifying credentials: {e}")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False


def generate_default_object_key() -> str:
    """
    Generates a default object key with timestamp.

    Returns:
        str: Object key with format uploads/file-YYYYMMDD-HHMMSS
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
    Generates a presigned URL to upload an object to S3.

    Args:
        bucket_name: S3 bucket name
        object_key: Object key/path in S3
        expiration: Validity duration in seconds (default: 3600)
        content_type: File MIME type (optional)

    Returns:
        Optional[str]: Presigned URL or None on error
    """
    try:
        s3_client = boto3.client('s3')

        # Prepare parameters
        params = {
            'Bucket': bucket_name,
            'Key': object_key
        }

        # Add Content-Type if specified
        if content_type:
            params['ContentType'] = content_type

        # Generate presigned URL for PUT
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params=params,
            ExpiresIn=expiration
        )

        return presigned_url

    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        error_message = e.response.get('Error', {}).get('Message', str(e))
        print_error(f"AWS Error ({error_code}): {error_message}")
        return None
    except Exception as e:
        print_error(f"Error generating URL: {e}")
        return None


def print_usage_examples(presigned_url: str, expiration: int) -> None:
    """
    Displays usage examples for the presigned URL.

    Args:
        presigned_url: The generated presigned URL
        expiration: Validity duration in seconds
    """
    print()
    print("━" * 70)
    print_success("PRESIGNED URL:")
    print(presigned_url)
    print("━" * 70)
    print()

    print_warning("To upload a file with this URL, use:")
    print()
    print("  With curl:")
    print(f'  curl -X PUT -T "path/to/file" "{presigned_url}"')
    print()
    print("  With wget:")
    print(f'  wget --method=PUT --body-file="path/to/file" "{presigned_url}"')
    print()
    print("  With Python requests:")
    print("  import requests")
    print("  with open('file', 'rb') as f:")
    print(f"      response = requests.put('{presigned_url[:50]}...', data=f)")
    print()

    # Convert duration to readable format
    hours = expiration // 3600
    minutes = (expiration % 3600) // 60
    seconds = expiration % 60

    duration_parts = []
    if hours > 0:
        duration_parts.append(f"{hours} hour{'s' if hours > 1 else ''}")
    if minutes > 0:
        duration_parts.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
    if seconds > 0 or not duration_parts:
        duration_parts.append(f"{seconds} second{'s' if seconds > 1 else ''}")

    duration_str = " ".join(duration_parts)
    print_warning(f"The URL expires in {duration_str}")
    print()


def main():
    """Main script function."""
    parser = argparse.ArgumentParser(
        description="Generates an AWS S3 presigned URL for file upload",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s my-bucket
  %(prog)s my-bucket --object-key uploads/document.pdf
  %(prog)s my-bucket --object-key uploads/document.pdf --expiration 7200
  %(prog)s my-bucket --object-key image.jpg --content-type image/jpeg

Prerequisites:
  - Python 3 with boto3 installed (pip3 install boto3)
  - Configured AWS credentials (aws configure)
  - S3 permissions to generate presigned URLs
        """
    )

    parser.add_argument(
        'bucket_name',
        help='S3 bucket name (required)'
    )

    parser.add_argument(
        '--object-key', '-k',
        help='Object key/name in S3 (default: uploads/file-YYYYMMDD-HHMMSS)',
        default=None
    )

    parser.add_argument(
        '--expiration', '-e',
        type=int,
        help='Validity duration in seconds (default: 3600 = 1 hour)',
        default=3600
    )

    parser.add_argument(
        '--content-type', '-t',
        help='File MIME type (e.g., image/jpeg, application/pdf)',
        default=None
    )

    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Quiet mode - displays only the URL'
    )

    args = parser.parse_args()

    # Validate arguments
    if args.expiration < 1:
        print_error("Error: Expiration must be at least 1 second")
        sys.exit(1)

    if args.expiration > 604800:  # 7 days
        print_warning("Warning: Maximum recommended expiration is 7 days (604800 seconds)")

    # Generate object key if not provided
    object_key = args.object_key if args.object_key else generate_default_object_key()

    if not args.quiet:
        print_warning("Checking prerequisites...")
        print()

        # Check AWS credentials
        if not check_aws_credentials():
            sys.exit(1)

        print()
        print_warning("Generating presigned URL...")
        print(f"Bucket: {args.bucket_name}")
        print(f"Object Key: {object_key}")
        print(f"Expiration: {args.expiration} seconds")
        if args.content_type:
            print(f"Content-Type: {args.content_type}")
        print()

    # Generate presigned URL
    presigned_url = generate_presigned_url(
        args.bucket_name,
        object_key,
        args.expiration,
        args.content_type
    )

    if not presigned_url:
        print_error("Failed to generate presigned URL")
        sys.exit(1)

    # Display results
    if args.quiet:
        print(presigned_url)
    else:
        print_success("✓ Presigned URL generated successfully!")
        print_usage_examples(presigned_url, args.expiration)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()
        print_warning("Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print_error(f"Fatal error: {e}")
        sys.exit(1)
