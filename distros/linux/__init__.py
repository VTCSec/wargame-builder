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
import os
import random
import distros


class Linux(distros.Distro):
    def crypt_password(self, password):
        """Encrypt a password in shadow format using sha512."""

        chrs = 'ABCDEFGHIJLKMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwzyx012345678\
                90'
        salt = "".join(random.sample(chrs, 8))
        return crypt.crypt(password, '$6${0}$'.format(salt))

    def set_password(self, path, user, password):
        """Set the password for the given user by updating /etc/shadow."""

        shadow = os.path.join(path, 'etc', 'shadow')
        csv.register_dialect('unixpwd', delimiter=':', quoting=csv.QUOTE_NONE)

        with open(shadow, 'rb') as f:
            reader = csv.reader(f, 'unixpwd')
            rows = [row for row in reader]

        for row in rows:
            if row[0] == user:
                row[1] = self.crypt_password(password)
                break

        with open(shadow, 'w') as f:
            for row in rows:
                f.write(':'.join(row) + "\n")

    def install_vulns(self, path):
        """
        Write /vulns/install.sh, which is used to install vulnerabilities at
        boot. The file will shred itself upon completion.
        """

        vulns_path = os.path.join(path, 'vulns')
        os.mkdir(vulns_path)

        f = open(os.path.join(vulns_path, 'install.sh'), 'w')
        f.write("#!/bin/bash\n")
        f.write("touch /vulns/pwned\n")
        f.write("shred -u /vulns/install.sh\n")
        f.close()
