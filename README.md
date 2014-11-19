gitolite_transition_tools
=========================

Some simple python scripts to help transition to using gitolite

**extract-public-ssh-keys-for-gitolite.py**:

Extract public SSH keys for a set of listed users'
`<userid>/.ssh/authorized_keys` files and create gitolite user public key files
to put into `gitolite-admin/keydir/.`

This script is to be run as sudo to gather up all of the public SSH files for
a set of users already on a machine and create gitolite-compatiable public key
files of the form `<userid>@<some-machine-name>.pub` run using something like:
```
$ sudo extract-public-ssh-keys-for-gitolite.py \
--homedir=/home \
--userids=<usr0>,<usr1>,... \
--keydir=~/gitolite-admin/keydir
```

**update-local-remotes-to-gitolite.py**:

Update the remotes in local repos for transition to gitolite.
This script is run by individual users to update their local git repos for
repos that are moved under gitolite repo. This is run as, for example,
```
$ update-local-remotes-to-gitolite.py \
--old-remote-machines=casl-dev,casl-dev.ornl.gov \
--old-remote-dir=/git-root \
--new-remote-base=git@casl-dev: \
--local-repo-dirs=repo1,repo2,...
```







