resource "aws_s3_bucket" "s3-data-upload" {
  bucket = "user-data-upload"
  acl    = "private"

  tags = "${merge(map(
        "type", "s3-app",
    ), var.ssml_default_tags)}"
}

resource "aws_s3_bucket" "s3-data-upload-output" {
  bucket = "user-data-upload-output"
  acl    = "private"

  tags = "${merge(map(
        "type", "s3-app",
    ), var.ssml_default_tags)}"
}

resource "aws_s3_bucket" "s3-lambda-package" {
  bucket = "ssml-lambda-package"
  acl    = "private"

  tags = "${merge(map(
        "type", "s3-app",
    ), var.ssml_default_tags)}"
}