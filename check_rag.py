import json,app,time
from pathlib import Path
chunks=json.loads(Path('documents/vector-index.json').read_text())['chunks'];results=[]
for q in ['교내 장학금 신청에 필요한 서류가 뭐야?','일반 휴학은 어떻게 신청해?','도서관 책은 몇 권까지, 며칠 동안 빌릴 수 있어?','2027년 장학금 지급액이 정확히 얼마야?','양자컴퓨터 냉각장치 설계 방법을 알려줘']:
 s=app.retrieve(q,app.embed(q),chunks)
 r=app.generate(q,s) if s else {'answer':'자료에서 확인할 수 없습니다.','citations':[],'abstain':True}
 out={'question':q,'retrieved':[(d['id'],d['score']) for d in s],'result':r};results.append(out);print(json.dumps(out,ensure_ascii=False),flush=True)
Path('rag-verification.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
