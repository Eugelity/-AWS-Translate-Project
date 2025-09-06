import json
from moto import mock_aws
import boto3
import os
from unittest.mock import patch

# Mock AWS Translate response
def mock_translate_text(*args, **kwargs):
    return {'TranslatedText': '¡Hola!'}

# Set environment variable for output bucket
os.environ['TARGET_BUCKET_NAME'] = 'echo-reverie-lingobotic-test'

# Mock all AWS services
with mock_aws():
    # Create S3 client
    s3 = boto3.client('s3', region_name='us-east-1')
    
    # Create mock buckets
    s3.create_bucket(Bucket='whisper-scrolls-lingobotic-test')
    s3.create_bucket(Bucket='echo-reverie-lingobotic-test')
    
    # Upload test JSON
    test_json = {'text': 'The boy is a good boy', 'target_language': 'es'}
    s3.put_object(
        Bucket='whisper-scrolls-lingobotic-test',
        Key='input.json',
        Body=json.dumps(test_json)
    )
    
    # Simulate S3 event
    event = {
        'Records': [{
            's3': {
                'bucket': {'name': 'whisper-scrolls-lingobotic-test'},
                'object': {'key': 'input.json'}
            }
        }]
    }
    
    # Mock Translate API
    with patch('index.translate_client.translate_text', side_effect=mock_translate_text):
        from index import lambda_handler
        result = lambda_handler(event, None)
        print(result)
        
        # Verify output
        output = s3.get_object(Bucket='echo-reverie-lingobotic-test', Key='translated_input.json')
        output_data = json.loads(output['Body'].read().decode('utf-8'))
        print("Output JSON:", output_data)