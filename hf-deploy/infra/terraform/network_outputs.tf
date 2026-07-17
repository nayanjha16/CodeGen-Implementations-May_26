# VNIC / public IP lookups (depend on oci_core_instance.api).

data "oci_core_vnic_attachments" "api_vnics" {
  compartment_id = var.compartment_ocid
  instance_id    = oci_core_instance.api.id
}

data "oci_core_vnic" "api_vnic" {
  vnic_id = data.oci_core_vnic_attachments.api_vnics.vnic_attachments[0].vnic_id
}

data "oci_core_public_ips" "api_public_ips" {
  compartment_id = var.compartment_ocid
  scope          = "REGION"

  filter {
    name   = "private_ip_id"
    values = [data.oci_core_vnic.api_vnic.private_ip_id]
  }
}
