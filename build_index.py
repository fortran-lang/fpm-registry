from datetime import datetime
import toml, json, os, traceback, github3, argparse

from fpm_fetch_toml import GitlabLite, fetch_fpm_toml
from fpm_validate import check_registry_entry, check_fpm_toml

def cli():
    """Define and parse command lines args"""
    parser = argparse.ArgumentParser(description=
              "Parses entries in registry.toml and generates index.json",
              epilog="""
              For each entry in registry.toml:
               check that the toml entry is valid;
               fetch the corresponding fpm.toml from the git repo;
               check that the fpm.toml file is valid;
               if all valid, add to index.json.

               Default behaviour is to issue a warning for package errors;
               use check arguments to exit with non-zero status instead. 
              """)

    parser.add_argument('--check-new', dest='check_new', action='store_true',
                   default=False,
                   help='check new packages: fail fatally if an unindexed package '
                       +'is parsed incorrectly.')

    parser.add_argument('--check-existing', dest='check_existing', action='store_true',
                   default=False,
                   help='check existing pacakges: fail fatally if an indexed package '
                       +'is parsed incorrectly.')

    parser.add_argument('--check-all', dest='check_all', action='store_true',
                   default=False,
                   help='check all pacakges: fail fatally if any package '
                       +'is parsed incorrectly.')

    return parser.parse_args()


def main():
    """Main script"""

    args = cli()

    # Fetch current index.json if exists
    if os.path.isfile('index.json'):
        with open('index.json', 'r') as myfile:
            data=myfile.read()
        index = json.loads(data)
    else:
        index = {"packages": {}}

    # Load registry.toml
    registry = toml.load("registry.toml")
    # Get authentication for Github API
    if os.getenv('CI'):
        user = os.getenv('GITHUB_ACTOR')
        tkn = os.getenv('GITHUB_TOKEN')
    else:
        account = toml.load("account.toml")
        user = account["github"]["user"]
        tkn = account["github"]["token"]

    # Setup and authenticate API objects
    api_context = {"github": github3.login(user, tkn), 
                "gitlab": GitlabLite()}

    # Loop over packages from registry.toml
    n_registered = 0
    n_update = 0
    n_new = 0
    n_skip = 0
    n_breaking = 0
    n_failed = 0
    for pkg_name in registry:

        for pkg_version in registry[pkg_name]:

            n_registered += 1

            try:

                # Check registry toml entry
                pkg_info = registry[pkg_name][pkg_version]
                check_registry_entry(pkg_name,pkg_version,pkg_info)

                # We can skip versioned packages if already in index.json
                #  and git tags match
                if (f"{pkg_name}" in index["packages"]
                    and f"{pkg_version}" in index["packages"][pkg_name]
                    and "git-tag" in index["packages"][pkg_name][pkg_version]
                    and "tag" in registry[pkg_name][pkg_version]
                    and index["packages"][pkg_name][pkg_version]["git-tag"] ==
                        registry[pkg_name][pkg_version]["tag"]):

                    print("        Package version already indexed and up-to-date, skipping.")
                    n_skip += 1
                    continue
                
                # Fetch fpm.toml for package version
                if "tag" in pkg_info:
                    fpm_toml = fetch_fpm_toml(api_context,
                                              pkg_info["git"],pkg_info["tag"])
                    ref = pkg_info['tag']
                else:
                    fpm_toml = fetch_fpm_toml(api_context,pkg_info["git"])
                    ref = None

                # Build json index entry
                pkgInfoFull = check_fpm_toml(fpm_toml)
                pkgInfoFull["git"] = pkg_info["git"]
                pkgInfoFull["git-tag"] = ref

                # Counting
                if (f"{pkg_name}" in index["packages"]
                    and f"{pkg_version}" in index["packages"][pkg_name]):

                    n_update += 1
                else:
                    n_new += 1
                
                # Save to index dict
                if f"{pkg_name}" not in index["packages"]:
                    index["packages"][pkg_name] = {}

                index["packages"][pkg_name][pkg_version] = pkgInfoFull

            except Exception:
                print(f"        (!) Error processing package '"
                     +f"{pkg_name}-{pkg_version}, skipping.\n")
                traceback.print_exc()
                print("")

                # Counting
                if (f"{pkg_name}" in index["packages"]
                    and f"{pkg_version}" in index["packages"][pkg_name]):

                    n_breaking += 1
                else:
                    n_failed += 1
    
    # Update index date
    index["index-date"] = datetime.now().strftime("%c")

    # Save index to index.json
    json.dump(index, open('index.json', "w"), indent=4)

    # Dump counts
    n_indexed = sum(len(index["packages"][p].keys()) for p in index["packages"])
    print("\nIndexing complete.")
    print(f" {n_registered} packages are registered in registry.toml")
    print(f" {n_indexed} packages are indexed in index.json \n")
    print(f" {n_new} unindexed packages were added to the index sucessfully")
    print(f" {n_failed} unindexed packages failed to be indexed correctly\n")
    print(f" {n_update} indexed packages were re-indexed sucessfully")
    print(f" {n_skip} indexed versioned packages were up-to-date and skipped")
    print(f" {n_breaking} indexed packages failed to be re-indexed correctly\n")
   
    print(f"Github API remaining requests: {api_context['github'].ratelimit_remaining}")
    print(f"Gitlab API remaining requests: {api_context['gitlab'].ratelimit_remaining}")

    if n_breaking > 0 and (args.check_existing or args.check_all):
        raise Exception(f"There were indexed packages that failed to be re-indexed")

    if n_failed > 0 and (args.check_new or args.check_all):
        raise Exception(f"There were unindexed packages that failed to be indexed")

    
if __name__ == "__main__":
    main()