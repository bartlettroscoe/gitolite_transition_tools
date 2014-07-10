#!/usr/bin/env python

usageHelp = r"""extract-public-ssh-keys-for-gitolite.py [OPTIONS]

Extract public SSH keys for a set of listed users'
<userid>/.ssh/authorized_keys files and create gitolite user public key files
to put into gitolite-admin/keydir/.

This script is to be run as sudo to gather up all of the public SSH files for
a set of users already on a machine and create gitolite-compatiable public ky
files of the form <userid>@<some-machine-name>.pub run using something like:

$ sudo extract-public-ssh-keys-for-gitolite.py \
  --homedir=/home \
  --userids=<usr0>,<usr1>,... \
  --keydir=~/gitolite-admin/keydir

"""

import sys
import os
import subprocess
import commands
import re

from optparse import OptionParser


def getPublicSSHKeysList(authorizedKeysFile):

  if not os.path.exists(authorizedKeysFile):
    print "Warning: the file '"+authorizedKeysFile+"' does not exist!"
    return []

  authorizedKeysFileContentsStr = open(authorizedKeysFile, "r").read()
  #print "\nauthorizedKeysFileContentsStr:\n", authorizedKeysFileContentsStr
  authorizedKeysFileContentsList = authorizedKeysFileContentsStr.strip().split("\n")
  return authorizedKeysFileContentsList


def getMachineOriginName(authorizedKeyLine):
  return authorizedKeyLine.split(" ")[-1]


def getNormalizedMachineOriginName(machineOriginName):
  normalizedMachineOriginName = ""
  for c in machineOriginName:
    if c == '@':
      cr = '_'
    elif c == '.':
      cr = '_'
    else:
      cr = c
    normalizedMachineOriginName += cr
  return normalizedMachineOriginName


def writePublicSSHKeyFile(authorizedKeyLine, normalizedMachineOriginName, keydir):
  publicKeyFile = keydir+"/"+normalizedMachineOriginName+".pub"
  print "Writing file "+publicKeyFile
  open(publicKeyFile, "w").write(authorizedKeyLine+"\n")

#
# Script body
#


if __name__ == '__main__':

  #
  # A) Get command-line options
  #
  
  from optparse import OptionParser
  
  clp = OptionParser(usage=usageHelp)

  clp.add_option(
    "--homedir", dest="homeDir", type="string",
    default="/home",
    help="Home base directory.  The default is '/home'.")

  clp.add_option(
    "--userids", dest="userids", type="string",
    default="",
    help="List of userids separated by comas '<usr0>,<usr1>,...' (required)")

  clp.add_option(
    "--keydir", dest="keyDir", type="string",
    default="",
    help="Base directory where the generated public SSH key files will be" \
      + " written to (required).")
  
  (options, args) = clp.parse_args()

  # Assert the commandline

  if not options.homeDir:
    print "\nError: --homedir=<homeDir> is required!"
    sys.exit(1)

  if not options.userids:
    print "\nError: --userids=<usr0>,<usr1>,... is required!"
    sys.exit(2)

  if not options.keyDir:
    print "\nError: --keydir=<keyDir> is required!"
    sys.exit(3)

  #
  # B) Look over all of the users, extract their public keys and make the
  # public key files.
  #

  useridsList = options.userids.split(",")

  for userid in useridsList:

    print "\nExtracting public SSH keys for userid: "+userid
    authorizedKeysFile = options.homeDir+"/"+userid+"/.ssh/authorized_keys"
    authorizedKeysList = getPublicSSHKeysList(authorizedKeysFile)
    #print "\nauthorizedKeysList =", authorizedKeysList
    for authorizedKeyLine in authorizedKeysList:
      machineOriginName = getMachineOriginName(authorizedKeyLine)
      #print "machineOriginName = "+machineOriginName
      normalizedMachineOriginName = getNormalizedMachineOriginName(machineOriginName)
      #print "normalizedMachineOriginName =", normalizedMachineOriginName
      writePublicSSHKeyFile(authorizedKeyLine, normalizedMachineOriginName,
        options.keyDir)
