# 캠퍼스 길잡이 · 대학 생활 안내 RAG 챗봇

## 2주차 구현 범위
1주차 기획의 S3 문서 저장소, API Gateway, Lambda, IAM, CloudWatch 기본 환경을 구성합니다.
가상 한빛대학교 자료만 사용합니다. 실제 대학의 규정이나 일정이 아닙니다.
이 버전은 환경 확인용 API이며 Bedrock 검색·생성 기능은 아직 연결하지 않았습니다.

## 구성
- Amazon S3: 원본·메타데이터 저장, 퍼블릭 액세스 차단, AES256 암호화, 버전 관리
- AWS Lambda: Python 3.13 / arm64 / 128MB / 제한 시간 10초
- Amazon API Gateway HTTP API: GET /health, GET /documents, GET /
- IAM: Lambda에 해당 버킷 documents/* 읽기와 자체 로그 쓰기만 허용
- CloudWatch Logs: API·Lambda 로그 30일 보관, 질문·답변 원문과 개인정보 기록 제외
- API 요청 제한: 초당 1건, 순간 2건(최선 노력 방식)

## 개발 환경
CloudShell(AWS CLI, Python, Git)과 로컬 코드 편집 환경을 사용합니다. 별도 액세스 키를 저장하지 않습니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 -m unittest test_app -v
```

## AWS 배포
로그인된 서울 리전 CloudShell에서 실행합니다.

```bash
bash deploy.sh
```

CloudFormation 스택: `campus-guide-rag-week2`
출력 `ApiUrl` 뒤에 `/health` 또는 `/documents`를 붙여 접속합니다.
`/documents` 성공 응답은 Lambda의 실제 S3 읽기까지 확인합니다.

## 다음 구현 단계
React+Amplify 화면, Bedrock Knowledge Bases, Cohere 임베딩, OpenSearch Serverless 및 Nova Lite 연결을 진행합니다.
기획서의 문서 20건은 준비 목표이며 현재는 가상 문서 1건과 메타데이터를 적재합니다.

## 자원 관리
스택 삭제 시 API·Lambda·IAM·로그는 제거되지만 S3 버킷은 자료 보호를 위해 보존됩니다.
실습용 EC2와 AWS Backup 리소스는 이 스택과 별개입니다. 중지된 EC2도 EBS 비용이 발생하며 백업은 설정한 보존 기간 동안 유지됩니다.

## 참고
- https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html
- https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-throttling.html
