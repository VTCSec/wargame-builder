#!/usr/bin/python2
# Copyright (c) 2011 mutantmonkey <mutantmonkey@mutantmonkey.in>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# * Neither the name of the mutantmonkey nor the
#   names of its contributors may be used to endorse or promote products
#   derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL MUTANTMONKEY BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
import subprocess
import time
import distros.linux
import distros.linux.debian


def build_vm(distro, hostname, root_password, nbd_dev, nbd_part, mountpt,
        vmimage, ip='', netmask='', gateway=''):
    """
    Modify a VM image at the specified location by mounting the root
    filesystem, setting the network configuration, hostname, root password,
    and installing vulnerabilities.
    """

    subprocess.call(['modprobe', 'nbd', 'max_part=63'])
    subprocess.call(['qemu-nbd', '-c', nbd_dev, vmimage])
    time.sleep(1)

    subprocess.call(['fsck', nbd_part])
    subprocess.call(['mount', nbd_part, mountpt])

    if not os.path.isdir(os.path.join(mountpt, 'boot')):
        raise Exception("The mountpoint does not appear to contain a Linux\
                install; ensure that the path to the image is correct and\
                /boot exists in partition 0")

    distro.set_network(mountpt, ip, netmask, gateway)
    distro.set_hostname(mountpt, hostname)
    distro.set_password(mountpt, 'root', root_password)

    # TOOD: need to specify vulnerabilities to install
    distro.install_vulns(mountpt)

    subprocess.call(['umount', mountpt])
    subprocess.call(['qemu-nbd', '-d', nbd_dev])


build_vm(distros.linux.debian.Debian(), 'wargame-testvm1', "123456", \
            '/dev/nbd0', '/dev/nbd0p1', '/media/tmp', \
            "/media/local/vms/libvirt/wargame-testvm1.img")
