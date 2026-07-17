variable "tenancy_ocid" {
  type        = string
  description = "OCI tenancy OCID."
}

variable "user_ocid" {
  type        = string
  description = "OCI user OCID for the API key."
}

variable "fingerprint" {
  type        = string
  description = "Fingerprint of the OCI API signing key."
}

variable "private_key_path" {
  type        = string
  description = "Path to the OCI API private key PEM file."
}

variable "region" {
  type        = string
  description = "OCI region, e.g. us-ashburn-1."
}

variable "compartment_ocid" {
  type        = string
  description = "Compartment OCID where resources are created."
}

variable "project_name" {
  type        = string
  description = "Prefix for resource display names."
  default     = "codegen-hf-deploy"
}

variable "ssh_public_key" {
  type        = string
  description = "OpenSSH public key injected into the VM (contents of id_rsa.pub)."
}

variable "instance_shape" {
  type        = string
  description = "Always Free Ampere shape recommended for model RAM."
  default     = "VM.Standard.A1.Flex"
}

variable "instance_ocpus" {
  type        = number
  description = "OCPUs for a flex shape (Always Free allows up to 4 total)."
  default     = 2
}

variable "instance_memory_gb" {
  type        = number
  description = "Memory in GB (350M model + PyTorch needs at least 4–8 GB)."
  default     = 12
}

variable "ubuntu_version" {
  type        = string
  description = "Ubuntu LTS version for the boot image."
  default     = "22.04"
}

variable "availability_domain_index" {
  type        = number
  description = "Index into availability domains (0 = first AD)."
  default     = 0
}

variable "vcn_cidr" {
  type        = string
  default     = "10.0.0.0/16"
}

variable "subnet_cidr" {
  type        = string
  default     = "10.0.1.0/24"
}
