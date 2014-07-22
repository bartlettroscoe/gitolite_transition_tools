#!/usr/bin/env python



#
# Defaults
#
# These defaults can be set for specific applications of the script so that
# users don't need to pass in a bunch of arguments.
#

oldRemoteMachines_default = ""
oldRemoteDir_default = ""
newRemoteBase_default = ""
localRepoDirsFile_default = ""
repoNameReplacements_default = ""


#
# Help message
#

usageHelp = r"""update-local-remotes-to-gitolite.py [OPTIONS]

Update the remotes in local repos for transition to gitolite.

This script is run by individual users to update their local git repos for
repos that are moved under gitolite repo.  This is run as, for example,

$ update-local-remotes-to-gitolite.py \
  --old-remote-machines=casl-dev,casl-dev.ornl.gov \
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
  if len(splitOnMachine) == 2:
    machine = splitOnMachine[0]
    dirAndRepo = splitOnMachine[1]
  else:
    machine = ""
    dirAndRepo = machineDirRepo

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
  newRemoteBase, repoNameReplacement \
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
  repoName = oldRemoteUrlDirct.get("repoName")
  newRepoName = repoNameReplacement.get(repoName, repoName)
  return newRemoteBase+subDir+newRepoName


def updateGitConfigFileStr(oldGitConfigStr, oldMachineNames, oldRemoteBaseDir,
  newRemoteBase, repoNameReplacement, showReplacements=False \
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

        oldRemoteUrl = lineEqSplit[1].strip()
        oldRemoteUrlDict = getRemoteUrlDict(oldRemoteUrl)
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
            oldRemoteBaseDir, newRemoteBase, repoNameReplacement)
          newLine = "\turl = "+newRemoteUrl
          #print "newLine = '"+newLine+"'"
          if showReplacements:
            print "Replacing remote '"+oldRemoteUrl+"' with '"+newRemoteUrl+"'"
          newGitConfigFileStr += (newLine+"\n")
          didReplacement = True

    if not didReplacement:
      newGitConfigFileStr += (line+"\n")

  return newGitConfigFileStr


def updateGitConfigFile(gitConfigFile, oldMachineNames, oldRemoteBaseDir,
  newRemoteBase, repoNameReplacement, noOp, dumpNewFile \
  ):

  print "\nProcessing: "+gitConfigFile

  oldGitConfigFileStr = open(gitConfigFile, "r").read()

  newGitConfigFileStr = updateGitConfigFileStr(oldGitConfigFileStr,
    oldMachineNames, oldRemoteBaseDir, newRemoteBase, repoNameReplacement, \
    showReplacements = True)

  if dumpNewFile:
    print "New file:\n---------------------------------------------"
    print newGitConfigFileStr
    print "---------------------------------------------"

  if not noOp:
    open(gitConfigFile, "w").write(newGitConfigFileStr)


def readListOfLocalRepoDirsFromFile(localRepoDirsFile):
  localRepoDirsFileStr = open(localRepoDirsFile, 'r').read()
  localRepoDirs = ["."]
  for localRepoDir in localRepoDirsFileStr.split("\n"):
    if len(localRepoDir) and localRepoDir[0] != "#":
      localRepoDirs.append(localRepoDir)
  return localRepoDirs


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
    "--old-remote-machines", dest="oldRemoteMachines", type="string",
    default=oldRemoteMachines_default,
    help="List of remote machines to match, <machine0>,<machine1>,....  This is" \
      +" the <old-remote-machines> part. (required)")

  clp.add_option(
    "--old-remote-dir", dest="oldRemoteDir", type="string",
    default=oldRemoteDir_default,
    help="Directory base for remote machines to match.  This is the"\
      +" <old-remote-dir> part. (required)")

  clp.add_option(
    "--new-remote-base", dest="newRemoteBase", type="string",
    default=newRemoteBase_default,
    help="The new base for the repalced remotes.  This is <new-remote-base>." \
      + " (required).")

  clp.add_option(
    "--local-repo-dirs", dest="localRepoDirs", type="string",
    default="",
    help="List of local repos to do replacements in <dir0>,<dir1>,..." \
      + "  If this is specified it is used over --local-repo-dirs-file.")

  clp.add_option(
    "--local-repo-dirs-file", dest="localRepoDirsFile", type="string",
    default=localRepoDirsFile_default,
    help="Path to a file that lists the local repos that will be processed.  When" \
      + " this option is used, the current directory is also included.")

  clp.add_option(
    "--repo-name-replacements", dest="repoNameReplacements", type="string",
    default=repoNameReplacements_default,
    help="List of repo name replacements '<oldName0>:<newName0>,<oldName1>:<newName1>,...'.")

  clp.add_option(
    "--no-op", dest="noOp", action="store_true",
    help="If set, then no files will be written, but files will be read.",
    default=False )

  clp.add_option(
    "--dump-new-file", dest="dumpNewFile", action="store_true",
    help="If set, then the contents of the updated files will be printed to STDOUT.",
    default=False )

  clp.add_option(
    "--debug-dump", dest="debugDump", action="store_true",
    help="If set, then a lot of debug info is printed to screen.",
    default=False )
  
  (options, args) = clp.parse_args()

  # Assert the commandline

  if not options.oldRemoteMachines:
    print "\nError: --old-remote-machines=<machine0>,<machine1>,... is required!"
    sys.exit(1)

  oldRemoteMachines = options.oldRemoteMachines.split(",")

  if not options.oldRemoteDir:
    print "\nError: --old-remote-dir=<old-remote-dir> is required!"
    sys.exit(2)

  if not options.newRemoteBase:
    print "\nError: --new-remote-base=<new-remote-base> is required!"
    sys.exit(3)

  if not (options.localRepoDirs or options.localRepoDirsFile):
    print "\nError: either --local-repo-dirs or --local-repo-dirs-file must be set!"
    sys.exit(4)

  #
  # B) Loop over the list of local repos
  #

  if options.localRepoDirs:
    localRepoDirs = options.localRepoDirs.split(",")
  else:
    localRepoDirs = readListOfLocalRepoDirsFromFile(options.localRepoDirsFile)

  repoNameReplacements = {}
  for repoNameReplaceStr in options.repoNameReplacements.split(","):
    print "\nrepoNameReplaceStr = '"+repoNameReplaceStr+"'"
    (oldRepoName, newRepoName) = repoNameReplaceStr.split(":")
    repoNameReplacements[oldRepoName] = newRepoName
  
  for localRepoDir in localRepoDirs:

    gitConfigFile = localRepoDir+"/.git/config"

    if os.path.exists(gitConfigFile):

      updateGitConfigFile(gitConfigFile, oldRemoteMachines, options.oldRemoteDir,
        options.newRemoteBase, repoNameReplacements, options.noOp, options.dumpNewFile)

#  LocalWords:  repos repo
