output "server-ip" {
  value = "${aws_eip.ssml-eip.public_ip}"
}