#!/usr/bin/env python
"""Functions for handling federated repositories of templates."""

import re
import os
import glob
import pygit2

def _credentials(user, password=None):
    if password:
        cred = pygit2.UserPass(user, password)
        mycb = pygit2.RemoteCallbacks()
        mycb.credentials = cred
        yield mycb
    else:
        ssh_path = os.path.join(os.path.expanduser("~"), ".ssh")
        for pub_key in glob.glob(os.path.join(ssh_path, "*.pub")):
            cred = pygit2.Keypair(user, pub_key, pub_key[0:-4], '')
            mycb = pygit2.RemoteCallbacks()
            mycb.credentials = cred
            yield mycb

def _remotes(repo, remote_name='origin', user=None):
    """Context which iterates over remotes of a given repository"""
    for remote in repo.remotes:
        if remote_name and remote.name != remote_name:
            continue
        if not user:
            url_info = _parse_repo_url(remote.url)
            user = url_info.get("user", os.getlogin())
        for mycb in _credentials(user):
            yield remote, mycb
        break

def _parse_repo_url(path):
    """Parses a url string, attempting to find a folder.git extension at the end."""
    url_re = re.compile(r'((git|ssh|http(s)?)(:(//)?)|(?P<user>[\w\d]*)@)?(?P<url>[\w\.]+).*\/(?P<dir>[\w\-]+)(\.git)(/)?')
    match = url_re.search(path)
    if not match:
        return None

    user = match.group('user') if match.group('user') else os.getlogin()

    return {'url' : match.group('url'),
            'dir': match.group('dir'),
            'user': user}

def clone_repo(url, tdir, rev=None):
    """Installs a template in the template_dir, optionally selecting a revision."""
    url_info = _parse_repo_url(url)
    if not url_info:
        raise ValueError('{0} is not a valid git URL'.format(url))
    repo_name = url_info['dir']
    repo_dest = os.path.join(tdir, repo_name)

    if os.path.exists(repo_dest):
        raise IOError('{0} already exists, cannot install on top'.format(repo))

    repo = None
    exc = None
    for cred in _credentials(url_info.get("user", os.getlogin())):
        try:
            print(url, repo_dest)
            repo = pygit2.clone_repository(url, repo_dest, callbacks=cred)
            if repo:
                break
        except pygit2.GitError as ex:
            exc = ex

    if repo:
        treeish_re = re.compile(r'[A-Za-z0-9_\-\.\/]+')
        if rev and treeish_re.match(rev):
            repo.checkout(rev)
    else:
        raise exc

def update_repo(rdir, rev=None, remote_name='origin', force=False):
    """Updates the given repository."""
    repo = pygit2.Repository(rdir)

    for remote, cred in _remotes(repo, remote_name):
        try:
            remote.fetch(callbacks=cred)
            print("Updated {0}".format(rdir))
        except pygit2.GitError:
            print("Failed {0}".format(remote.name))
            continue
        bname = repo.head.shorthand
        remote_refname = 'refs/remotes/{0}/{1}'.format(remote_name, bname)
        remote_master_id = repo.lookup_reference(remote_refname).target
        merge_result, _ = repo.merge_analysis(remote_master_id)
        if merge_result & pygit2.GIT_MERGE_ANALYSIS_FASTFORWARD:
            repo.checkout_tree(repo.get(remote_master_id))
            master_ref = repo.lookup_reference('refs/heads/{0}'.format(bname))
            master_ref.set_target(remote_master_id)
            repo.head.set_target(remote_master_id)
        elif merge_result & pygit2.MERGE_ANALYSIS_NORMAL and force:
            repo.checkout_tree(remote_master_id, strategy=pygit2.GIT_CHECKOUT_FORCE)
    if rev:
        repo.checkout(rev)
