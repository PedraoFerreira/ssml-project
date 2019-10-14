# AWS Config

variable "aws_access_key" {
  default = ""
}

variable "aws_secret_key" {
  default = ""
}

variable "aws_region" {
  default =  "us-east-1" #Norte da Virginia
}

variable "public_key_path" {
  description = "Path to the public SSH key you want to bake into the instance."
  default     = "../ssh-keys/ssml_key.pub"
}

variable "private_key_path" {
  description = "Path to the private SSH key, used to access the instance."
  default     = "../ssh-keys/ssml_key"
}

variable "ssml_default_tags" {
    type = "map"
    default = {
        project = "ssml",
        app = "console-ssml"
  }
}

variable "lambda_function_path" {
  description = "Path to lambda_function folder"
  default     = "../../lambda-function"
}
