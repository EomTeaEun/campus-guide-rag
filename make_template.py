import json
from pathlib import Path
root=Path(__file__).parent
t=json.loads((root/'week2-base.json').read_text());r=t['Resources']
t['Description']='Campus Guide week3 RAG MVP - Titan vectors, Nova answers, same-origin web UI, daily usage cap'
r['QuotaTable']={'Type':'AWS::DynamoDB::Table','Properties':{'BillingMode':'PAY_PER_REQUEST','AttributeDefinitions':[{'AttributeName':'day','AttributeType':'S'}],'KeySchema':[{'AttributeName':'day','KeyType':'HASH'}],'TimeToLiveSpecification':{'AttributeName':'expires_at','Enabled':True}}}
role=r['ExecutionRole']['Properties']['Policies'][0]['PolicyDocument']['Statement']
role.extend([{'Effect':'Allow','Action':'bedrock:InvokeModel','Resource':[{'Fn::Sub':'arn:${AWS::Partition}:bedrock:${AWS::Region}::foundation-model/amazon.titan-embed-text-v2:0'},{'Fn::Sub':'arn:${AWS::Partition}:bedrock:${AWS::Region}:${AWS::AccountId}:inference-profile/apac.amazon.nova-lite-v1:0'},{'Fn::Sub':'arn:${AWS::Partition}:bedrock:ap-*::foundation-model/amazon.nova-lite-v1:0'}]}, {'Effect':'Allow','Action':'dynamodb:UpdateItem','Resource':{'Fn::GetAtt':['QuotaTable','Arn']}}])
f=r['ApiFunction']['Properties'];f['MemorySize']=256;f['Timeout']=28;f['ReservedConcurrentExecutions']=2
f['Environment']['Variables'].update({'QUOTA_TABLE':{'Ref':'QuotaTable'},'DAILY_LIMIT':'50','CHAT_MODEL':'apac.amazon.nova-lite-v1:0'})
f['Code']['ZipFile']=(root/'app.py').read_text()+'\nWEB_HTML = '+repr((root/'index.html').read_text())+'\n'
r['Integration']['Properties']['TimeoutInMillis']=29000
r['HttpApi']['Properties']['DisableExecuteApiEndpoint']=False
r['HttpApi']['Properties']['Description']='Fictional campus RAG demo, daily global limit 50 questions'
for key,path,method in [('ChatRoute','/chat','POST'),('SourceRoute','/source','GET')]:
 r[key]={'Type':'AWS::ApiGatewayV2::Route','Properties':{'ApiId':{'Ref':'HttpApi'},'RouteKey':method+' '+path,'Target':{'Fn::Join':['/',['integrations',{'Ref':'Integration'}]]}}}
r['PostInvokePermission']={'Type':'AWS::Lambda::Permission','Properties':{'FunctionName':{'Ref':'ApiFunction'},'Action':'lambda:InvokeFunction','Principal':'apigateway.amazonaws.com','SourceAccount':{'Ref':'AWS::AccountId'},'SourceArn':{'Fn::Sub':'arn:${AWS::Partition}:execute-api:${AWS::Region}:${AWS::AccountId}:${HttpApi}/*/POST/chat'}}}
r['Stage']['Properties']['DefaultRouteSettings'].update({'ThrottlingRateLimit':2,'ThrottlingBurstLimit':4})
(root/'infrastructure.json').write_text(json.dumps(t,ensure_ascii=False,indent=2))
