#!/usr/bin/env python

usageHelp = r"""extract-public-ssh-keys-for-gitolite.py [OPTIONS]

Extract public SSH keys for a set of listed users'
<userid>/.ssh/authorized_keys files and create gitolite user public key files
to put into gitolite-admin/keydir/.
"""

import sys
import os
import subprocess
import commands
import re

from optparse import OptionParser

