#!/usr/bin/env python

usageHelp = r"""update-local-remotes-to-gitolite.py [OPTIONS]

Update the remotes in local repos for transition to gitolite.

This script is run by individual users to update their local git repos for
repos that are moved under gitolite repo.  This is run as, for example,

$ update-local-remotes-to-gitolite.py \
  --old-remote-machine=casl-dev,casl-dev.ornl.gov \
  --old-remote-dir=/git-root \
  --new-remote-base=git@casl-dev: \
  --local-repo-dirs=repo1,repo2,...

and it replaces old git repo URLs in <localRepoDir>/.git/config files of the
form:

  url = [<userid>@]<old-remote-machine>:<old-remote-dir>/<repo-name>

and replaces it with:

  url = <new-remote-base><remote-name>

If <userid> was used in the original remote URL, it is discarded because gitolite always uses 

This is sufficient flexibility for the types of transitions this script was
designed to support.
"""

import sys
import os
import subprocess
import commands
import re

from optparse import OptionParser


#
# Functions
#


def getRemoteUrlDict(inputRemoteUrlStr):

  splitOnUserid = inputRemoteUrlStr.split("@")
  if len(splitOnUserid) == 1:
    userid = ""
    machineDirRepo = inputRemoteUrlStr
  else:
    userid = splitOnUserid[0]
    machineDirRepo = splitOnUserid[1]
  
  splitOnMachine = machineDirRepo.split(":")
  
  machine = splitOnMachine[0]
  dirAndRepo = splitOnMachine[1]

  (baseDir, repoName) = os.path.split(dirAndRepo)

  return {
    "userid" : userid,
    "machine" : machine,
    "baseDir" : baseDir,
    "repoName" : repoName
    }


  



#
# Script body
#


if __name__ == '__main__':

  raise Exception("ToDo: Implement!")

#  LocalWords:  repos repo
