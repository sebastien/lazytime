#!/usr/bin/env bash
#
# Automatically logs entries in `timetrap` based on the $TIMETRAP_PROJECT
# environment variable.

LAZYTIME_LOG_PATH="$HOME/.config/lazytime/journal.log"

function lazytime_log_cwd {
	if test ! -e "$LAZYTIME_LOG_PATH"; then
		mkdir -p "$(dirname "$LAZYTIME_LOG_PATH")"
	fi
	if test -n "$LAZYTIME_PROJECT"; then
		echo "$(date '+%F %T')§$LAZYTIME_PROJECT§$TIMETRAP_TASK" >> "$LAZYTIME_LOG_PATH"
	fi
}


# EOF - vim: syntax=sh ts=4 sw=4 noet
