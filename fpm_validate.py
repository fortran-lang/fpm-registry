def check_registry_entry(name,version,entry,dump=True):
    """Checks registry toml entry"""

    if not isinstance(entry, dict):
        raise Exception(f"registry.toml: unexpected format for package "
                        + f"'{name}-{version}', entry:\n {entry}")

    if dump:
        print("Package:", name)
        print("    Version:", version)

    # Required keys
    for key in ["git"]:
        if key not in entry:
            raise Exception(f"registry.toml: missing required key "
                          + f"'{key}' for package '{name}-{version}'")
    
    # Exactly one reference (tag/commit) is required for versioned entries
    if version != "latest" and sum(k in entry for k in ["tag"]) != 1:
        raise Exception(f"registry.toml: versioned package '{name}-{version}'"
                         + f" does not have a git reference (tag/commit)")

    if dump:
        print("        git:", entry["git"])
        if "tag" in entry:
                print("        tag:", entry["tag"])
    

def check_fpm_toml(contents):
    """Checks contents of fpm.toml, returns cut-down version for json index"""
    import toml

    p = toml.loads(contents)

    fpm_info = {}
    
    # Must be present, copied to json
    requiredKeys = ["name", "version", "license", "author", 
                       "maintainer", "copyright"]

    # Optionally present, copied to json
    optionalKeys = ["description", "executable", "dependencies",
                     "dev-dependencies"]

    # Optionally present, not copied to json
    otherKeys = ["test", "library"]

    # Check for required keys
    for key in requiredKeys:
        if key not in p:
            raise Exception(f"Missing required key '{key}' in fpm.toml.")

    for key in p.keys():
        if key not in requiredKeys + optionalKeys + otherKeys:
            print(f"        (!) Warning: unexpected key '{key}; in fpm.toml")

    # Copy keys to dict for json index
    for key in requiredKeys:
        fpm_info[key] = p[key]

    for key in optionalKeys:
        if key in p:
            fpm_info[key] = p[key]
        else:
            fpm_info[key] = None
    
    return fpm_info