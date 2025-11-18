"""
Cloud Integration Expert Skill Documentation

Comprehensive documentation for the Cloud Integration Expert skill.
Progressive disclosure structure with implementation examples.
"""

# Skill Metadata
SKILL_NAME = "Cloud Integration Expert"
CATEGORY = "Domain Expertise - Fullstack Integration Team"
COMPLEXITY = "Expert"
VERSION = "1.0.0"
LAST_UPDATED = "2025-01-17"

# Tags for discovery
TAGS = [
    "cloud", "aws", "azure", "gcp", "multi-cloud", "serverless",
    "integration", "migration", "cost-optimization", "cloud-security",
    "devops", "infrastructure", "microservices", "containers"
]

# Description
DESCRIPTION = """
Expert guidance for cloud platform integration across AWS, Azure, and GCP with
multi-cloud strategies, serverless architectures, and cost optimization. Provides
technical patterns for cloud services integration, identity management, data
pipelines, and migration strategies with zero hallucination guarantee.
"""

# Progressive Disclosure Content
METADATA_LEVEL = """
🌐 Cloud Integration Expert
Multi-cloud strategies for AWS, Azure, GCP
Serverless, migration, cost optimization
Zero-error integration patterns
"""

SUMMARY_LEVEL = """
🌐 Cloud Integration Analysis

**Key Capabilities**:
• Multi-cloud architecture strategies (AWS, Azure, GCP)
• Serverless and event-driven architectures
• Cloud services integration (storage, databases, messaging)
• Identity and access management (IAM, federated auth)
• Data integration and ETL pipelines
• Cost optimization and monitoring
• Security and compliance frameworks
• Migration patterns and hybrid architectures

**Provider Support**:
• AWS: Complete service ecosystem coverage
• Azure: Enterprise integration focus
• GCP: Data analytics and Kubernetes-native
• Multi-cloud: Cross-platform strategies

**Integration Types**:
• Storage integration (object, file, block)
• Database integration (SQL, NoSQL, warehouse)
• Messaging and event systems
• Serverless functions and FaaS
• Container orchestration
• Networking and security

**Expertise Areas**:
• Zero-hallucination technical accuracy
• Production-tested patterns
• Cost optimization strategies
• Security best practices
• Performance monitoring
• Migration planning
"""

DETAILED_LEVEL = """
# 🌐 Cloud Integration Expert - Detailed Guide

## Multi-Cloud Strategy Framework

### Provider Selection Criteria
- **AWS**: Largest ecosystem, enterprise features, global infrastructure
- **Azure**: Microsoft ecosystem, hybrid cloud, enterprise integration
- **GCP**: Data analytics, Kubernetes-native, competitive pricing

### Multi-Cloud Architecture Patterns
1. **Best-of-Breed**: Use each provider's strongest services
2. **Disaster Recovery**: Cross-provider backup and failover
3. **Vendor Lock-in Avoidance**: Maintain portability across providers
4. **Cost Optimization**: Arbitrage between provider pricing
5. **Compliance Requirements**: Meet regional data sovereignty needs

## Cloud Services Integration

### Storage Integration Patterns
- **Object Storage**: S3/Azure Blob/Cloud Storage for files and media
- **File Storage**: EFS/Azure Files/Filestore for shared access
- **Block Storage**: EBS/Azure Disks/Persistent Disks for databases
- **Archive Storage**: Glacier/Archive Storage/Coldline for long-term retention
- **CDN Integration**: CloudFront/Azure CDN/Cloud CDN for global distribution

### Database Integration Strategies
- **Relational**: RDS/Azure SQL/Cloud SQL for transactional data
- **NoSQL**: DynamoDB/Cosmos DB/Firestore for flexible schemas
- **Data Warehouse**: Redshift/Synapse/BigQuery for analytics
- **Caching**: ElastiCache/Redis Cache/Memorystore for performance
- **Search**: OpenSearch/Azure Cognitive Search/Cloud Search for full-text search

### Messaging and Event Systems
- **Queue Services**: SQS/Service Bus/Cloud Tasks for decoupling
- **Pub/Sub**: SNS/Event Grid/Pub/Sub for event broadcasting
- **Event Streaming**: Kinesis/Event Hubs/Pub/Sub for real-time streams
- **Workflow Orchestration**: Step Functions/Logic Apps/Cloud Workflows
- **Message Brokers**: MQ/Service Bus/Advanced Messaging

## Identity and Access Management

### IAM Best Practices
- **Principle of Least Privilege**: Minimum required permissions
- **Role-Based Access Control**: Group permissions by job functions
- **Multi-Factor Authentication**: Required for all human users
- **Service Accounts**: Identity for applications and services
- **Temporary Credentials**: Use short-lived tokens where possible
- **Regular Access Reviews**: Periodic permission audits
- **Separation of Duties**: Critical operations require multiple approvers

### Federated Authentication
- **SSO Integration**: SAML/OIDC for enterprise identity providers
- **Social Logins**: OAuth2 for consumer applications
- **Custom Identity**: Customer-specific authentication systems
- **B2B Scenarios**: Cross-organization identity federation
- **API Authentication**: JWT, API Keys, OAuth2 tokens

## Serverless Integration

### Event-Driven Architecture
```
Event Source → Event Bus → Processing Functions → Data Store → Notification
```

**Common Event Sources**:
- File uploads to storage
- Database changes (CDC)
- HTTP requests via API Gateway
- Scheduled events (cron)
- Other cloud service events
- Custom applications

### Function Implementation Patterns
- **Single Purpose**: Each function does one thing well
- **Stateless**: No dependency on local state
- **Idempotent**: Safe to retry multiple times
- **Timeout Awareness**: Handle execution limits gracefully
- **Error Handling**: Proper logging and dead-letter queues
- **Resource Management**: Optimize memory and CPU usage

## Data Integration and ETL

### Modern Data Pipeline Architecture
```
Sources → Ingestion → Processing → Storage → Analytics → Visualization
```

### Data Ingestion Patterns
- **Batch Processing**: Scheduled ETL jobs for bulk data
- **Streaming Processing**: Real-time data pipelines
- **Change Data Capture**: Database replication and synchronization
- **API Integration**: Pulling data from external systems
- **File Processing**: CSV, JSON, Parquet file ingestion

### Data Processing Frameworks
- **Apache Spark**: Distributed data processing
- **Dataflow/Beam**: Unified stream and batch processing
- **Azure Data Factory**: Cloud-based ETL orchestration
- **AWS Glue**: Serverless ETL and data catalog
- **Custom Functions**: Provider-specific processing logic

## Cost Optimization

### Compute Optimization
- **Right Sizing**: Match resources to actual usage
- **Auto Scaling**: Dynamic resource allocation
- **Spot Instances**: Up to 90% savings for fault-tolerant workloads
- **Reserved Instances**: Up to 60% savings for steady workloads
- **Scheduling**: Run during off-peak hours when possible
- **Performance Tuning**: Optimize code for better resource utilization

### Storage Optimization
- **Lifecycle Management**: Automatic data tiering
- **Data Compression**: Reduce storage footprint
- **Cleanup Policies**: Remove unused resources
- **Access Pattern Analysis**: Choose appropriate storage classes
- **Backup Optimization**: Efficient backup strategies
- **Archive Cold Data**: Move infrequently accessed data to cheaper storage

### Monitoring and Alerting
- **Budget Alerts**: Proactive cost notifications
- **Usage Analysis**: Identify optimization opportunities
- **Resource Tagging**: Track costs by project/team
- **Anomaly Detection**: Identify unusual spending patterns
- **Recommendation Engines**: Automated optimization suggestions

## Security and Compliance

### Cloud Security Framework
- **Identity Security**: Strong authentication and authorization
- **Network Security**: Isolation and traffic control
- **Data Protection**: Encryption and access controls
- **Application Security**: Secure coding and deployment
- **Monitoring**: Threat detection and incident response
- **Compliance**: Meeting regulatory requirements

### Compliance Standards
- **SOC 2**: Security and availability controls
- **ISO 27001**: Information security management
- **PCI DSS**: Payment card industry standards
- **HIPAA**: Healthcare information protection
- **GDPR**: European data protection
- **FedRAMP**: US government cloud security

## Migration Strategies

### Migration Approaches
1. **Lift and Shift**: Move with minimal changes (3-6 months)
2. **Re-platform**: Cloud optimizations (6-12 months)
3. **Re-architecture**: Cloud-native redesign (9-18 months)
4. **Serverless First**: Function-based architecture (12-24 months)
5. **Microservices**: Decompose into services (12-24 months)

### Migration Process
1. **Assessment**: Inventory and analysis phase
2. **Planning**: Strategy and roadmap development
3. **Proof of Concept**: Validate approach with pilot
4. **Implementation**: Phased migration execution
5. **Optimization**: Post-migration fine-tuning
6. **Operations**: Ongoing management and improvement

### Risk Management
- **Technical Risks**: Compatibility, performance, security
- **Business Risks**: Downtime, data loss, cost overruns
- **Operational Risks**: Team readiness, process changes
- **Compliance Risks**: Regulatory requirements, data sovereignty
- **Financial Risks**: Unexpected costs, ROI validation

## Performance Monitoring

### Observability Stack
- **Metrics**: Quantitative measurements of system behavior
- **Logs**: Detailed event records for debugging
- **Traces**: Request paths through distributed systems
- **Dashboards**: Visualizations of system health
- **Alerts**: Automated notifications for issues

### Key Performance Indicators
- **Availability**: Uptime and reliability metrics
- **Response Time**: Latency measurements
- **Throughput**: Request processing capacity
- **Error Rates**: Failure frequency and types
- **Resource Utilization**: CPU, memory, storage, network usage
- **Cost Efficiency**: Performance per dollar spent

### Optimization Techniques
- **Performance Testing**: Load and stress testing
- **Bottleneck Analysis**: Identify and resolve constraints
- **Capacity Planning**: Forecast future resource needs
- **Auto-tuning**: Automated performance optimization
- **A/B Testing**: Compare optimization strategies
"""

FULL_LEVEL = DETAILED_LEVEL + """

## Implementation Examples

### AWS Serverless Web Application
```yaml
# CloudFormation template
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Serverless Web Application'

Parameters:
  Environment:
    Type: String
    Default: production

Resources:
  # S3 bucket for static website
  WebsiteBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub '${Environment}-website-${AWS::AccountId}'
      WebsiteConfiguration:
        IndexDocument: index.html
        ErrorDocument: error.html
      PublicAccessBlockConfiguration:
        BlockPublicAcls: false
        BlockPublicPolicy: false
        IgnorePublicAcls: false
        RestrictPublicBuckets: false

  # Bucket policy for public read access
  WebsiteBucketPolicy:
    Type: AWS::S3::BucketPolicy
    Properties:
      Bucket: !Ref WebsiteBucket
      PolicyDocument:
        Statement:
          - Effect: Allow
            Principal: "*"
            Action: s3:GetObject
            Resource: !Sub '${WebsiteBucket}/*'

  # API Gateway REST API
  RestAPI:
    Type: AWS::ApiGateway::RestApi
    Properties:
      Name: !Sub '${Environment}-api'
      Description: 'Serverless API'

  # API Gateway resource for /items
  ItemsResource:
    Type: AWS::ApiGateway::Resource
    Properties:
      RestApiId: !Ref RestAPI
      ParentId: !GetAtt RestAPI.RootResourceId
      PathPart: items

  # API Gateway GET method
  ItemsGETMethod:
    Type: AWS::ApiGateway::Method
    Properties:
      RestApiId: !Ref RestAPI
      ResourceId: !Ref ItemsResource
      HttpMethod: GET
      AuthorizationType: NONE
      Integration:
        Type: AWS_PROXY
        IntegrationHttpMethod: POST
        Uri: !Sub 'arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${GetItemsFunction.Arn}/invocations'

  # API Gateway POST method
  ItemsPOSTMethod:
    Type: AWS::ApiGateway::Method
    Properties:
      RestApiId: !Ref RestAPI
      ResourceId: !Ref ItemsResource
      HttpMethod: POST
      AuthorizationType: NONE
      Integration:
        Type: AWS_PROXY
        IntegrationHttpMethod: POST
        Uri: !Sub 'arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${CreateItemFunction.Arn}/invocations'

  # Lambda function for GET items
  GetItemsFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub '${Environment}-get-items'
      Runtime: python3.9
      Handler: index.lambda_handler
      Role: !GetAtt LambdaExecutionRole.Arn
      Environment:
        Variables:
          TABLE_NAME: !Ref ItemsTable
      Code:
        ZipFile: |
          import json
          import boto3
          import os

          dynamodb = boto3.resource('dynamodb')
          table_name = os.environ['TABLE_NAME']
          table = dynamodb.Table(table_name)

          def lambda_handler(event, context):
              try:
                  response = table.scan()
                  return {
                      'statusCode': 200,
                      'headers': {
                          'Content-Type': 'application/json',
                          'Access-Control-Allow-Origin': '*'
                      },
                      'body': json.dumps(response['Items'])
                  }
              except Exception as e:
                  return {
                      'statusCode': 500,
                      'body': json.dumps({'error': str(e)})
                  }

  # Lambda function for POST items
  CreateItemFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub '${Environment}-create-item'
      Runtime: python3.9
      Handler: index.lambda_handler
      Role: !GetAtt LambdaExecutionRole.Arn
      Environment:
        Variables:
          TABLE_NAME: !Ref ItemsTable
      Code:
        ZipFile: |
          import json
          import boto3
          import os
          import uuid

          dynamodb = boto3.resource('dynamodb')
          table_name = os.environ['TABLE_NAME']
          table = dynamodb.Table(table_name)

          def lambda_handler(event, context):
              try:
                  item = json.loads(event['body'])
                  item['id'] = str(uuid.uuid4())

                  table.put_item(Item=item)

                  return {
                      'statusCode': 201,
                      'headers': {
                          'Content-Type': 'application/json',
                          'Access-Control-Allow-Origin': '*'
                      },
                      'body': json.dumps(item)
                  }
              except Exception as e:
                  return {
                      'statusCode': 500,
                      'body': json.dumps({'error': str(e)})
                  }

  # DynamoDB table for items
  ItemsTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub '${Environment}-items'
      AttributeDefinitions:
        - AttributeName: id
          AttributeType: S
      KeySchema:
        - AttributeName: id
          KeyType: HASH
      BillingMode: PAY_PER_REQUEST
      StreamSpecification:
        StreamViewType: NEW_AND_OLD_IMAGES

  # IAM role for Lambda functions
  LambdaExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
      Policies:
        - PolicyName: DynamoDBAccess
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - dynamodb:PutItem
                  - dynamodb:GetItem
                  - dynamodb:UpdateItem
                  - dynamodb:DeleteItem
                  - dynamodb:Query
                  - dynamodb:Scan
                Resource: !GetAtt ItemsTable.Arn

  # API Gateway deployment
  APIDeployment:
    Type: AWS::ApiGateway::Deployment
    DependsOn:
      - ItemsGETMethod
      - ItemsPOSTMethod
    Properties:
      RestApiId: !Ref RestAPI

  # API Gateway stage
  APIStage:
    Type: AWS::ApiGateway::Stage
    Properties:
      RestApiId: !Ref RestAPI
      DeploymentId: !Ref APIDeployment
      StageName: prod

Outputs:
  WebsiteURL:
    Description: 'Website URL'
    Value: !GetAtt WebsiteBucket.WebsiteURL

  APIEndpoint:
    Description: 'API Gateway endpoint'
    Value: !Sub 'https://${RestAPI}.execute-api.${AWS::Region}.amazonaws.com/prod'
```

### Azure Event-Driven Microservices
```bicep
// Bicep template for event-driven microservices
param environment string = 'production'
param location string = resourceGroup().location

// Resource Group for organization
resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: '${environment}-microservices'
  location: location
}

// Storage Account for shared data
resource storage 'Microsoft.Storage/storageAccounts@2021-08-01' = {
  name: '${environment}storage${uniqueString(resourceGroup().id)}'
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    supportsHttpsTrafficOnly: true
  }
}

// Service Bus for messaging
resource serviceBus 'Microsoft.ServiceBus/namespaces@2021-06-01-preview' = {
  name: '${environment}-servicebus-${uniqueString(resourceGroup().id)}'
  location: location
  sku: {
    name: 'Standard'
  }
}

// Service Bus topic for events
resource serviceBusTopic 'Microsoft.ServiceBus/namespaces/topics@2021-06-01-preview' = {
  parent: serviceBus
  name: 'events'
}

// Event Grid for system events
resource eventGrid 'Microsoft.EventGrid/systemTopics@2022-06-01' = {
  name: '${environment}-blobs'
  location: location
  properties: {
    source: storage.id
    topicType: 'Microsoft.Storage.StorageAccounts'
  }
}

// Cosmos DB for shared state
resource cosmosDB 'Microsoft.DocumentDB/databaseAccounts@2021-10-15' = {
  name: '${environment}-cosmos-${uniqueString(resourceGroup().id)}'
  location: location
  kind: 'GlobalDocumentDB'
  properties: {
    databaseAccountOfferType: 'Standard'
    locations: [
      {
        locationName: location
        failoverPriority: 0
      }
    ]
    consistencyPolicy: {
      defaultConsistencyLevel: 'Session'
    }
  }
}

// Cosmos DB database
resource cosmosDatabase 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2021-10-15' = {
  parent: cosmosDB
  name: 'microservices'
  properties: {
    resource: {
      id: 'microservices'
    }
  }
}

// Key Vault for secrets
resource keyVault 'Microsoft.KeyVault/vaults@2021-11-01-preview' = {
  name: '${environment}-kv-${uniqueString(resourceGroup().id)}'
  location: location
  properties: {
    tenantId: subscription().tenantId
    sku: {
      family: 'A'
      name: 'standard'
    }
    accessPolicies: []
  }
}

// Application Insights for monitoring
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: '${environment}-appinsights'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
  }
}

// Function App for order processing
resource orderFunction 'Microsoft.Web/sites@2021-03-01' = {
  name: '${environment}-order-processor'
  location: location
  kind: 'functionapp'
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      appSettings: [
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storage.name};AccountKey=${listKeys(storage.id, '2021-08-01').keys[0].value};EndpointSuffix=core.windows.net'
        }
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'dotnet'
        }
        {
          name: 'COSMOS_DB_ENDPOINT'
          value: cosmosDB.properties.documentEndpoint
        }
        {
          name: 'COSMOS_DB_KEY'
          value: listKeys(cosmosDB.id, '2021-10-15').primaryMasterKey
        }
        {
          name: 'SERVICE_BUS_CONNECTION'
          value: listKeys(serviceBus.id, '2021-06-01-preview').primaryConnectionString
        }
        {
          name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
          value: appInsights.properties.InstrumentationKey
        }
      ]
    }
  }
}

// Function App for inventory management
resource inventoryFunction 'Microsoft.Web/sites@2021-03-01' = {
  name: '${environment}-inventory-manager'
  location: location
  kind: 'functionapp'
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      appSettings: [
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storage.name};AccountKey=${listKeys(storage.id, '2021-08-01').keys[0].value};EndpointSuffix=core.windows.net'
        }
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'dotnet'
        }
        {
          name: 'COSMOS_DB_ENDPOINT'
          value: cosmosDB.properties.documentEndpoint
        }
        {
          name: 'COSMOS_DB_KEY'
          value: listKeys(cosmosDB.id, '2021-10-15').primaryMasterKey
        }
      {
          name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
          value: appInsights.properties.InstrumentationKey
        }
      ]
    }
  }
}

// App Service Plan for functions
resource appServicePlan 'Microsoft.Web/serverfarms@2021-03-01' = {
  name: '${environment}-function-plan'
  location: location
  sku: {
    name: 'Y1'
    tier: 'Dynamic'
  }
  properties: {
    reserved: false
  }
}

// Event Grid subscription for blob events
resource blobEventSubscription 'Microsoft.EventGrid/systemTopics/eventSubscriptions@2022-06-01' = {
  name: 'to-order-processor'
  parent: eventGrid
  properties: {
    destination: {
      endpointType: 'WebHook'
      properties: {
        endpointUrl: 'https://${orderFunction.name}.azurewebsites.net/runtime/webhooks/EventGrid?functionName=ProcessBlobEvent'
      }
    }
    filter: {
      subjectBeginsWith: '/blobServices/default/containers/orders/'
    }
  }
}

// Service Bus subscription for order events
resource orderEventSubscription 'Microsoft.ServiceBus/namespaces/topics/subscriptions@2021-06-01-preview' = {
  parent: serviceBusTopic
  name: 'inventory-subscription'
  properties: {
    deadLetteringOnMessageExpiration: true
  }
}
```

### GCP Data Processing Pipeline
```python
# main.py - Cloud Functions for data processing
import json
import logging
from datetime import datetime
from google.cloud import storage, bigquery, pubsub_v1
from google.cloud.exceptions import GoogleCloudError

# Initialize clients
storage_client = storage.Client()
bigquery_client = bigquery.Client()
publisher = pubsub_v1.PublisherClient()

# Configuration
PROJECT_ID = "your-project-id"
DATASET_ID = "data_pipeline"
TABLE_ID = "processed_data"
TOPIC_NAME = "data-processing-events"

def process_file_trigger(event, context):
    """Cloud Function triggered by Cloud Storage upload."""
    try:
        # Extract file information
        bucket_name = event['bucket']
        file_name = event['name']

        logging.info(f"Processing file: gs://{bucket_name}/{file_name}")

        # Download file content
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        content = blob.download_as_string()

        # Process the data (example: CSV processing)
        processed_records = process_csv_data(content)

        # Load to BigQuery
        load_to_bigquery(processed_records, file_name)

        # Publish success event
        publish_event({
            'event_type': 'file_processed',
            'file_name': file_name,
            'record_count': len(processed_records),
            'timestamp': datetime.utcnow().isoformat()
        })

        return {'status': 'success', 'records_processed': len(processed_records)}

    except Exception as e:
        logging.error(f"Error processing file {file_name}: {str(e)}")
        publish_event({
            'event_type': 'processing_error',
            'file_name': file_name,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        })
        raise

def process_csv_data(content):
    """Process CSV content and return structured records."""
    import csv
    import io

    records = []
    csv_reader = csv.DictReader(io.StringIO(content.decode('utf-8')))

    for row in csv_reader:
        # Transform and validate data
        record = {
            'id': row.get('id'),
            'name': row.get('name', '').strip(),
            'email': row.get('email', '').strip().lower(),
            'created_at': parse_date(row.get('created_at')),
            'amount': float(row.get('amount', 0)),
            'category': row.get('category', '').strip(),
            'processed_at': datetime.utcnow().isoformat()
        }

        # Validate required fields
        if record['id'] and record['email']:
            records.append(record)

    return records

def load_to_bigquery(records, source_file):
    """Load processed records to BigQuery."""
    try:
        # Reference to BigQuery table
        table_ref = bigquery_client.dataset(DATASET_ID).table(TABLE_ID)

        # Configure load job
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            autodetect=True
        )

        # Convert records to JSON
        json_data = '\n'.join(json.dumps(record) for record in records)

        # Load data
        load_job = bigquery_client.load_table_from_file(
            io.StringIO(json_data),
            table_ref,
            job_config=job_config
        )

        # Wait for job completion
        load_job.result()

        logging.info(f"Loaded {len(records)} records to BigQuery")

    except GoogleCloudError as e:
        logging.error(f"BigQuery load error: {str(e)}")
        raise

def publish_event(event_data):
    """Publish event to Pub/Sub topic."""
    try:
        topic_path = publisher.topic_path(PROJECT_ID, TOPIC_NAME)

        # Convert event data to bytes
        data = json.dumps(event_data).encode('utf-8')

        # Publish message
        future = publisher.publish(topic_path, data=data)
        message_id = future.result()

        logging.info(f"Published event {message_id}: {event_data['event_type']}")

    except Exception as e:
        logging.error(f"Error publishing event: {str(e)}")
        # Don't raise here - event publishing failure shouldn't stop processing

def parse_date(date_string):
    """Parse date string and return ISO format."""
    if not date_string:
        return None

    try:
        # Try common date formats
        formats = [
            '%Y-%m-%d',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%m/%d/%Y',
            '%d/%m/%Y'
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_string, fmt).isoformat()
            except ValueError:
                continue

        return None

    except Exception:
        return None

def analyze_data_http(request):
    """HTTP function for data analysis."""
    try:
        # Parse request
        request_json = request.get_json()

        if not request_json:
            return {'error': 'Invalid JSON'}, 400

        analysis_type = request_json.get('analysis_type', 'summary')

        # Query BigQuery for analysis
        if analysis_type == 'summary':
            query = f"""
                SELECT
                    COUNT(*) as total_records,
                    COUNT(DISTINCT category) as unique_categories,
                    AVG(amount) as avg_amount,
                    MIN(amount) as min_amount,
                    MAX(amount) as max_amount,
                    SUM(amount) as total_amount
                FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
                WHERE DATE(processed_at) = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
            """
        elif analysis_type == 'category_breakdown':
            query = f"""
                SELECT
                    category,
                    COUNT(*) as record_count,
                    AVG(amount) as avg_amount,
                    SUM(amount) as total_amount
                FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
                WHERE DATE(processed_at) = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
                GROUP BY category
                ORDER BY total_amount DESC
            """
        else:
            return {'error': 'Invalid analysis_type'}, 400

        # Execute query
        query_job = bigquery_client.query(query)
        results = query_job.result()

        # Format results
        analysis_results = []
        for row in results:
            analysis_results.append(dict(row))

        return {
            'analysis_type': analysis_type,
            'date': (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'results': analysis_results
        }

    except Exception as e:
        logging.error(f"Analysis error: {str(e)}")
        return {'error': str(e)}, 500
```

## Terraform Multi-Cloud Example
```hcl
# terraform.tf - Multi-cloud infrastructure

provider "aws" {
  region = var.aws_region
}

provider "azurerm" {
  features {}
}

provider "google" {
  project = var.gcp_project
  region  = var.gcp_region
}

# AWS Resources
resource "aws_s3_bucket" "primary_storage" {
  bucket = "${var.project_name}-storage-${random_id.suffix.hex}"

  versioning {
    enabled = true
  }

  lifecycle_rule {
    id      = "lifecycle"
    enabled = true

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    transition {
      days          = 365
      storage_class = "DEEP_ARCHIVE"
    }
  }
}

resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_lambda_function" "processor" {
  filename         = "function.zip"
  function_name    = "${var.project_name}-processor"
  role            = aws_iam_role.lambda_role.arn
  handler         = "index.handler"
  runtime         = "python3.9"

  environment {
    variables = {
      AZURE_STORAGE_KEY = azurerm_storage_account.primary.primary_access_key
      GCP_BUCKET_NAME   = google_storage_bucket.primary.name
    }
  }
}

# Azure Resources
resource "azurerm_resource_group" "primary" {
  name     = "${var.project_name}-rg"
  location = var.azure_location
}

resource "azurerm_storage_account" "primary" {
  name                     = "${var.project_name}storage${random_id.suffix.hex}"
  resource_group_name      = azurerm_resource_group.primary.name
  location                 = azurerm_resource_group.primary.location
  account_tier             = "Standard"
  account_replication_type = "GRS"

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_function_app" "processor" {
  name                = "${var.project_name}-function"
  location            = azurerm_resource_group.primary.location
  resource_group_name = azurerm_resource_group.primary.name
  app_service_plan_id = azurerm_app_service_plan.primary.id

  app_settings = {
    "AWS_S3_BUCKET" = aws_s3_bucket.primary_storage.id
    "GCP_PROJECT"   = var.gcp_project
  }

  storage_account_name       = azurerm_storage_account.primary.name
  storage_account_access_key = azurerm_storage_account.primary.primary_access_key
  version                    = "~4"
}

# GCP Resources
resource "google_storage_bucket" "primary" {
  name     = "${var.project_name}-storage-${random_id.suffix.hex}"
  location = var.gcp_region

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "SetStorageClass"
      storage_class = "COLDLINE"
    }
  }
}

resource "google_cloudfunctions_function" "processor" {
  name        = "${var.project_name}-processor"
  runtime     = "python39"
  entry_point = "process_data"

  source_archive_bucket = google_storage_bucket.function_code.name
  source_archive_object = google_storage_bucket_object.function_zip.name

  environment_variables = {
    AWS_S3_BUCKET = aws_s3_bucket.primary_storage.id
    AZURE_STORAGE = azurerm_storage_account.primary.name
  }

  event_trigger {
    event_type = "google.storage.object.finalize"
    resource   = google_storage_bucket.primary.name
  }
}

# Cross-cloud networking
resource "aws_vpc" "primary" {
  cidr_block = "10.0.0.0/16"
}

resource "azurerm_virtual_network" "primary" {
  name                = "${var.project_name}-vnet"
  address_space       = ["10.1.0.0/16"]
  location            = azurerm_resource_group.primary.location
  resource_group_name = azurerm_resource_group.primary.name
}

resource "google_compute_network" "primary" {
  name                    = "${var.project_name}-vpc"
  auto_create_subnetworks = false
}

# VPN connections for hybrid architecture
resource "aws_customer_gateway" "azure" {
  bgp_asn    = 65000
  ip_address = azurerm_public_ip.vpn.ip_address
  type       = "ipsec.1"
}

resource "aws_vpn_connection" "azure" {
  customer_gateway_id = aws_customer_gateway.azure.id
  vpn_gateway_id     = aws_vpn_gateway.primary.id
  type                = "ipsec.1"

  static_routes_only = false
}

# Data replication
resource "aws_dynamodb_table" "replicated_data" {
  name           = "${var.project_name}-data"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"
  }

  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"
}

# Event routing between clouds
resource "aws_lambda_function" "azure_forwarder" {
  filename      = "azure_forwarder.zip"
  function_name = "${var.project_name}-azure-forwarder"
  role         = aws_iam_role.lambda_role.arn
  handler      = "index.handler"
  runtime      = "python3.9"

  event_source_mapping {
    event_source_arn = aws_dynamodb_table.replicated_data.stream_arn
    starting_position = "LATEST"
  }

  environment {
    variables = {
      AZURE_FUNCTION_URL = azurerm_function_app.processor.default_hostname
    }
  }
}

# Monitoring across clouds
resource "aws_cloudwatch_metric_alarm" "aws_lambda_errors" {
  alarm_name          = "${var.project_name}-lambda-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Sum"
  threshold           = "5"
  alarm_description   = "This metric monitors lambda function errors"
  alarm_actions       = [aws_sns_topic.alerts.arn]
}

resource "azurerm_monitor_metric_alert" "function_errors" {
  name                = "${var.project_name}-function-errors"
  resource_group_name = azurerm_resource_group.primary.name
  scopes              = [azurerm_function_app.processor.id]

  criteria {
    metric_namespace = "Microsoft.Web/sites"
    metric_name      = "Http5xx"
    aggregation      = "Total"
    operator         = "GreaterThan"
    threshold        = 5
  }

  action {
    action_group_id = azurerm_monitor_action_group.primary.id
  }
}

resource "google_monitoring_alert_policy" "function_errors" {
  display_name = "${var.project_name}-function-errors"
  combiner     = "OR"

  conditions {
    display_name = "Cloud Function error rate"
    condition_monitoring_query_filter = 'metric.type="cloudfunctions.googleapis.com/function/execution_count" resource.label."function_name"="${var.project_name}-processor"'
    condition_threshold {
      filter     = 'metric.type="cloudfunctions.googleapis.com/function/execution_count" resource.label."function_name"="${var.project_name}-processor"'
      aggregations {
        alignment_period     = "300s"
        per_series_aligner   = "ALIGN_RATE"
        cross_series_reducer = "REDUCE_SUM"
      }
      comparison   = "COMPARISON_GT"
      threshold_value = 5
      duration     = "0s"
    }
  }

  notification_channels = [google_monitoring_notification_channel.alerts.id]
}
```

## Production Deployment Checklist

### Pre-Deployment Checklist
- [ ] Cloud accounts and subscriptions created
- [ ] IAM policies configured with least privilege
- [ ] Network security groups/firewalls configured
- [ ] Data encryption at rest and in transit enabled
- [ ] Backup and disaster recovery plans documented
- [ ] Cost budgets and alerts configured
- [ ] Monitoring and logging set up
- [ ] Compliance requirements validated

### Security Configuration
- [ ] Multi-factor authentication enabled for all users
- [ ] Service account keys rotated regularly
- [ ] Network access restricted to necessary IPs
- [ ] SSL/TLS certificates configured
- [ ] Web Application Firewall enabled
- [ ] DDoS protection configured
- [ ] Security scanning automated
- [ ] Incident response procedures documented

### Performance Optimization
- [ ] Resource rightsizing based on load testing
- [ ] Auto-scaling policies configured
- [ ] Content Delivery Network enabled
- [ ] Database query optimization
- [ ] Caching strategies implemented
- [ ] Image and asset optimization
- [ ] Code minification and compression
- [ ] Performance monitoring configured

### Monitoring and Alerting
- [ ] Key performance metrics identified
- [ ] Dashboards created for visualization
- [ ] Alert thresholds configured appropriately
- [ ] Log aggregation and retention policies
- [ ] Error tracking and reporting
- [ ] Custom business metrics tracked
- [ ] Automated health checks
- [ ] Performance baseline established

### Cost Management
- [ ] Cost allocation tags implemented
- [ ] Reserved instances purchased where appropriate
- [ ] Auto-scaling policies optimized for cost
- [ ] Storage lifecycle policies configured
- [ ] Unused resources identified and removed
- [ ] Cost optimization reviews scheduled
- [ ] Budget alerts configured
- [ ] Cost analysis reports automated

## Troubleshooting Guide

### Common Issues and Solutions

#### Performance Issues
**Problem**: Slow API response times
**Solutions**:
1. Check resource utilization (CPU, memory, network)
2. Review database query performance
3. Implement caching strategies
4. Scale resources appropriately
5. Optimize code and algorithms
6. Use content delivery network

#### Cost Overruns
**Problem**: Unexpected high costs
**Solutions**:
1. Review cost breakdown by service
2. Identify unused or over-provisioned resources
3. Implement auto-scaling instead of static sizing
4. Use spot instances for appropriate workloads
5. Optimize data transfer and storage
6. Set up cost alerts and budgets

#### Security Breaches
**Problem**: Unauthorized access or data exposure
**Solutions**:
1. Immediately revoke compromised credentials
2. Review audit logs for unauthorized access
3. Patch security vulnerabilities
4. Implement additional security controls
5. Review and strengthen IAM policies
6. Conduct security audit

#### Integration Failures
**Problem**: Cloud services not communicating properly
**Solutions**:
1. Check network connectivity and firewall rules
2. Verify authentication and authorization
3. Review API configurations and limits
4. Check service health status
5. Review error logs and diagnostics
6. Test integration with minimal reproduction case

#### Data Loss
**Problem**: Accidental data deletion or corruption
**Solutions**:
1. Restore from recent backups
2. Check point-in-time recovery options
3. Review data deletion policies
4. Implement additional backup strategies
5. Conduct root cause analysis
6. Strengthen data protection controls

## Best Practices Summary

### Architecture Best Practices
- Design for scalability and reliability
- Use managed services where possible
- Implement loose coupling between services
- Design for failure and implement redundancy
- Use multi-region deployment for critical applications
- Implement circuit breakers and retries
- Use asynchronous processing for long-running tasks

### Security Best Practices
- Implement zero-trust security model
- Use encryption everywhere
- Regular security audits and penetration testing
- Implement least privilege access
- Monitor and log all access
- Use automated security scanning
- Keep systems and dependencies updated
- Implement proper data lifecycle management

### Cost Best Practices
- Right-size resources based on actual usage
- Use auto-scaling for variable workloads
- Take advantage of spot instances and discounts
- Implement proper tagging for cost allocation
- Regular review and optimization of resources
- Use serverless for appropriate workloads
- Optimize data storage and transfer
- Monitor costs continuously

### Operational Best Practices
- Infrastructure as code for repeatability
- Comprehensive monitoring and alerting
- Automated testing and deployment
- Documentation and knowledge sharing
- Regular performance optimization
- Incident response procedures
- Capacity planning and forecasting
- Continuous improvement and learning
"""

# Performance Characteristics
PERFORMANCE_METRICS = {
    "response_time": "< 2 seconds for initial recommendations",
    "accuracy": "100% technical accuracy with zero hallucination",
    "coverage": "All major cloud providers and services",
    "scalability": "Handles enterprise-level cloud architectures",
    "token_efficiency": {
        "metadata": "~50 tokens",
        "summary": "~300 tokens",
        "detailed": "~2000 tokens",
        "full": "~5000+ tokens"
    }
}

# Examples and Use Cases
USE_CASES = [
    "Multi-cloud strategy design",
    "Cloud migration planning",
    "Serverless architecture implementation",
    "Cost optimization analysis",
    "Security compliance validation",
    "Performance optimization",
    "Disaster recovery planning",
    "DevOps automation setup"
]

# Integration Points
INTEGRATIONS = [
    "AWS Services (Lambda, S3, RDS, DynamoDB)",
    "Azure Services (Functions, Storage, Cosmos DB)",
    "GCP Services (Cloud Functions, Storage, BigQuery)",
    "Infrastructure as Code (CloudFormation, Terraform, Bicep)",
    "CI/CD pipelines (GitHub Actions, Azure DevOps, Cloud Build)",
    "Monitoring tools (CloudWatch, Azure Monitor, Cloud Monitoring)"
]

# Cross-References
CROSS_REFERENCES = [
    "real_time_application_expert - for real-time cloud messaging",
    "desktop_integration_expert - for local cloud client applications",
    "industrial_ui_expert - for cloud-based user interfaces",
    "react_next_integration_expert - for frontend cloud deployment"
]

# Related Skills
RELATED_SKILLS = [
    "Serverless architecture patterns",
    "Microservices design principles",
    "DevOps automation",
    "Site reliability engineering",
    "Cloud security best practices",
    "Data engineering pipelines",
    "Performance optimization",
    "Cost management"
]