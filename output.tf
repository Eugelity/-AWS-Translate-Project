output "input_bucket_name" {
  value = aws_s3_bucket.input_bucket.bucket
}

output "output_bucket_name" {
  value = aws_s3_bucket.output_bucket.bucket
}

output "lambda_function_arn" {
  value = aws_lambda_function.translate_func.arn
}