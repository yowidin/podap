# Pomodoro Day Planner

If you have an hourly plan for the whole week this app allows will display a task you are to work on in a floating 
window and will remind you to take a break in regular intervals (15 minutes by default). 

This app expects you to have a directory containing a list of daily schedules each of them containing a list of task and
their starting hours. See `example` contents for an example of such schedule.

## Installation

### Global

```bash
% pip3 install ./path/to/source/directory
```

### Virtual Environment

```bash
% virtualenv venv
% source ./venv/bin/activate
% pip3 install ./path/to/source/directory
```

# Usage

Just start the app, passing working directory as a command line argument:
```bash
% podap -wd ./path/to/working/directory
```

# Building a standalone app

Install and run `pyinstall` from a virtual environment
```bash
% pyinstaller -y --clean ./podap.spec
```

