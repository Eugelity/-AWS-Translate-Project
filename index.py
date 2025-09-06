import json
import boto3
import urllib.parse
import os

# Initialize clients with explicit region
s3_client = boto3.client('s3', region_name='us-east-1')
translate_client = boto3.client('translate', region_name='us-east-1')

def lambda_handler(event, context):
    try:
        # Extract bucket and key from S3 event
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
        
        # Read JSON from input bucket
        response = s3_client.get_object(Bucket=bucket, Key=key)
        data = json.loads(response['Body'].read().decode('utf-8'))
        
        # Validate JSON
        if 'text' not in data or 'target_language' not in data:
            raise ValueError("JSON must contain 'text' and 'target_language'")
        
        text = data['text']
        target_language = data['target_language']
        
        # Check text size (AWS Translate limit: 10,000 bytes)
        if len(text.encode('utf-8')) > 10000:
            raise ValueError("Text exceeds 10,000-byte limit")
        
        # Translate text
        translation = translate_client.translate_text(
            Text=text,
            SourceLanguageCode='auto',
            TargetLanguageCode=target_language
        )
        translated_text = translation['TranslatedText']
        
        # Create output JSON
        output = {
            'original_text': text,
            'translated_text': translated_text,
            'target_language': target_language
        }
        
        # Write to output bucket
        output_bucket = os.environ['TARGET_BUCKET_NAME']
        output_key = f"translated_{key}"
        s3_client.put_object(
            Bucket=output_bucket,
            Key=output_key,
            Body=json.dumps(output, ensure_ascii=False).encode('utf-8')
        )
        
        print(f"Translated {key} to {output_key} in {output_bucket}")
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Translation completed', 'output_key': output_key})
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")  # Logs to CloudWatch
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }