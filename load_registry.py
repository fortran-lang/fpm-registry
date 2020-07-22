import toml

d = toml.load("registry.toml")
print(d)

for pkg in d:
    print("Package:", pkg)
    for version in d[pkg]:
        print("    Version:", version)
        info = d[pkg][version]
        if isinstance(info, dict):
            if "git" in info:
                print("        git:", info["git"])
            if "tag" in info:
                print("        tag:", info["tag"])
        else:
            print("        Info:", info)
