#!/usr/bin/env fish
# TODO: This should be automatically converted
if test -z "$LAZYTIME_LOG_PATH"
	set LAZYTIME_LOG_PATH "$HOME/.config/lazytime/journal.log"
end

function lazytime_log_cat
	if test -e $LAZYTIME_LOG_PATH
		cat $LAZYTIME_LOG_PATH
	end
end

function lazytime_log_tail
	if test -e $LAZYTIME_LOG_PATH
		tail -n50 $LAZYTIME_LOG_PATH
	end
end

function lazytime_log_edit
	if test -e $LAZYTIME_LOG_PATH
		eval $EDITOR $LAZYTIME_LOG_PATH
	end
end

function lazytime_log_cwd
	if test -e .lazytime
		set LAZYTIME_PROJECT (tail -n1 .lazytime)
	end
	if test -z "$LAZYTIME_TASK"
		set LAZYTIME_TASK "cd	$PWD"
	end
	if test -n "$LAZYTIME_PROJECT"
		lazytime_log_append $LAZYTIME_PROJECT $LAZYTIME_TASK
		set -U LAZYTIME_STATUS "running"
	end
end

function lazytime_log_stop
	lazytime_log_append $LAZYTIME_PROJECT stop
	set -U LAZYTIME_STATUS "stopped"
end

function lazytime_log_start
	lazytime_log_append $LAZYTIME_PROJECT start
	set -U LAZYTIME_STATUS "running"
end

function lazytime_log_append
	if test "$LAZYTIME_STATUS" != "stopped"
		if test ! -e "$LAZYTIME_LOG_PATH"
			mkdir -p (dirname "$LAZYTIME_LOG_PATH")
		end
		if test -z "$argv[1]"
			set LAZYTIME_PROJECT "*"
		else
			set LAZYTIME_PROJECT $argv[1]
		end
		if test -z "$argv[2]"
			set LAZYTIME_TASK "cd\t$PWD"
		else
			set LAZYTIME_TASK $argv[2]
		end
		# We log the entry only if it's different from the previous one
		set ENTRY  "$LAZYTIME_PROJECT	$LAZYTIME_TASK"
		set TSTAMP (date "+%Y%m%d%H%M")
		if test "$ENTRY" != "$LAZYTIME_LAST_ENTRY" -o "$TSTAMP" != "$LAZYTIME_LAST_TSTAMP"
			echo (date '+%F %T')"	$ENTRY" >> "$LAZYTIME_LOG_PATH"
		end
		set -U LAZYTIME_LAST_ENTRY "$ENTRY"
		set -U LAZYTIME_LAST_TSTAMP "$TSTAMP"
		set -U LAZYTIME_STATUS "running"
	end
end

# EOF - vim: syntax=sh ts=4 sw=4 noet
