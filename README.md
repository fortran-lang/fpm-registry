# fpm-registry

Centralized registry of fpm packages

## How to submit a new package

Please submit a pull request against this repository, add the new package into the file
[registry.toml](./registry.toml) in alphabetical order. Explicitly list each
version using the `tag` keyword, otherwise the master branch will be used. An
example:

```toml
[datetime]
"1.7.0" = {git="https://github.com/wavebitscientific/datetime-fortran", tag="v1.7.0"}
"latest" = {git="https://github.com/wavebitscientific/datetime-fortran"}
```

## Test your edits

Before submitting the pull request, you can validate the `registry.toml` file
locally using the provided Python script.
First set up a new virtual environment and install dependencies:

```
python3 -m venv venv
source venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

To validate `registry.toml`, run:

```
python load_registry.py
```
