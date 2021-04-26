variable "aws_api_key" {}
variable "aws_api_secret" {}
data "aws_caller_identity" "current" {}

provider "aws" {
  access_key = var.aws_api_key
  secret_key = var.aws_api_secret
  region     = "eu-west-1"
}

resource "aws_instance" "arm64_builder" {
  ami           = "ami-0f4fb321056ea2a14"
  instance_type = "a1.xlarge"
  security_groups = [
    "Ping",
    "SSH"
  ]
  tags = {
    Name   = "[GitHub Actions] [Ubuntu] [ARM64 Docker Builder] [Terraform]",
    Type   = "test",
    Owner  = "${data.aws_caller_identity.current.user_id}",
    Groups = "arm64_builder, terraform",
    User   = "centos"
  }
  root_block_device {
    volume_type           = "gp2"
    delete_on_termination = "true"
  }
}

output "arm64_builder_stats" {
  value = {
    ip     = "${aws_instance.arm64_builder.public_ip}",
    groups = "${aws_instance.arm64_builder.tags.Groups}"
    user   = "${aws_instance.arm64_builder.tags.User}"
  }
}

resource "aws_instance" "amd64_builder" {
  ami           = "ami-00c5ee06663571065"
  instance_type = "t2.xlarge"
  security_groups = [
    "Ping",
    "SSH"
  ]
  tags = {
    Name   = "[GitHub Actions] [Ubuntu] [AMD64 Docker Builder] [Terraform]",
    Type   = "test",
    Owner  = "${data.aws_caller_identity.current.user_id}",
    Groups = "amd64_builder, terraform",
    User   = "centos"
  }
  root_block_device {
    volume_type           = "gp2"
    delete_on_termination = "true"
  }
}

output "amd64_builder_stats" {
  value = {
    ip     = "${aws_instance.amd64_builder.public_ip}",
    groups = "${aws_instance.amd64_builder.tags.Groups}"
    user   = "${aws_instance.amd64_builder.tags.User}"
  }
}
