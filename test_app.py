import unittest,json,io,math
from unittest.mock import patch,MagicMock
import app

def event(q=None,**extra):
 e={'rawPath':'/chat','requestContext':{'http':{'method':'POST'}},'body':json.dumps({'question':q})};e.update(extra);return e
class RagTests(unittest.TestCase):
 def test_empty_rejected_without_billing(self):
  with patch('app.quota') as q:
   self.assertEqual(app.handler(event(' '),None)['statusCode'],400);q.assert_not_called()
 def test_bad_json_and_nonobject(self):
  for body in ['{','[]','null']:
   self.assertEqual(app.handler(event(body=body),None)['statusCode'],400)
 def test_long_rejected(self):self.assertEqual(app.handler(event('가'*501),None)['statusCode'],400)
 def test_base64_question(self):
  import base64
  e=event();e['body']=base64.b64encode(json.dumps({'question':' '}).encode()).decode();e['isBase64Encoded']=True
  self.assertEqual(app.handler(e,None)['statusCode'],400)
 def test_quota_prevents_model_calls(self):
  with patch('app.quota',return_value=False),patch('app.embed') as embed:
   self.assertEqual(app.handler(event('장학금 서류'),None)['statusCode'],429);embed.assert_not_called()
 def test_real_pipeline_returns_actual_citation_mapping(self):
  d={'id':'scholarship-01','title':'장학금','section':'서류','text':'신청서와 재학증명서','keywords':'장학금 서류','version':'1.0','effective_date':'2026-11-26','embedding':[1,0]}
  with patch('app.quota',return_value=True),patch('app.embed',return_value=[1,0]),patch('app.load_index',return_value=[d]),patch('app.generate',return_value={'answer':'신청서와 재학증명서입니다. [1]','citations':[1],'abstain':False}):
   out=json.loads(app.handler(event('장학금 서류'),None)['body']);self.assertEqual(out['sources'][0]['id'],d['id']);self.assertEqual(out['sources'][0]['url'],'/source?id=scholarship-01')
 def test_unrelated_retrieval_abstains_without_generation(self):
  d={'title':'장학','keywords':'장학','embedding':[1,0]}
  with patch('app.quota',return_value=True),patch('app.embed',return_value=[0,1]),patch('app.load_index',return_value=[d]),patch('app.generate') as gen:
   out=json.loads(app.handler(event('우주선 엔진 설계'),None)['body']);self.assertTrue(out['abstain']);self.assertEqual(out['sources'],[]);gen.assert_not_called()
 def test_model_invalid_citation_is_rejected(self):
  bedrock=MagicMock();bedrock.converse.return_value={'output':{'message':{'content':[{'text':'{"answer":"확인 [9]","citations":[9],"abstain":false}'}]}}}
  with patch('app.client',return_value=bedrock):
   with self.assertRaises(ValueError):app.generate('질문',[{'title':'문서','section':'절','text':'내용'}])
 def test_valid_and_abstaining_model_json(self):
  for data in [{'answer':'신청서입니다. [1]','citations':[1],'abstain':False},{'answer':'자료에 없습니다.','citations':[],'abstain':True}]:
   bedrock=MagicMock();bedrock.converse.return_value={'output':{'message':{'content':[{'text':json.dumps(data)}]}}}
   with patch('app.client',return_value=bedrock):self.assertEqual(app.generate('질문',[{'title':'제목','section':'절','text':'내용'}])['abstain'],data['abstain'])
 def test_storage_failure_no_fake_success(self):
  with patch('app.quota',return_value=True),patch('app.embed',return_value=[1]),patch('app.load_index',side_effect=RuntimeError('storage down')):
   r=app.handler(event('장학금 서류'),None);self.assertEqual(r['statusCode'],503);self.assertNotIn('answer',json.loads(r['body']))
 def test_source_path_traversal(self):
  e={'rawPath':'/source','queryStringParameters':{'id':'../../secret'}}
  with patch('app.client') as client:
   self.assertEqual(app.handler(e,None)['statusCode'],400);client.assert_not_called()
 def test_missing_source_returns_404(self):
  class MissingSource(Exception):
   response={'Error':{'Code':'NoSuchKey'}}
  c=MagicMock();c.get_object.side_effect=MissingSource()
  with patch.dict('os.environ',{'DOCUMENT_BUCKET':'test-bucket'}),patch('app.client',return_value=c):
   e={'rawPath':'/source','queryStringParameters':{'id':'missing-01'}}
   self.assertEqual(app.handler(e,None)['statusCode'],404)
 def test_unknown_source_checked_against_manifest_before_s3_read(self):
  c=MagicMock();c.get_object.return_value={'Body':io.BytesIO(b'[{"id":"scholarship-01"}]')}
  with patch.dict('os.environ',{'DOCUMENT_BUCKET':'test-bucket'}),patch('app.client',return_value=c):
   e={'rawPath':'/source','queryStringParameters':{'id':'missing-01'}}
   self.assertEqual(app.handler(e,None)['statusCode'],404)
   self.assertEqual(c.get_object.call_count,1)
   self.assertEqual(c.get_object.call_args.kwargs['Key'],'documents/manifest.json')
 def test_vector_dimension_mismatch(self):
  with self.assertRaises(ValueError):app.cosine([1,0],[1])
 def test_ui_no_external_api_secret(self):
  r=app.handler({'rawPath':'/'},None);self.assertEqual(r['statusCode'],200);self.assertIn('text/html',r['headers']['content-type']);self.assertIn("fetch('/chat'",r['body'])
if __name__=='__main__':unittest.main()
