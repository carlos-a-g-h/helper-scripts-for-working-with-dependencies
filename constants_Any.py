#!/usr/bin/python3.9

_JOB_GATHER="gather"
_JOB_TRACE="trace"

_EXC_DEFAULTS=[
	"libc.so.6",
	"libpthread.so.0"
]

_EXC_MODE_DEFAULT=0
_EXC_MODE_INCLUDE_ALL=1
_EXC_MODE_EXCLUDE_DEFAULTS=2

_EXC_SWITCH_INC_ALL="all"
_EXC_SWITCH_EXC_DEF="-"
