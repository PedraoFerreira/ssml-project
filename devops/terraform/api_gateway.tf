resource "aws_api_gateway_rest_api" "api_gateway" {
  name        = "SSML Lambda API"
  description = "API Gateway para acessar as funcoes Lambdas"
}

resource "aws_api_gateway_resource" "resource_proxy_api" {
  rest_api_id = "${aws_api_gateway_rest_api.api_gateway.id}"
  parent_id   = "${aws_api_gateway_rest_api.api_gateway.root_resource_id}"
  path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "method_proxy_api" {
  rest_api_id   = "${aws_api_gateway_rest_api.api_gateway.id}"
  resource_id   = "${aws_api_gateway_resource.resource_proxy_api.id}"
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "api_lambda_integration" {
  rest_api_id = "${aws_api_gateway_rest_api.api_gateway.id}"
  resource_id = "${aws_api_gateway_method.method_proxy_api.resource_id}"
  http_method = "${aws_api_gateway_method.method_proxy_api.http_method}"

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "${aws_lambda_function.lambda_linear_regretion.invoke_arn}"
}

resource "aws_api_gateway_method" "method_proxy_root_api" {
  rest_api_id   = "${aws_api_gateway_rest_api.api_gateway.id}"
  resource_id   = "${aws_api_gateway_rest_api.api_gateway.root_resource_id}"
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "api_lambda_root_integration" {
  rest_api_id = "${aws_api_gateway_rest_api.api_gateway.id}"
  resource_id = "${aws_api_gateway_method.method_proxy_root_api.resource_id}"
  http_method = "${aws_api_gateway_method.method_proxy_root_api.http_method}"

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "${aws_lambda_function.lambda_linear_regretion.invoke_arn}"
}

resource "aws_api_gateway_deployment" "api_deployment" {
  depends_on = [
    "aws_api_gateway_integration.api_lambda_integration",
    "aws_api_gateway_integration.api_lambda_root_integration",
  ]

  rest_api_id = "${aws_api_gateway_rest_api.api_gateway.id}"
  stage_name  = "PROD"
}