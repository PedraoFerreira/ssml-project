resource "aws_key_pair" "ssml-key" {
  key_name   = "ssml-key"
  public_key = "${file("${var.public_key_path}")}"
}