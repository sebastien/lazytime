
Features
--------

[ ] Report: lookahead and determine column format
[ ] Aggregator: aggregate some values

Tasks
-----

[X] Convert to SQLite with a structure of (Project, Event) where
    Project:{id,name}, Event:{id,project:#,timestamp,tag:#} Tag:{id,label}
[X] Use click
[-] Use https://pypi.org/project/tabulate/ → Doesn't work well
[ ] SystemD suspend/resume tasks: https://bbs.archlinux.org/viewtopic.php?id=151640

Events
------

[ ] Idling: X11 (xssstate) 
[ ] Idling: Wayland dbus-send --print-reply --dest=org.gnome.Mutter.IdleMonitor /org/gnome/Mutter/IdleMonitor/Core org.gnome.Mutter.IdleMonitor.GetIdletime from [here](https://unix.stackexchange.com/questions/396911/how-can-i-tell-if-a-user-is-idle-in-wayland)

Algorithm
---------

- Iterate on timestamp-sorted events


Commands
--------

- lazytime config
- lazytime dump
- lazytime log <PROJECT> <EVENT> <ARGS…>

Reports
-------


Timesheet::

	Logs time per project, per day.

    ```
    DATE         DAY    LOGGED 

    2018-10-01   Mon    6h00        del-myinsight-ffkit
                        0h14        ff-libs
                        0h01        ff-kit
                        ----
                        7h15

    2018-10-02   Tue    0h44        wapikoni-map
                        0h18        ff-libs
                        0h18        del-myinsight-ffkit
                        0h00        pcss
                        ----
                        1h20
    -----------------------------------------------------
    Hours during period : 8h35
    Average hours/day   : 1h20
    ```

Journal::

	Logs events, aggregated when contigious for the same project.

    ```
    DATE         DAY    EVENT

    2018-10-01   Mon    8h00    9h00     del-myinsights    1h
                        9h00   12h00     ff-kit            2h
                        12h00  13h25     [AUTO] break      2h

    -----------------------------------------------------
    Hours during period : 8h35
    Average hours/day   : 1h20
    ```

Projects::

	Logs hours per project over the period of time.

    ``` 
    PROJECT        FIRST      LAST         ELAPSED ENTRIES HOURS  HOUR/DAY
    del-myinsights 2018-09-01 2018-10-02       32d     20d  200h        5h
    ```
