
import unittest
import sys
import imp

from update_local_remotes_to_gitolite import *

#
# Helper functions
#

def assertEqualsLineByLine(testObj, stringIn, stringExpected):
  stringInArray = stringIn.split("\n")
  stringExpectedArray = stringExpected.split("\n")
  for i in xrange(len(stringExpectedArray)):
    if i > len(stringInArray):
      testObj.assertEqual(None, stringExpectedArray[i])
    else:
      testObj.assertEqual(stringInArray[i], stringExpectedArray[i])
  if len(stringInArray) > len(stringExpectedArray):
    testObj.assertEqual(stringInArray[len(stringExpectedArray)], None)


#
# Test data
#


git_config_file_1 = \
"""
[core]
	urltrick1
	urltrick2 = dummystuff
[remote "origin"]
	url = casl-dev:/git-root/Trilinos
	fetch = +refs/heads/*:refs/remotes/origin/*
[remote "urltrick"]
	url = something.at.com:/junk/something/Trilinos
"""

git_config_file_1_out = \
"""
[core]
	urltrick1
	urltrick2 = dummystuff
[remote "origin"]
	url = git@casl-dev:Trilinos
	fetch = +refs/heads/*:refs/remotes/origin/*
[remote "urltrick"]
	url = something.at.com:/junk/something/Trilinos
"""

git_config_file_2 = \
"""
[core]
	repositoryformatversion = 0
	filemode = true
	bare = false
	logallrefupdates = true
	sparsecheckout = false
[remote "origin"]
	url = casl-dev:/git-root/Trilinos
	fetch = +refs/heads/*:refs/remotes/origin/*
[branch "master"]
	remote = origin
	merge = refs/heads/master
[remote "casl-dev"]
	url = casl-dev:/git-root/Trilinos
	fetch = +refs/heads/*:refs/remotes/casl-dev/*
[remote "casl-dev-collab"]
	url = casl-dev.ornl.gov:/git-root/collaboration/Trilinos
	fetch = +refs/heads/*:refs/remotes/casl-dev-collab/*
[remote "casl-dev2"]
	url = 8vt@casl-dev.ornl.gov:/git-root/Trilinos
	fetch = +refs/heads/*:refs/remotes/casl-dev2/*
[remote "casl-dev3"]
	url = 8vt@casl-dev:/git-root/collaboration/Trilinos
	fetch = +refs/heads/*:refs/remotes/casl-dev3/*
[remote "ssg"]
	url = software.sandia.gov:/space/git/Trilinos
	fetch = +refs/heads/*:refs/remotes/ssg/*
[remote "urltrick"]
	url = something.at.com:/junk/something/Trilinos
"""

git_config_file_2_out = \
"""
[core]
	repositoryformatversion = 0
	filemode = true
	bare = false
	logallrefupdates = true
	sparsecheckout = false
[remote "origin"]
	url = git@casl-dev:Trilinos
	fetch = +refs/heads/*:refs/remotes/origin/*
[branch "master"]
	remote = origin
	merge = refs/heads/master
[remote "casl-dev"]
	url = git@casl-dev:Trilinos
	fetch = +refs/heads/*:refs/remotes/casl-dev/*
[remote "casl-dev-collab"]
	url = git@casl-dev:collaboration/Trilinos
	fetch = +refs/heads/*:refs/remotes/casl-dev-collab/*
[remote "casl-dev2"]
	url = git@casl-dev:Trilinos
	fetch = +refs/heads/*:refs/remotes/casl-dev2/*
[remote "casl-dev3"]
	url = git@casl-dev:collaboration/Trilinos
	fetch = +refs/heads/*:refs/remotes/casl-dev3/*
[remote "ssg"]
	url = software.sandia.gov:/space/git/Trilinos
	fetch = +refs/heads/*:refs/remotes/ssg/*
[remote "urltrick"]
	url = something.at.com:/junk/something/Trilinos
"""


#
# Unit tests
#


class test_getRemoteUrlDirct(unittest.TestCase):

  def test_1(self):
    urlDict = getRemoteUrlDict("casl-dev:/git-root/Trilinos")
    urlDict_expected = {
      "userid" : "",
      "machine" : "casl-dev",
      "baseDir" : "/git-root",
      "repoName" : "Trilinos"
      }
    self.assertEqual(urlDict, urlDict_expected)

  def test_1b(self):
    urlDict = getRemoteUrlDict("casl-dev:/git-root/Trilinos.git")
    urlDict_expected = {
      "userid" : "",
      "machine" : "casl-dev",
      "baseDir" : "/git-root",
      "repoName" : "Trilinos"
      }
    self.assertEqual(urlDict, urlDict_expected)

  def test_2(self):
    urlDict = getRemoteUrlDict("8vt@casl-dev:/git-root/Trilinos")
    urlDict_expected = {
      "userid" : "8vt",
      "machine" : "casl-dev",
      "baseDir" : "/git-root",
      "repoName" : "Trilinos"
      }
    self.assertEqual(urlDict, urlDict_expected)

  def test_3(self):
    urlDict = getRemoteUrlDict("8vt@casl-dev.ornl.gov:/git-root/collaboration/Trilinos")
    urlDict_expected = {
      "userid" : "8vt",
      "machine" : "casl-dev.ornl.gov",
      "baseDir" : "/git-root/collaboration",
      "repoName" : "Trilinos"
      }
    self.assertEqual(urlDict, urlDict_expected)


class test_matchesMachineAndBaseDir(unittest.TestCase):

  def test_1(self):
    self.assertEqual(
      matchesMachineAndBaseDir(
        getRemoteUrlDict("casl-dev:/git-root/Trilinos"),
        "casl-dev", "/git-root"
        ),
      True
      )

  def test_2(self):
    self.assertEqual(
      matchesMachineAndBaseDir(
        getRemoteUrlDict("casl-dev:/git-root/Trilinos"),
        "casl-dev", "/git-roots"
        ),
      False
      )

  def test_2b(self):
    self.assertEqual(
      matchesMachineAndBaseDir(
        getRemoteUrlDict("casl-dev:/some-other-path/Trilinos"),
        "casl-dev", "/git-roots"
        ),
      False
      )

  def test_3(self):
    self.assertEqual(
      matchesMachineAndBaseDir(
        getRemoteUrlDict("casl-dev:/git-root/collaboration/Trilinos"),
        "casl-dev", "/git-root"
        ),
      True
      )

  def test_4(self):
    self.assertEqual(
      matchesMachineAndBaseDir(
        getRemoteUrlDict("8vt@casl-dev.ornl.gov:/git-root/COBRA-TF"),
        "casl-dev", "/git-root"
        ),
      False
      )

  def test_5(self):
    self.assertEqual(
      matchesMachineAndBaseDir(
        getRemoteUrlDict("8vt@casl-dev.ornl.gov:/git-root/COBRA-TF"),
        "casl-dev.ornl.gov", "/git-root"
        ),
      True
      )


class test_getNewRemoteUrlStrFromOldUrlDict(unittest.TestCase):

  def test_1(self):
    newRemoteUrlStr = getNewRemoteUrlStrFromOldUrlDict(
      getRemoteUrlDict("casl-dev.ornl.gov:/git-root/Trilinos"),
      "/git-root", "git@casl-dev:"
      )
    newRemoteUrlStr_expected = "git@casl-dev:Trilinos"
    self.assertEqual(newRemoteUrlStr, newRemoteUrlStr_expected)

  def test_2(self):
    newRemoteUrlStr = getNewRemoteUrlStrFromOldUrlDict(
      getRemoteUrlDict("casl-dev:/git-root/collaboration/Trilinos"),
      "/git-root", "git@casl-dev:"
      )
    newRemoteUrlStr_expected = "git@casl-dev:collaboration/Trilinos"
    self.assertEqual(newRemoteUrlStr, newRemoteUrlStr_expected)

  def test_3(self):
    self.assertRaises(
      Exception,
      getNewRemoteUrlStrFromOldUrlDict,
      getRemoteUrlDict("casl-dev:/some-other-path/Trilinos"),
      "/git-root", "git@casl-dev:"
      )


class test_updateGitConfigFileStr(unittest.TestCase):

  def test_1(self):
    newGetConfigFileStr = updateGitConfigFileStr(git_config_file_1,
     ["casl-dev"], "/git-root", "git@casl-dev:" )
    assertEqualsLineByLine(self, newGetConfigFileStr, git_config_file_1_out)

  def test_2(self):
    newGetConfigFileStr = updateGitConfigFileStr(git_config_file_2,
     ["casl-dev", "casl-dev.ornl.gov"], "/git-root", "git@casl-dev:" )
    assertEqualsLineByLine(self, newGetConfigFileStr, git_config_file_2_out)


#
# Main()
#


if __name__ == '__main__':
  unittest.main()
