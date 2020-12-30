# 🌊 seaport

<img src="https://avatars2.githubusercontent.com/u/4225322?s=280&v=4" align="right"
     alt="MacPorts Logo" width="150">

*A more mighty `port bump` for MacPorts!*

## ✨ Features

* __Automatically determines new version numbers and checksums__ for MacPorts portfiles.
* __Copies the changes to your clipboard 📋__, and optionally __sends a PR to update them__.
* Contains __additional checking functionality__, such as running tests, linting and installing the updated program.

## 🤖 Example

```
> seaport gping
👍 New version is 1.2.0-post
🔻 Downloading from https://github.com/orf/gping/tarball/v1.2.0-post/gping-1.2.0-post.tar.gz
🔎 Checksums:
Old rmd160: 8b274132c8389ec560f213007368c7f521fdf682
New rmd160: 4a614e35d4e1e496871ee2b270ba8836f84650c6
Old sha256: 1879b37f811c09e43d3759ccd97d9c8b432f06c75a27025cfa09404abdeda8f5
New sha256: 1008306e8293e7c59125de02e2baa6a17bc1c10de1daba2247bfc789eaf34ff5
Old size: 853432
New size: 853450
⏪️ Changing revision numbers
No changes necessary
📋 The contents of the portfile have been copied to your clipboard!
```

## ⬇️ Install

Note that if installing from PyPi or building from source, [MacPorts](https://www.macports.org/) needs to already be installed, and [GitHub CLI](https://cli.github.com/) is required if using the `--pr` flag.

### Homebrew 🍺

Binary bottles are available for x86_64_linux, catalina and big_sur.

```
brew install harens/tap/seaport
```

### PyPi 🐍

```
pip install seaport
```

### Build from source ☁️

```
git clone https://github.com/harens/seaport
cd seaport
poetry install
poetry shell
seaport
```

## 💻 Usage

```txt
> seaport --help
Usage: seaport [OPTIONS] NAME

  Bumps the version number and checksum of NAME, and copies the result to
  your clipboard

Options:
  --version                 Show the version and exit.
  --bump TEXT               The new version number
  --pr PATH                 Location for where to clone the macports-ports
                            repo

  --test / --no-test        Runs port test
  --lint / --no-lint        Runs port lint --nitpick
  --install / --no-install  Installs the port and allows testing of basic
                            functionality

  --help                    Show this message and exit.
```

### 🚀 Use of sudo

Sudo is only required if `--test`, `--lint` or `--install` are specified, and it will be asked for during runtime. This is since the local portfile repo needs to be modified to be able to run the relevant commands.

Any changes made to the local portfile repo are reverted during the cleanup stage.

## 🔨 Contributing

Any change, big or small, that you think can help improve this action is more than welcome 🎉.

As well as this, feel free to open an issue with any new suggestions or bug reports. Every contribution is appreciated.

## 📒 Notice of Non-Affiliation and Disclaimer

This project is not affiliated, associated, authorized, endorsed by, or in any way officially connected with the MacPorts Project, or any of its subsidiaries or its affiliates. The official MacPorts Project website can be found at <https://www.macports.org>.

The name MacPorts as well as related names, marks, emblems and images are registered trademarks of their respective owners.
