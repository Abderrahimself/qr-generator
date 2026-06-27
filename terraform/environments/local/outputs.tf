output "vm_name" {
  description = "libvirt domain name."
  value       = libvirt_domain.vm.name
}

output "vm_ip" {
  description = "DHCP-assigned IP on the dedicated NAT network. Feed this into the Ansible inventory."
  value       = libvirt_domain.vm.network_interface[0].addresses[0]
}

output "ssh_command" {
  description = "Convenience SSH command (key auth as the default user)."
  value       = "ssh ${var.username}@${libvirt_domain.vm.network_interface[0].addresses[0]}"
}
