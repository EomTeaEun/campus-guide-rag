#!/usr/bin/env bash
set -euo pipefail
export AWS_DEFAULT_REGION=ap-northeast-2 AWS_PAGER=''
aws lambda put-function-concurrency --function-name campus-guide-rag-api --reserved-concurrent-executions 2
aws apigatewayv2 update-api --api-id ip970smv8k --no-disable-execute-api-endpoint >/dev/null
