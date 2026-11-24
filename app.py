"""Week 2 campus guide API. Uses fictional documents; no model calls yet."""
import json
import os
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def response(status, body):
    return {
        'statusCode': status,
        'headers': {'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store'},
        'body': json.dumps(body, ensure_ascii=False),
    }


def read_manifest():
    import boto3
    obj = boto3.client('s3').get_object(Bucket=os.environ['DOCUMENT_BUCKET'], Key='documents/manifest.json')
    return json.loads(obj['Body'].read())


def handler(event, context):
    method = event.get('requestContext', {}).get('http', {}).get('method', 'GET')
    path = event.get('rawPath', '/')
    logger.info(json.dumps({'request_id': getattr(context, 'aws_request_id', 'local'), 'method': method, 'path': path}))
    if method != 'GET':
        return response(405, {'error': 'method_not_allowed'})
    if path in ('/', '/health'):
        return response(200, {
            'service': 'campus-guide-rag', 'name': '캠퍼스 길잡이', 'status': 'ok',
            'stage': 'week2-environment', 'region': os.environ.get('AWS_REGION', 'local'),
            'fictional_university': '한빛대학교', 'rag_enabled': False,
            'message': 'AWS 기본 API 실행 확인 완료. 가상 자료를 사용합니다.',
            'checked_at': datetime.now(timezone.utc).isoformat(),
        })
    if path == '/documents':
        try:
            manifest = read_manifest()
            return response(200, {'fictional': True, 'storage': 'Amazon S3', 'count': len(manifest), 'documents': manifest})
        except Exception:
            logger.exception('document_manifest_read_failed')
            return response(503, {'error': 'document_storage_unavailable'})
    return response(404, {'error': 'not_found'})
