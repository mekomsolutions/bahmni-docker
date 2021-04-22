variable "aws_api_key" {}
variable "aws_api_secret" {}
data "aws_caller_identity" "current" {}

provider "aws" {
  access_key = var.aws_api_key
  secret_key = var.aws_api_secret
  region     = "eu-west-1"
}

resource "tls_private_key" "host-rsa" {
  algorithm = "RSA"
  rsa_bits  = 4096
}
resource "tls_private_key" "host-ecdsa" {
  algorithm = "ECDSA"
}

resource "aws_instance" "arm_builder" {
  ami           = "ami-0f4fb321056ea2a14"
  instance_type = "a1.xlarge"
  security_groups = [
    "Ping",
    "SSH"
  ]
  tags = {
    Name   = "[CI] [Ubuntu] [ARM Docker Builder] [Terraform]",
    Type   = "test",
    Owner  = "${data.aws_caller_identity.current.user_id}",
    Groups = "arm_builder, terraform",
    User   = "centos"
  }
  root_block_device {
    volume_type           = "gp2"
    delete_on_termination = "true"
  }
  user_data = <<EOF
#!/bin/bash
umask 077
echo '${tls_private_key.host-ecdsa.private_key_pem}' >/etc/ssh/ssh_host_ecdsa_key
echo '${tls_private_key.host-rsa.private_key_pem}' >/etc/ssh/ssh_host_rsa_key
# Remove unsupported keys (Terraform can't generate DSA and ED25519 keys)
rm /etc/ssh/ssh_host_dsa_key
rm /etc/ssh/ssh_host_ed25519_key
service ssh restart
EOF
}
output "arm_builder_stats" {
  value = {
    ip     = "${aws_instance.arm_builder.public_ip}",
    groups = "${aws_instance.arm_builder.tags.Groups}"
    user   = "${aws_instance.arm_builder.tags.User}"
  }
}
