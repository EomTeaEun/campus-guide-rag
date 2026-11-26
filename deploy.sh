#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export AWS_DEFAULT_REGION=ap-northeast-2 AWS_PAGER=''
python3 make_corpus.py
python3 build_index.py
python3 make_template.py
aws cloudformation deploy --stack-name campus-guide-rag-week2 --template-file infrastructure.json --capabilities CAPABILITY_IAM --no-fail-on-empty-changeset --tags Project=CampusGuide Stage=Week3
BUCKET=$(aws cloudformation describe-stacks --stack-name campus-guide-rag-week2 --query "Stacks[0].Outputs[?OutputKey=='DocumentBucket'].OutputValue | [0]" --output text)
aws s3 cp documents/ "s3://$BUCKET/documents/" --recursive
aws cloudformation describe-stacks --stack-name campus-guide-rag-week2 --query 'Stacks[0].Outputs' --output json
