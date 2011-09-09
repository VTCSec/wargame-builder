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

import csv
import os
import distros.linux


class Debian(distros.linux.Linux):
    def set_network(self, path, ip="", netmask="255.255.255.0", gateway=""):
        """
        Update /etc/network/interfaces with network configuration information.

        If ip is left blank, the host will be configured to use DHCP.
        """

        with open(os.path.join(path, 'etc', 'network', 'interfaces'), 'w') \
                as f:
            f.write("auto lo\niface lo inet loopback\n\n")

            if len(ip) <= 0:
                f.write("auto eth0\niface eth0 inet dhcp\n")
            else:
                f.write("auto eth0\niface eth0 inet static\n")
                f.write("\taddress {0}\n\tnetmask {1}\n\tgateway {2}\n".\
                        format(ip, netmask, gateway))

    def set_hostname(self, path, hostname):
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
