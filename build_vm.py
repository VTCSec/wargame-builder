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

import crypt
import csv
import hashlib
import os
import random
import subprocess
import time


def set_network(path, ip="", netmask="255.255.255.0", gateway=""):
    """
    Update /etc/network/interfaces with network configuration information.

    If ip is left blank, the host will be configured to use DHCP.
    """

    with open(os.path.join(path, 'etc', 'network', 'interfaces'), 'w') as f:
        f.write("auto lo\niface lo inet loopback\n\n")

        if len(ip) <= 0:
            f.write("auto eth0\niface eth0 inet dhcp\n")
        else:
            f.write("auto eth0\niface eth0 inet static\n")
            f.write("\taddress {0}\n\tnetmask {1}\n\tgateway {2}\n".\
                    format(ip, netmask, gateway))


def set_hostname(path, hostname):
    """Update /etc/hostname and /etc/hosts with the specified hostname."""

    f = open(os.path.join(path, 'etc', 'hostname'), 'w')
    f.write(hostname + "\n")
    f.close()

    hosts = os.path.join(path, 'etc', 'hosts')

    with open(hosts, 'rb') as f:
        reader = csv.reader(f, delimiter="\t")
        rows = [row for row in reader]

    for row in rows:
        if len(row) > 1 and row[0] == '127.0.1.1':
            row[1] = hostname
            break

    with open(hosts, 'w') as f:
        for row in rows:
            f.write("\t".join(row) + "\n")


def crypt_password(password):
    """Encrypt a password in shadow format using sha512."""

    chars = 'ABCDEFGHIJLKMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwzyx01234567890'
    salt = "".join(random.sample(chars, 8))
    return crypt.crypt(password, '$6${0}$'.format(salt))


def set_password(path, user, password):
    """Set the password for the given user by updating /etc/shadow."""

    shadow = os.path.join(path, 'etc', 'shadow')

    csv.register_dialect('unixpwd', delimiter=':', quoting=csv.QUOTE_NONE)

    with open(shadow, 'rb') as f:
        reader = csv.reader(f, 'unixpwd')
        rows = [row for row in reader]

    for row in rows:
        if row[0] == user:
            row[1] = crypt_password(password)
            break

    with open(shadow, 'w') as f:
        for row in rows:
            f.write(':'.join(row) + "\n")


def install_vulns(path):
    """
    Write /vulns/install.sh, which is used to install vulnerabilities at boot.
    The file will shred itself upon completion.
    """

    vulns_path = os.path.join(path, 'vulns')
    os.mkdir(vulns_path)

    f = open(os.path.join(vulns_path, 'install.sh'), 'w')
    f.write("#!/bin/bash\n")
    f.write("touch /vulns/pwned\n")
    f.write("shred -u /vulns/install.sh\n")
    f.close()


def build_vm(hostname, root_password, nbd_dev, nbd_part, mountpt, vmimage,
        ip='', netmask='', gateway=''):
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
        raise Exception("The mountpoint does not appear to contain a Linux \
                install; ensure that the path to the image is correct and \
                /boot exists in partition 0")

    set_network(mountpt, ip, netmask, gateway)
    set_hostname(mountpt, hostname)
    set_password(mountpt, 'root', root_password)

    # TOOD: need to specify vulnerabilities to install
    install_vulns(mountpt)

    subprocess.call(['umount', mountpt])
    subprocess.call(['qemu-nbd', '-d', nbd_dev])


build_vm('wargame-testvm1', "123456", '/dev/nbd0', '/dev/nbd0p1',\
        '/media/tmp', "/media/local/vms/libvirt/wargame-testvm1.img")
