resource "aws_eip" "ssml-eip" {
  instance    = "${aws_instance.ssml-app-instance.id}"
}