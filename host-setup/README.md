# Host setup (local Fedora dev machine)

One-time prerequisites for running the local libvirt VMs (Phase 5.4 Vagrant, Phase 5.5 Terraform)
on this Fedora host. These configure the **host**, not the app — they are not part of any image
or deployment.

## 1. libvirt default storage pool

Vagrant/Terraform need a `default` storage pool in **system** libvirt (`qemu:///system`):

```bash
virsh -c qemu:///system pool-define-as default dir --target /var/lib/libvirt/images
virsh -c qemu:///system pool-build default
virsh -c qemu:///system pool-start default
virsh -c qemu:///system pool-autostart default
```

(No root needed — the libvirt socket is world-accessible; libvirtd performs the action as root.)

## 2. Docker ↔ libvirt forwarding (`libvirt-docker-forward.service`)

`docker-ce` runs on this host alongside Podman. Docker sets the netfilter `FORWARD` policy to DROP
and manages a `DOCKER-USER` chain, which blocks libvirt VMs' outbound NAT (symptom: VM resolves DNS
and pings its gateway but can't reach the internet). Docker's documented fix is to add allow rules
to `DOCKER-USER`; this unit does that persistently and for **all** libvirt bridges (`virbr+`), so it
covers every libvirt network without per-subnet edits, survives reboots, and re-applies whenever
Docker restarts (`PartOf=docker.service`).

Install:

```bash
sudo cp host-setup/libvirt-docker-forward.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now libvirt-docker-forward.service

# verify the rules are in place
sudo iptables -S DOCKER-USER
```

This supersedes any manual `iptables -I DOCKER-USER -s 192.168.121.0/24 ...` rules (which clear on
reboot). After enabling the unit you can remove those manual rules, or just let them expire at the
next reboot.

> Cleaner alternative if you ever stop using host Docker: `sudo systemctl disable --now docker docker.socket`
> removes the conflict entirely and this unit becomes unnecessary.
