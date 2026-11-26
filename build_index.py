"""Run in authenticated AWS CloudShell. Builds a versioned vector index."""
import json,boto3,hashlib
from pathlib import Path
from datetime import datetime,timezone
root=Path(__file__).parent
runtime=boto3.client('bedrock-runtime',region_name='ap-northeast-2')
chunks=json.loads((root/'corpus.json').read_text())
for d in chunks:
 text=d['title']+'\n'+d['section']+'\n'+d['keywords']+'\n'+d['text']
 r=runtime.invoke_model(modelId='amazon.titan-embed-text-v2:0',body=json.dumps({'inputText':text,'dimensions':256,'normalize':True}),contentType='application/json')
 d['embedding']=json.loads(r['body'].read())['embedding']
 assert len(d['embedding'])==256
 print('EMBEDDED',d['id'],flush=True)
index={'embedding_model':'amazon.titan-embed-text-v2:0','dimensions':256,'generated_at':datetime.now(timezone.utc).isoformat(),'corpus_sha256':hashlib.sha256((root/'corpus.json').read_bytes()).hexdigest(),'chunks':chunks}
(root/'documents/vector-index.json').write_text(json.dumps(index,ensure_ascii=False))
print('INDEX_READY',len(chunks),flush=True)
