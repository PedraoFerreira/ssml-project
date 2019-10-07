provider "aws" {
  access_key = "${var.aws_access_key}"
  secret_key = "${var.aws_secret_key}"
  region     = "${var.aws_region}"

  version = "~> 2.29"
}

provider "null" {
  version = "~> 2.1"
}

provider "archive" {
  version = "~> 1.3"
}

data "aws_caller_identity" "current" {}