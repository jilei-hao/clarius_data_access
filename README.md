# clarius_data_access

## Setup

### On The App

- Select `research` in `Settings > Scanner > Clarius Cast`
  - This ensures same port number for each session

### MacOS - Python

- Download release from https://github.com/clariusdev/cast/releases
- Copy `pyclariuscast.so` for your python version from the release to the same folder as the `clarius_streamer.py`
- Copy `libcast.dylib` from the release to a folder and add this folder to the `DYLD_LIBRARY_PATH` environment variable for each terminal session


## Run

- Turn on the transducer
- Use app to start a scan session, it will join the scanner network automatically
- In the app, check `Status` for `SSID` and `Network Password` to connect the scanner network from the computer
- Run `clarius_streamer.py` or any other program imports it
