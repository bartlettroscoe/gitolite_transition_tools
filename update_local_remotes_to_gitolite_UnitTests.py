
import unittest
import sys
import imp

from update_local_remotes_to_gitolite import *


#
# Test data
#


git_config_file_1 = \
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
	fetch = +refs/heads/*:refs/remotes/casl-dev/*
[remote "casl-dev3"]
	url = 8vt@casl-dev:/git-root/collaboration/Trilinos
	fetch = +refs/heads/*:refs/remotes/casl-dev/*
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


if __name__ == '__main__':
  unittest.main()
