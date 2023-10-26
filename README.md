         ___                              __                              
        /\_ \                            /\ \__  __                       
        \//\ \      __     ____    __  __\ \ ,_\/\_\    ___ ___      __   
          \ \ \   /'__`\  /\_ ,`\ /\ \/\ \\ \ \/\/\ \ /' __` __`\  /'__`\ 
           \_\ \_/\ \L\.\_\/_/  /_\ \ \_\ \\ \ \_\ \ \/\ \/\ \/\ \/\  __/ 
           /\____\ \__/.\_\ /\____\\/`____ \\ \__\\ \_\ \_\ \_\ \_\ \____\
           \/____/\/__/\/_/ \/____/ `/___/> \\/__/ \/_/\/_/\/_/\/_/\/____/
                                       /\___/                             
                                       \/__/                              

**Lazytime** is a developer-focused time tracking system that logs
events from your shell and editor and automatically derives a per-project
timesheet. Lazytime is built upon a very simple plain-text event log
which is then post-processed to create reports.

Lazytime can:

-   track when you enter and leave time-tracked directories from your
    shell.

-   track when you edit files from within your editor

## Working in a project from the terminal

    $ cd ~/Workspace/client-project
    # Time tracking is started, time tracker appears in the prompt

    $ lazytime pause
    # Time tracking is paused, time tracker is paused in the prompt

    $ lazytime resume
    # Time tracking is resumed, time tracker is running

## Logging entries through your editor

-   Open a file in a project
-   Write or close a file in a project

## Integrations

### Shell

=========

Lazytime can be integrated in your `$PROMPT` to track the directories
you're `cd'ing` to.

## Data format

### Log

    YYY-MM-DD HH:MM:SS<Tab>PROJECT<Tab>DIRECTIVE<Tab>TASK<EOL>

### Files

-   `~/.config/lazytime/events.log` is where all events are stored.

### Similiar & related tools

[Wakatime]() is a proprietary, full-featured cloud-based service with an
open source client that integrates with pretty much any editor out
there.

[Timetrap](https://github.com/samg/timetrap) provides a way to track
time per project (called "sheet") from the command line using simple
commands (`t in`, `t out`, etc.)

[Ultimate Time Tracking](https://github.com/larose/utt) is similar to
Timetrap, but more task focused than project focused.
