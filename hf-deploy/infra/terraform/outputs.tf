locals {
  instance_public_ip = data.oci_core_public_ips.api_public_ips.public_ips[0].ip_address
}

output "instance_public_ip" {
  description = "Public IP of the API VM (use in Ansible inventory)."
  value       = local.instance_public_ip
}

output "instance_ocid" {
  description = "OCID of the compute instance."
  value       = oci_core_instance.api.id
}

output "vcn_id" {
  description = "VCN OCID."
  value       = oci_core_vcn.main.id
}

output "ssh_command" {
  description = "Example SSH command for the ubuntu user."
  value       = "ssh ubuntu@${local.instance_public_ip}"
}

output "ansible_inventory_line" {
  description = "Single-host inventory entry for Ansible."
  value       = "${local.instance_public_ip} ansible_user=ubuntu"
}
