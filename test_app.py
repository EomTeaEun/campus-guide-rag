import importlib.util
import json
import unittest
from pathlib import Path
from unittest.mock import patch
spec = importlib.util.spec_from_file_location('app', Path(__file__).parent / 'app.py')
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)

def event(path, method='GET'):
    return {'rawPath': path, 'requestContext': {'http': {'method': method}}}

class ApiTests(unittest.TestCase):
    def test_health_does_not_claim_rag(self):
        r = app.handler(event('/health'), None)
        self.assertEqual(r['statusCode'], 200)
        self.assertFalse(json.loads(r['body'])['rag_enabled'])
    def test_s3_manifest_and_fictional_label(self):
        with patch.object(app, 'read_manifest', return_value=[{'id': 'scholarship-01'}]):
            r = app.handler(event('/documents'), None)
        body = json.loads(r['body'])
        self.assertEqual(body['count'], 1)
        self.assertTrue(body['fictional'])
    def test_storage_failure_is_not_success(self):
        with patch.object(app, 'read_manifest', side_effect=RuntimeError('unavailable')):
            self.assertEqual(app.handler(event('/documents'), None)['statusCode'], 503)
    def test_unknown_route_and_method(self):
        self.assertEqual(app.handler(event('/missing'), None)['statusCode'], 404)
        self.assertEqual(app.handler(event('/health','POST'), None)['statusCode'], 405)

if __name__ == '__main__':
    unittest.main()
