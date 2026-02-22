from typing import Any
import json
import os
import subprocess

import boto3
from botocore.exceptions import (
    UnauthorizedSSOTokenError,
    TokenRetrievalError,
    SSOTokenLoadError,
)


def get_aws_session(region: str = "eu-north-1") -> boto3.Session:
    running_in_github = os.getenv("GITHUB_ACTIONS") == "true"

    if running_in_github:
        print("Running in GitHub Actions - using default AWS credentials")
        return boto3.Session(region_name=region)
    else:
        session = boto3.Session(profile_name="ronantfs", region_name=region)
        try:
            session.client("sts").get_caller_identity()
        except (UnauthorizedSSOTokenError, TokenRetrievalError, SSOTokenLoadError, Exception) as e:
            if "SSO" in str(e) or "token" in str(e).lower() or "expired" in str(e).lower():
                print("SSO session expired or not active. Running: aws sso login --profile ronantfs")
                subprocess.run(["aws", "sso", "login", "--profile", "ronantfs"], check=True)
                session = boto3.Session(profile_name="ronantfs", region_name=region)
            else:
                raise
        print("Using local AWS SSO profile: ronantfs")
        return session


def get_s3_client():
    running_in_aws = os.getenv("AWS_EXECUTION_ENV") is not None  # set in Lambda
    running_in_github = os.getenv("GITHUB_ACTIONS") == "true"

    if running_in_aws or running_in_github:
        print("Running in AWS-managed environment - using default credentials")
        session = boto3.Session()
    else:
        session = get_aws_session()

    return session.client("s3")


def upload_dict_to_s3(s3_client, bucket: str, key: str, data: Any) -> None:
    s3_client.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8"),
    )


def download_json_from_s3(s3_client, bucket: str, key: str) -> Any:
    try:
        obj = s3_client.get_object(Bucket=bucket, Key=key)
        raw = obj["Body"].read().decode("utf-8")
        return json.loads(raw)
    except s3_client.exceptions.NoSuchKey:
        raise FileNotFoundError(f"S3 key not found: {key}")
    except Exception as e:
        raise RuntimeError(f"Failed to download {key}: {e}")
