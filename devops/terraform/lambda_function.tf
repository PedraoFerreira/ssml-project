# Prepare Lambda package (https://github.com/hashicorp/terraform/issues/8344#issuecomment-345807204)

resource "aws_s3_bucket_object" "layer_package_upload" {
  bucket = "${aws_s3_bucket.s3-lambda-package.bucket}"
  key    = "layer_scikit_numpy_pandas.zip"
  source = "${var.lambda_function_path}/layer/my-Python36-DtScience.zip"

  # The filemd5() function is available in Terraform 0.11.12 and later
  # For Terraform 0.11.11 and earlier, use the md5() function and the file() function:
  # etag = "${md5(file("path/to/file"))}"
  etag = "${md5(file("${var.lambda_function_path}/layer/my-Python36-DtScience.zip"))}"
}

resource "aws_lambda_layer_version" "layer_libs_python" {
  layer_name = "scikit_numpy_pandas"

  s3_bucket = "${aws_s3_bucket.s3-lambda-package.bucket}"
  s3_key = "layer_scikit_numpy_pandas.zip"

  compatible_runtimes = ["python3.6"]

  depends_on = ["aws_s3_bucket_object.layer_package_upload"]
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${var.lambda_function_path}/linear-regression/"
  output_path = "${var.lambda_function_path}/.temp/linear-regression.zip"
}

resource "aws_lambda_function" "lambda_linear_regretion" {
  filename         = "${var.lambda_function_path}/.temp/linear-regression.zip"
  source_code_hash = "${data.archive_file.lambda_zip.output_base64sha256}"
  function_name    = "ssml-linear-regression"
  role             = "${aws_iam_role.iam_for_lambda.arn}"
  handler          = "main.lambda_handler"
  runtime          = "python3.6"
  timeout          = 180
  memory_size      = 512

  environment {
    variables = {
      ENV         = "PROD"
    }
  }
  layers = ["${aws_lambda_layer_version.layer_libs_python.arn}"]
   depends_on    = ["aws_iam_role_policy_attachment.lambda_policy_attachment"]
}

resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.lambda_linear_regretion.function_name}"
  principal     = "apigateway.amazonaws.com"

  # The "/*/*" portion grants access from any method on any resource
  # within the API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.api_gateway.execution_arn}/*/*"
}