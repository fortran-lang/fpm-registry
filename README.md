# fpm-registry

Centralized registry of [fpm](https://github.com/fortran-lang/fpm)
packages for the [fortran-lang](https://fortran-lang.org) site.

## How to submit a new package

Your new registry submittal should first meet the 
[general package criteria](https://github.com/fortran-lang/fortran-lang.org/blob/master/PACKAGES.md)
required of any package listed at the
[packages listing](https://fortran-lang.org/packages).

Please submit a Pull Request ([PR](https://egghead.io/series/how-to-contribute-to-an-open-source-project-on-github))
against this repository, adding the new package into the file
[registry.toml](./registry.toml)
in alphabetical order. It is recommended that you explicitly list each version using the 
[`tag`](https://docs.github.com/en/free-pro-team@latest/desktop/contributing-and-collaborating-using-github-desktop/managing-tags)
keyword, otherwise the tip of the master branch will be used. An example:

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

## Registry

When a pull request is merged it will then appear at the
[`fpm registry`](https://fortran-lang.org/packages/fpm).

## How to request help

If you have a great Fortran package that you are interested
in registering as an **fpm** package but terms like **fpm**, **PR**, **toml**, and
**python** are putting you off, then please open an
[issue](https://github.com/fortran-lang/fpm-registry/issues) at the
**fpm Registry** site listing your Repository and let us know how we can help. Get as
far as you can and identify where you got stuck. We are always happy to help.

The 
[Fortran Discourse](https://fortran-lang.discourse.group/t/welcome-to-discourse)
forum is another valuable avenue for help as well as general
discussions and announcements related to the 
[Fortran Programming Language](https://fortran-lang.org).
