# fpm-registry

Centralized registry of fpm packages

## How to submit a new package

Please submit a PR against this repository, add the new package into the file
[registry.toml](./registry.toml) in alphabetical order. Explicitly list each
version using the `tag` keyword, otherwise the master branch will be used. An
example:
```toml
[datetime]
"1.7.0" = {git="https://github.com/wavebitscientific/datetime-fortran", tag="v1.7.0"}
"latest" = {git="https://github.com/wavebitscientific/datetime-fortran"}
```
