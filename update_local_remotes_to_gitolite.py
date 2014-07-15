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

  url = [<userid>@]<old-remote-machine>:<old-remote-dir>/<sub-dir>/<repo-name>[.git]

and replaces it with:

  url = <new-remote-base><sub-dir>/<remote-name>

If <userid> was used in the original remote URL, it is discarded because
gitolite always uses a special seperate user (e.g. 'git').  Also, to normalize
the git repo name, the optional ".git" extension is removed.

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

  (repoNameBase, repoNameExt) = os.path.splitext(repoName)
  if repoNameExt == ".git":
    repoName = repoNameBase

  return {
    "userid" : userid,
    "machine" : machine,
    "baseDir" : baseDir,
    "repoName" : repoName
    }


def matchesMachineAndBaseDir(remoteUrlDict, machine, baseDir):

  if remoteUrlDict.get("machine") != machine:
    return False

  remoteBaseDir = remoteUrlDict.get("baseDir")
  if remoteBaseDir == baseDir:
    return True
  elif remoteBaseDir.find(baseDir+"/") == 0:
    return True

  return False


def getNewRemoteUrlStrFromOldUrlDict(oldRemoteUrlDirct, oldRemoteBaseDir,
  newRemoteBase \
  ):
  # Find the left over subdir path that must be added to the new remote URL
  oldFullRemoteDir = oldRemoteUrlDirct.get("baseDir")
  if oldFullRemoteDir == oldRemoteBaseDir:
    subDir = ""
  else:
    oldRemoteBaseDirSlash = oldRemoteBaseDir+"/"
    if oldFullRemoteDir.find(oldRemoteBaseDirSlash) != 0:
      raise Exception("Error, the matching base dir path '"+oldRemoteBaseDir+"'" \
        +" is not the beginning path in the remote repo path '"+oldFullRemoteDir+"'!")
    subDir = oldFullRemoteDir[len(oldRemoteBaseDirSlash):]+"/"
  # Return the new remote URL
  return newRemoteBase+subDir+oldRemoteUrlDirct.get("repoName")


def updateGitConfigFileStr(oldGitConfigStr, oldMachineNames, oldRemoteBaseDir,
  newRemoteBase \
  ):

  newGitConfigFileStr = ""

  oldGitConfigStrArray = oldGitConfigStr.split("\n")
  if(oldGitConfigStrArray[-1] == ""): # Get rid of last dummy empty line after the last "\n"
    oldGitConfigStrArray = oldGitConfigStrArray[:-1]

  for line in oldGitConfigStrArray:

    #print "\nline = '"+line+"'"

    didReplacement = False

    # Look for the beginning url

    if line.find("\turl") == 0:

      skipReplacement = False

      lineEqSplit = line.split("=")

      # Make sure we have <something1> = <something2>
      if len(lineEqSplit) != 2:
        # Line is not split by '=' so don't replace!
        skipReplacement = True

      # Make sure that <something1> == 'url'
      if not skipReplacement:
        leftOfEq = lineEqSplit[0].strip()
        #print "leftOfEq = '"+leftOfEq+"'"
        if leftOfEq != "url":
          skipReplacement = True

      # If the line is matching for "\turl =", then repalce the URL
      if not skipReplacement:

        oldRemoteUrlDict = getRemoteUrlDict(lineEqSplit[1].strip())
        #print "oldRemoteUrlDict =", oldRemoteUrlDict

        # Make sure this URL matches what we are looking to replace
        matchesOne = False
        for oldMachineName in oldMachineNames:
          if  matchesMachineAndBaseDir(oldRemoteUrlDict, oldMachineName,
            oldRemoteBaseDir \
            ):
            #print "Matches '"+oldMachineName+"' and '"+oldRemoteBaseDir+"'!"
            matchesOne = True
        if not matchesOne:
          skipReplacement = True

        if not skipReplacement:
          # The URL matches so we just need to do the replacement!
          newRemoteUrl = getNewRemoteUrlStrFromOldUrlDict(oldRemoteUrlDict,
            oldRemoteBaseDir, newRemoteBase)
          newLine = "\turl = "+newRemoteUrl
          #print "newLine = '"+newLine+"'"
          newGitConfigFileStr += (newLine+"\n")
          didReplacement = True

    if not didReplacement:
      newGitConfigFileStr += (line+"\n")

  return newGitConfigFileStr



#
# Script body
#


if __name__ == '__main__':

  raise Exception("ToDo: Implement!")

#  LocalWords:  repos repo
