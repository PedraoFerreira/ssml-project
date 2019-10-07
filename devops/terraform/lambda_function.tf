# Prepare Lambda package (https://github.com/hashicorp/terraform/issues/8344#issuecomment-345807204)
resource "null_resource" "pip" {
  triggers = {
    main         = "${base64sha256(file("${var.lambda_function_path}/linear-regression/main.py"))}"
    requirements = "${base64sha256(file("${var.lambda_function_path}/requirements.txt"))}"
  }

  /*
  provisioner "local-exec" {
    command = "/usr/bin/pip3 install -r ${var.lambda_function_path}/requirements.txt -t ${var.lambda_function_path}/linear-regression/lib"
  }
  */

}

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${var.lambda_function_path}/linear-regression/"
  output_path = "${var.lambda_function_path}/zip-package/linear-regression.zip"

  depends_on = ["null_resource.pip"]
}



resource "aws_lambda_function" "lambda_linear_regretion" {
  filename         = "${var.lambda_function_path}/zip-package/linear-regression.zip"
  source_code_hash = "${data.archive_file.lambda_zip.output_base64sha256}"
  function_name    = "ssml-linear-regression"
  role             = "${aws_iam_role.iam_for_lambda.arn}"
  handler          = "main.handler"
  runtime          = "python3.6"
  timeout          = 120

  environment {
    variables = {
      HASH         = "${base64sha256(file("${var.lambda_function_path}/linear-regression/main.py"))}-${base64sha256(file("${var.lambda_function_path}/requirements.txt"))}"
    }
  }

  lifecycle {
    ignore_changes = ["source_code_hash"]
  }
}