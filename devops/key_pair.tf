resource "aws_key_pair" "ssml-key" {
  key_name   = "ssml-key"
  public_key = "${file("ssml_key.pub")}"
}