class GitlabLite:
    """Minimal gitlab api wrapper"""

    def __init__(self):
        self.ratelimit_remaining = 60

    def repo_file_contents(self,repo_owner,repo_name,path,ref):
        """ Retrieve file contents from a repo """

        import urllib.request
        import base64, json

        api_url = "https://gitlab.com/api/v4/projects/"
        api_url += f"{repo_owner}%2F{repo_name}/repository/files/{path}"
        if ref is not None:
            api_url += f"?ref={ref}"
        else:
            api_url += f"?ref=HEAD"

        with urllib.request.urlopen(api_url) as url:
            self.ratelimit_remaining = int(url.info().get('RateLimit-Remaining'))
            data = json.loads(url.read().decode())

        base64_bytes = data["content"].encode('ascii')
        message_bytes = base64.b64decode(base64_bytes)

        return message_bytes.decode('ascii')


def fetch_fpm_toml(api_context,git_url,ref=None):
    """Use various APIs to download contents of fpm.toml from git remote"""

    import re, os
    from urllib.parse import urlparse
    from git import Repo
    
    git_url_parts = urlparse(git_url)
    git_url_loc = git_url_parts.netloc
    git_url_path = git_url_parts.path.strip("/")
    parts = re.split(r'\/|\.',git_url_path)
    repo_owner = parts[0]
    repo_name = parts[1]

    if ("github.com" in git_url
        and api_context["github"].ratelimit_remaining > 0):
        # Use github.py API to retrieve fpm.toml
        print('        Retrieving fpm.toml via github api...')
        
        repo = api_context["github"].repository(repo_owner, repo_name)
        fpm_toml = repo.file_contents('fpm.toml',ref=ref)
        fpm_toml = fpm_toml.decoded.decode('ascii')

    elif ("gitlab.com" in git_url 
          and api_context["gitlab"].ratelimit_remaining > 0):
        # Use gitlab api
        print('        Retrieving fpm.toml via gitlab api...')

        fpm_toml = api_context["gitlab"].repo_file_contents(repo_owner,
                                                    repo_name,'fpm.toml',ref)

    else:
        # Fall-back on cloning git repo
        print('        Retrieving fpm.toml via git clone...')

        local_clone = os.path.join(os.getcwd(),"repos",git_url_loc,
                                   git_url_path)
        if os.path.isdir(local_clone):
            repo = Repo(local_clone)
            repo.remotes["origin"].fetch(depth=1)
        else:
            repo = Repo.clone_from(git_url, local_clone,no_checkout=True,
                                   depth=1)

        if ref is not None:
            repo.remotes["origin"].fetch(tags=True)
            cloneRef = ref
        else:
            cloneRef = "HEAD"

        fpm_toml = repo.git.show('{}:{}'.format(cloneRef, 'fpm.toml'))

    return fpm_toml