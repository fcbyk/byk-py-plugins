# Slide

[![PyPI](https://img.shields.io/pypi/v/byk-slide.svg)](https://pypi.org/project/byk-slide/)
[![Python](https://img.shields.io/badge/python-%E2%89%A53.10-blue?logo=python&logoColor=white)](https://www.python.org/downloads/)

A LAN-based remote presentation control plugin for `byk`.

`Slide` lets you quickly start a web-based PPT remote control service on your local network.
You can use your phone or other mobile devices to control slides and basic mouse actions remotely through a browser.

## Installation

If the `byk` command is already available on your system:

```bash
pip install byk-lansend
```

If you don't have `byk` installed yet:

```bash
pip install "byk-lansend[byk]"
```

## Features

* Start a web-based PPT remote control service
* Control previous/next slide and jump to first/last slide from any device on the same LAN
* Support basic mouse controls, including:

  * mouse movement
  * left click
  * right click
  * long press
  * scroll wheel
* Protect the control page with an access password

## Usage

Start Slide:

```bash
byk slide [OPTIONS]
```

After startup, Slide will:

* Check whether the port is available
* Interactively ask for an access password and require confirmation (cannot be empty)
* Start a Flask + Socket.IO based web control service
* Display available LAN access addresses
* Automatically copy one access address to the clipboard
* Automatically open the control page in the default browser

## Parameters

* `-p, --port`
  Specify the web service port. Default: `80`

* `-nb, --no-browser`
  Disable automatically opening the browser

## Examples

Start Slide using the default port (`80`):

```bash
byk slide
```

Start Slide on a custom port:

```bash
byk slide -p 8080
```

Typical workflow during a presentation:

```bash
# 1. Start Slide on the presentation computer
byk slide -p 8080

# 2. Open the control address on your phone
#    under the same Wi-Fi network

# 3. Enter the access password

# 4. Use the web page to control slides and mouse actions
```

## Notes

* Slide works by simulating keyboard and mouse events. Make sure your environment allows such operations and avoid conflicts with other automation software.
* It is recommended to test locally before a presentation to ensure compatibility with your system, presentation software, and `pyautogui`.
* For safety, only run Slide when needed and keep the access password secure.
* Slide is designed for LAN usage only and is not recommended for direct public network exposure.
