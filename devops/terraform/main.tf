resource "aws_instance" "ssml-app-instance" {
  ami           = "${data.aws_ami.ubuntu.id}" #"ami-07d0cf3af28718ef8"
  instance_type = "t2.micro"
  key_name      = "${aws_key_pair.ssml-key.key_name}"
  user_data = "${file("user_data/config-server.sh")}"


  security_groups = [
    "${aws_security_group.allow_ssh.name}",
    "${aws_security_group.allow_outbound.name}",
    "${aws_security_group.allow_http.name}"
  ]
/*
  provisioner "remote-exec" {
    inline = ["echo 'Hello World'"]

    connection {
      type        = "ssh"
      user        = "ubuntu"
      private_key = "${file("${var.private_key_path}")}"
    }
  }
  provisioner "local-exec" {
    command = "ansible-playbook -i '${aws_instance.ssml-app-instance.public_ip},' --private-key ${var.private_key_path} ../ansible/deploy.yml"
  }
*/
  tags = "${merge(map(
        "type", "ec2-app",
    ), var.ssml_default_tags)}"
}