# lansend

[![PyPI](https://img.shields.io/pypi/v/byk-lansend.svg)](https://pypi.org/project/byk-lansend/)
[![Python](https://img.shields.io/badge/python-%E2%89%A53.10-blue?logo=python&logoColor=white)](https://www.python.org/downloads/)

A LAN file sharing plugin for `byk`

## Installation

If the `byk` command is already available on your system:

```bash
pip install byk-lansend
```

If you don't have `byk` installed yet:

```bash
pip install "byk-lansend[byk]"
```

## Usage

Share the current directory:

```bash
byk lansend
```

Share a specific directory:

```bash
byk lansend -d /path/to/share
```

Specify port:

```bash
byk lansend -p 8080
```

After startup, it will output both local and LAN access addresses, and automatically open the browser by default.

## Parameters

- `-d, --directory`: Specify the shared directory
- `-p, --port`: Specify the port
- `-ap, --ask-password`: Set upload password at startup
- `-nb, --no-browser`: Do not automatically open browser
- `-nd, --hide-download`: Hide download button
- `-nu, --disable-upload`: Disable upload
- `--chat`: Enable chat

View help:

```bash
byk lansend -h
```