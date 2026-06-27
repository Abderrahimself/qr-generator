variable "vm_name" {
  description = "Name of the VM / libvirt domain."
  type        = string
  default     = "qr-server-tf"
}

variable "vcpus" {
  description = "Number of virtual CPUs."
  type        = number
  default     = 2
}

variable "memory_mb" {
  description = "RAM in MB."
  type        = number
  default     = 4096
}

variable "disk_size_gb" {
  description = "Root disk size in GB (grown from the cloud image by cloud-init)."
  type        = number
  default     = 20
}

variable "pool" {
  description = "libvirt storage pool (system daemon)."
  type        = string
  default     = "default"
}

variable "network_cidr" {
  description = <<-EOT
    CIDR for the VM's dedicated NAT network. Avoid existing subnets on this host:
    192.168.121.0/24 (vagrant mgmt), 192.168.50.0/24 (vagrant private),
    192.168.122.0/24 (libvirt default).
  EOT
  type        = string
  default     = "192.168.60.0/24"
}

variable "image_url" {
  description = "Ubuntu 24.04 LTS cloud image (qcow2). Downloaded once into the pool."
  type        = string
  default     = "https://cloud-images.ubuntu.com/releases/noble/release/ubuntu-24.04-server-cloudimg-amd64.img"
}

variable "ssh_public_key_path" {
  description = "Public key injected into the cloud image's default user for SSH/Ansible."
  type        = string
  default     = "~/.ssh/id_ed25519.pub"
}

variable "username" {
  description = "Initial login user (the cloud image default). Ansible creates the deploy user later."
  type        = string
  default     = "ubuntu"
}
