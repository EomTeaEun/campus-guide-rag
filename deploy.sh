#!/usr/bin/env bash
set -euo pipefail
export AWS_DEFAULT_REGION=ap-northeast-2
export AWS_PAGER=''
cd "$(dirname "$0")"
aws cloudformation deploy --stack-name campus-guide-rag-week2 --template-file infrastructure.json --capabilities CAPABILITY_IAM --no-fail-on-empty-changeset --tags Project=CampusGuide Stage=Week2
BUCKET=$(aws cloudformation describe-stacks --stack-name campus-guide-rag-week2 --query "Stacks[0].Outputs[?OutputKey=='DocumentBucket'].OutputValue | [0]" --output text)
aws s3 cp manifest.json "s3://$BUCKET/documents/manifest.json" --content-type 'application/json; charset=utf-8'
aws s3 cp scholarship-01.txt "s3://$BUCKET/documents/scholarship-01.txt" --content-type 'text/plain; charset=utf-8'
aws cloudformation describe-stacks --stack-name campus-guide-rag-week2 --query 'Stacks[0].Outputs' --output json | tee deployment.json
