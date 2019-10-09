output "server-ip" {
  value = "${aws_eip.ssml-eip.public_ip}"
}

output "lambda_url" {
  value = "${aws_api_gateway_deployment.api_deployment.invoke_url}"
}