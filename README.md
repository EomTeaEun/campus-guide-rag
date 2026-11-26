# 캠퍼스 길잡이

가상 한빛대학교 안내 자료를 검색해 답변과 출처를 보여주는 3주차 RAG 챗봇 MVP입니다. 모든 문서는 과제용 창작 자료이며 실제 학교의 규정이 아닙니다.

## 접속

- 웹 화면: https://ip970smv8k.execute-api.ap-northeast-2.amazonaws.com/
- 상태 확인: 위 주소의 `/health`
- 문서 목록: `/documents`
- 원문: `/source?id=scholarship-01`
- 질문: `POST /chat`, JSON `{"question":"교내 장학금 제출 서류는?"}`

배포 후 확인한 결과와 배포 중지 여부는 제출 보고서를 함께 확인하세요. 비용 관리로 API를 중지하면 접속이 차단됩니다.

## 구현

브라우저 → API Gateway HTTP API → Lambda → S3 문서 벡터 검색 → Bedrock Nova Lite → 답변과 인용 출처.

- 문서: 가상 안내 20건. 장학금, 수강신청, 휴·복학, 기숙사, 도서관, 증명서, 등록금, 상담, Wi-Fi 등.
- 인덱싱: Titan Text Embeddings V2, 256차원 정규화 벡터. 제목·절·본문·키워드를 임베딩합니다.
- 검색: Lambda에서 코사인 유사도 80%와 한국어 글자 bigram 검색 20%를 결합해 최대 3건을 선택합니다. 최상위 벡터 유사도가 0.30 미만이면 검색 근거 없음으로 처리합니다.
- 답변: `apac.amazon.nova-lite-v1:0`의 Converse API. 선택된 문서를 근거로 한국어 답변을 만들며 인용 번호 범위를 서버에서 검증합니다.
- 자료에 없는 날짜/금액과 무관한 질문은 답변을 보류합니다. 사실 검증을 완전히 보장하는 시스템은 아니므로 원문을 함께 확인해야 합니다.
- 웹: 질문 입력, 예시 질문, 진행 상태, 오류 안내, 답변, 원문 링크, 검색된 자료 확인. HTML/CSS/JavaScript로 구현했으며 API와 같은 HTTPS 주소에서 제공합니다.

1주차의 관리형 Knowledge Bases/OpenSearch 계획은 소규모 MVP의 고정 비용을 줄이기 위해 S3 벡터 파일과 Lambda 검색으로 변경했습니다. 관리형 벡터 DB를 구축한 것으로 표시하지 않습니다. 문서 증가 시 별도 검색 서비스 전환이 필요합니다.

## 비용 및 접근 제한

- 상시 실행 EC2, NAT, ALB, OpenSearch를 이번 MVP에 새로 만들지 않습니다.
- 질문 500자 이내, 답변 생성 최대 650토큰, Lambda 동시 실행 2개.
- DynamoDB 원자적 카운터로 한국시간 하루 전체 서비스 50회 질문을 허용합니다. 사용자별 50회가 아닙니다. 실패 요청도 슬롯을 사용할 수 있습니다.
- 질문·답변 본문은 로그/DB에 저장하지 않습니다. DB에는 날짜, 요청 수, TTL만 저장합니다.
- 브라우저에 AWS 키를 넣지 않습니다. Lambda IAM은 해당 S3 문서, 지정 모델 호출, 자체 로그, 전용 카운터 쓰기만 허용합니다.
- Nova의 APAC 추론 프로파일은 APAC 내 다른 AWS 리전으로 요청이 전달될 수 있습니다.
- 공개 수업용 데모이며 로그인 기능은 없습니다. 사용량 제한은 총금액에 대한 절대 보장이 아닙니다. 기존 수업 자원의 비용은 별도입니다.

## 개발과 테스트

```bash
python3 -m pip install -r requirements.txt
python3 -m unittest -v
```

테스트의 모델·저장소는 mock을 사용합니다. 실제 Bedrock 연동은 `check_rag.py` 및 배포 후 공개 API 검증에서 별도로 확인합니다.

## AWS 배포

서울 리전 CloudShell에서 저장소를 내려받은 뒤 실행합니다. 기존 2주차 스택을 업데이트합니다.

```bash
bash deploy.sh
```

`make_corpus.py`는 과제용 문서와 manifest를 만들고, `build_index.py`는 실제 Bedrock 모델을 호출해 벡터 파일을 만듭니다. 모델 호출 비용이 발생할 수 있습니다. `make_template.py`는 `week2-base.json`에서 최신 코드와 웹 화면을 포함한 `infrastructure.json`을 생성합니다.

```bash
python3 make_corpus.py
python3 build_index.py
python3 check_rag.py
```

문서 내용을 바꾼 뒤에는 인덱스를 다시 만들고 S3로 업로드해야 합니다. 2주차 root의 manifest.json과 scholarship-01.txt는 이전 실습 자료이며 3주차는 documents/ 아래에 생성되는 파일을 사용합니다.

## 잠시 중지 및 재개

```bash
bash pause.sh
bash resume.sh
```

중지는 API 기본 엔드포인트를 비활성화하고 Lambda 동시성을 0으로 만듭니다. 재개는 동시성 2와 엔드포인트를 복원합니다. 이미 사용한 당일 질문 한도는 재개해도 초기화하지 않습니다. 저장소·로그 등은 남아 있으므로 중지가 모든 AWS 비용을 없애는 것은 아닙니다.

## 참고 문서

- https://docs.aws.amazon.com/bedrock/latest/userguide/titan-embedding-models.html
- https://docs.aws.amazon.com/nova/latest/userguide/using-converse-api.html
- https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-disable-default-endpoint.html
