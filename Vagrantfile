# Vagrantfile — Phase 5.4: a local Ubuntu 24.04 VM that stands in for a cloud server.
# Provider: libvirt/KVM (Fedora native). Bring up with:  vagrant up --provider=libvirt
#
# The VM is configured by Ansible (Phase 5.6), not by synced folders or manual SSH —
# per DEVOPS.md ("Terraform creates, Ansible configures").

Vagrant.configure("2") do |config|
  # cloud-image/* is the vagrant-libvirt project's own cloud-init box family and
  # ships a libvirt provider. (generic/ubuntu2404 is gone from the registry; bento's
  # 24.04 has no libvirt provider.)
  config.vm.box = "cloud-image/ubuntu-24.04"
  config.vm.hostname = "qr-server"

  # Static private IP that Ansible will target.
  # NOTE: do NOT use 192.168.121.0/24 — that is vagrant-libvirt's own management
  # network; overlapping it causes address conflicts. Use a dedicated subnet.
  config.vm.network "private_network", ip: "192.168.50.10"

  # Convenience host port-forwards (the private IP above also works directly):
  config.vm.network "forwarded_port", guest: 80,   host: 8080  # app (nginx)
  config.vm.network "forwarded_port", guest: 3000, host: 3000  # Grafana (Phase 5.8)

  # We don't need the project tree inside the VM — Ansible ships files over SSH and
  # images are pulled from GHCR. Disabling the default mount avoids the NFS/sudo
  # prompt. (vagrant-sshfs is installed if you ever want `type: "sshfs"` instead.)
  config.vm.synced_folder ".", "/vagrant", disabled: true

  config.vm.provider :libvirt do |lv|
    # Fedora's vagrant-libvirt defaults to the rootless session daemon
    # (qemu:///session), which has no NAT networks and so cannot create the
    # private network above. Use the system daemon for real server-like
    # networking (NAT + the default network + system storage pool). The libvirt
    # socket is world-accessible here, so no root is needed at the vagrant level.
    lv.qemu_use_session = false
    lv.cpus = 2
    lv.memory = 4096
  end
end
