# Dedicated NAT network so the Terraform VM is isolated from the Vagrant one.
# DHCP assigns the address; Terraform captures it (wait_for_lease) and exports it
# as an output that the Ansible inventory consumes.
resource "libvirt_network" "net" {
  name      = "${var.vm_name}-net"
  mode      = "nat"
  addresses = [var.network_cidr]

  dhcp {
    enabled = true
  }
  dns {
    enabled = true
  }
}

# Base image, downloaded once from the Ubuntu cloud-image catalog.
resource "libvirt_volume" "base" {
  name   = "${var.vm_name}-base.qcow2"
  pool   = var.pool
  source = var.image_url
  format = "qcow2"
}

# Per-VM root disk, backed by the base image and grown to disk_size_gb.
# cloud-init's growpart/resizefs expand the filesystem to fill it on first boot.
resource "libvirt_volume" "root" {
  name           = "${var.vm_name}.qcow2"
  pool           = var.pool
  base_volume_id = libvirt_volume.base.id
  size           = var.disk_size_gb * 1024 * 1024 * 1024
  format         = "qcow2"
}

# cloud-init: hostname + SSH key for the default user (which already has
# passwordless sudo on the cloud image). Ansible bootstraps from this user.
resource "libvirt_cloudinit_disk" "init" {
  name = "${var.vm_name}-cloudinit.iso"
  pool = var.pool
  user_data = templatefile("${path.module}/templates/cloud_init.yaml.tftpl", {
    hostname   = var.vm_name
    ssh_pubkey = trimspace(file(pathexpand(var.ssh_public_key_path)))
  })
}

resource "libvirt_domain" "vm" {
  name      = var.vm_name
  memory    = var.memory_mb
  vcpu      = var.vcpus
  cloudinit = libvirt_cloudinit_disk.init.id

  disk {
    volume_id = libvirt_volume.root.id
  }

  network_interface {
    network_id     = libvirt_network.net.id
    wait_for_lease = true
  }

  # Serial console so `virsh console` works for debugging.
  console {
    type        = "pty"
    target_port = "0"
    target_type = "serial"
  }

  graphics {
    type        = "vnc"
    listen_type = "address"
  }
}
