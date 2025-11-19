#!/usr/bin/env python3

"""
Script: generate-presigned-download-url.py
Description: Generates an AWS S3 presigned URL to allow file download
             by an unauthenticated user
Usage: ./generate-presigned-download-url.py <bucket-name> <object-key> [options]
"""

import argparse
import sys
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


def check_object_exists(bucket_name: str, object_key: str) -> bool:
    """
    Checks if the object exists in the S3 bucket.

    Args:
        bucket_name: S3 bucket name
        object_key: Object key in S3

    Returns:
        bool: True if object exists, False otherwise
    """
    try:
        s3_client = boto3.client('s3')
        s3_client.head_object(Bucket=bucket_name, Key=object_key)
        return True
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        if error_code == '404':
            return False
        print_warning(f"Unable to verify object existence: {e}")
        return True  # Continue anyway
    except Exception:
        return True  # Continue on error


def get_object_info(bucket_name: str, object_key: str) -> Optional[dict]:
    """
    Retrieves information about the S3 object.

    Args:
        bucket_name: S3 bucket name
        object_key: Object key in S3

    Returns:
        Optional[dict]: Object information or None
    """
    try:
        s3_client = boto3.client('s3')
        response = s3_client.head_object(Bucket=bucket_name, Key=object_key)

        size_bytes = response.get('ContentLength', 0)

        # Convert to readable format
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
    Generates a presigned URL to download an object from S3.

    Args:
        bucket_name: S3 bucket name
        object_key: Object key/path in S3
        expiration: Validity duration in seconds (default: 3600)
        filename: Suggested filename for download (optional)

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

        # Add suggested filename if specified
        response_content_disposition = None
        if filename:
            response_content_disposition = f'attachment; filename="{filename}"'
            params['ResponseContentDisposition'] = response_content_disposition

        # Generate presigned URL for GET
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
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


def print_usage_examples(presigned_url: str, expiration: int, object_key: str) -> None:
    """
    Displays usage examples for the presigned URL.

    Args:
        presigned_url: The generated presigned URL
        expiration: Validity duration in seconds
        object_key: Object key
    """
    print()
    print("━" * 70)
    print_success("PRESIGNED DOWNLOAD URL:")
    print(presigned_url)
    print("━" * 70)
    print()

    print_warning("To download the file with this URL:")
    print()
    print("  With the provided script:")
    print(f'  ./download-from-presigned-url.sh "{presigned_url}"')
    print()
    print("  With curl:")
    print(f'  curl -o "file" "{presigned_url}"')
    print()
    print("  With wget:")
    print(f'  wget -O "file" "{presigned_url}"')
    print()
    print("  In a web browser:")
    print("  Simply paste the URL in the address bar")
    print()
    print("  With Python requests:")
    print("  import requests")
    print(f"  response = requests.get('{presigned_url[:50]}...')")
    print("  with open('file', 'wb') as f:")
    print("      f.write(response.content)")
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
        description="Generates an AWS S3 presigned URL for file download",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s my-bucket uploads/document.pdf
  %(prog)s my-bucket uploads/document.pdf --expiration 7200
  %(prog)s my-bucket uploads/photo.jpg --filename "my-photo.jpg"
  %(prog)s my-bucket data/report.xlsx --expiration 300 --filename "report-2025.xlsx"

Prerequisites:
  - Python 3 with boto3 installed (pip3 install boto3)
  - Configured AWS credentials (aws configure)
  - S3 permissions to generate presigned URLs (s3:GetObject)
  - The file must exist in the S3 bucket
        """
    )

    parser.add_argument(
        'bucket_name',
        help='S3 bucket name (required)'
    )

    parser.add_argument(
        'object_key',
        help='Object key/path in S3 (required)'
    )

    parser.add_argument(
        '--expiration', '-e',
        type=int,
        help='Validity duration in seconds (default: 3600 = 1 hour)',
        default=3600
    )

    parser.add_argument(
        '--filename', '-f',
        help='Suggested filename for download',
        default=None
    )

    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Quiet mode - displays only the URL'
    )

    parser.add_argument(
        '--no-check',
        action='store_true',
        help='Do not check if the file exists (faster)'
    )

    args = parser.parse_args()

    # Validate arguments
    if args.expiration < 1:
        print_error("Error: Expiration must be at least 1 second")
        sys.exit(1)

    if args.expiration > 604800:  # 7 days
        print_warning("Warning: Maximum recommended expiration is 7 days (604800 seconds)")

    if not args.quiet:
        print_warning("Checking prerequisites...")
        print()

        # Check AWS credentials
        if not check_aws_credentials():
            sys.exit(1)

        print()
        print_warning("Generating presigned download URL...")
        print(f"Bucket: {args.bucket_name}")
        print(f"Object Key: {args.object_key}")
        print(f"Expiration: {args.expiration} seconds")
        if args.filename:
            print(f"Suggested filename: {args.filename}")
        print()

        # Check if object exists (if not disabled)
        if not args.no_check:
            print_info("Checking file existence...")
            if not check_object_exists(args.bucket_name, args.object_key):
                print_error(f"The file '{args.object_key}' does not exist in bucket '{args.bucket_name}'")
                print_warning("Use --no-check to skip this verification")
                sys.exit(1)

            # Display file information
            info = get_object_info(args.bucket_name, args.object_key)
            if info:
                print_success("✓ File found")
                print(f"  Size: {info['size']}")
                print(f"  Type: {info['content_type']}")
                print(f"  Last modified: {info['last_modified']}")
            print()

    # Generate presigned URL
    presigned_url = generate_presigned_download_url(
        args.bucket_name,
        args.object_key,
        args.expiration,
        args.filename
    )

    if not presigned_url:
        print_error("Failed to generate presigned URL")
        sys.exit(1)

    # Display results
    if args.quiet:
        print(presigned_url)
    else:
        print_success("✓ Presigned download URL generated successfully!")
        print_usage_examples(presigned_url, args.expiration, args.object_key)


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
