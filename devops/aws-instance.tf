resource "aws_instance" "ssml-app-instance" {
  ami           = "${data.aws_ami.ubuntu.id}" #"ami-07d0cf3af28718ef8"
  instance_type = "t2.micro"
  tags {
    type = "ec2-app"
  }
}