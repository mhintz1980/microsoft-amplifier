def _get_serverless_guidance(self, provider: str) -> str:
    """Get serverless architecture guidance"""
    serverless_guides = {
            'aws': """
**AWS Serverless Implementation**:
```python
import json
import boto3

# Lambda function example
def lambda_handler(event, context):
    # Process event from S3, SQS, API Gateway, etc.
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Success'})
    }

# Infrastructure as CloudFormation
Resources:
  MyFunction:
    Type: AWS::Lambda::Function
    Properties:
      Handler: index.lambda_handler
      Runtime: python3.9
      Timeout: 30
      MemorySize: 256
```

**Best Practices**:
- Use environment variables for configuration
- Implement dead letter queues for error handling
- Monitor with CloudWatch metrics and logs
- Use Lambda Layers for shared code
""",
            'azure': """
**Azure Serverless Implementation**:
```python
import json
import logging

import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    return func.HttpResponse(f"Hello {name}")

# ARM Template deployment
{
  "type": "Microsoft.Web/sites",
  "apiVersion": "2021-03-01",
  "name": "[parameters('functionAppName')]",
  "kind": "functionapp"
}
```

**Best Practices**:
- Use Application Insights for monitoring
- Implement retry policies for external calls
- Use managed identities for authentication
- Leverage consumption plan for cost efficiency
""",
            'gcp': """
**GCP Serverless Implementation**:
```python
import functions_framework

@functions_framework.http
def hello_http(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
    """
    request_json = request.get_json(silent=True)
    request_args = request.args

    if request_json and 'name' in request_json:
        name = request_json['name']
    elif request_args and 'name' in request_args:
        name = request_args['name']
    else:
        name = 'World'

    return f'Hello {name}!'

# Deployment with gcloud
gcloud functions deploy hello_http \
  --runtime python39 \
  --trigger-http \
  --allow-unauthenticated
```

**Best Practices**:
- Use Cloud Logging for centralized logs
- Implement circuit breakers for external services
- Use Cloud Secrets Manager for sensitive data
- Configure proper timeout and memory limits
"""
    }
    return serverless_guides.get(provider, serverless_guides['aws'])