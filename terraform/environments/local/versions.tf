# Phase 5.5 — local environment (libvirt/KVM).
# Provisions an Ubuntu 24.04 VM equivalent to the Vagrant one, but as code.
# To target Azure later (Phase 5.12), swap this provider block for azurerm and
# the resource set in terraform/environments/azure/ — Ansible/inventory are the
# only other touch points, and they consume the same outputs (vm_ip).

terraform {
  required_version = ">= 1.5"

  required_providers {
    libvirt = {
      source = "dmacvicar/libvirt"
      # Pin to the classic 0.7/0.8 line. v0.9.x is a schema-incompatible rewrite
      # (libvirt_domain loses the disk/network_interface/console/graphics blocks,
      # libvirt_volume loses source/base_volume_id/format), which breaks this config.
      # The committed .terraform.lock.hcl pins the exact patch.
      version = ">= 0.7.0, < 0.9.0"
    }
  }
}

provider "libvirt" {
  # System daemon: real NAT networking + the system storage pool. The libvirt
  # socket is world-accessible on this host, so no root is needed.
  uri = "qemu:///system"
}
