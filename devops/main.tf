resource "aws_instance" "ssml-app-instance" {
  ami           = "${data.aws_ami.ubuntu.id}" #"ami-07d0cf3af28718ef8"
  instance_type = "t2.micro"
  key_name      = "${aws_key_pair.ssml-key.key_name}"


  security_groups = [
    "${aws_security_group.allow_ssh.name}",
    "${aws_security_group.allow_outbound.name}"
  ]

/*
  provisioner "remote-exec" {
    inline = [
      "command curl -sSL https://rvm.io/mpapis.asc | gpg --import -",
      "\\curl -sSL https://get.rvm.io | bash -s stable --rails",
    ]

    connection {
      type          = "ssh"
      user          = "ubuntu"
      private_key   = "${file("~/.ssh/ssml_key")}"
    }
  }
*/

  tags {
    type = "ec2-app"
  }
}