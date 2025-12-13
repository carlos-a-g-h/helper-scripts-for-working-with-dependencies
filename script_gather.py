#!/usr/bin/python3.9

# Given a binary to an executable or a library, this function
# will gather all of its associated dependencies in the current
# system and it will preserve their structure in the destination
# directory and reproduce their symlinks
# This is useful for stuff like making appimages for example

# Usage:
#
# program /path/to/binary /path/to/new/dir
# program /path/to/binary /path/to/new/dir lib1 lib2 lib3 .... libN
# program /path/to/binary /path/to/new/dir lib1 lib2 lib3 .... libN -
# program /path/to/binary /path/to/new/dir all
#

# NOTE about the exclusions:
#
# By default, the names in the "_DATA_EXCLUDED_BY_DEFAULT" container are excluded,
# so in order to get absolutely everything, you need to use "all"
#
# In the example of the hyphen, the names in "_DATA_EXCLUDED_BY_DEFAULT" are NOT excluded

from pathlib import Path

from constants_Any import (
	_EXC_DEFAULTS,
	_EXC_MODE_DEFAULT,
	_EXC_MODE_INCLUDE_ALL,
	_EXC_MODE_EXCLUDE_DEFAULTS,
	_EXC_SWITCH_INC_ALL,
	_EXC_SWITCH_EXC_DEF,
)
from utils_ldd import (

	_DEP_COMMON,
	_DEP_CORE,

	fun_ldd,
	util_copy_library,
)

def util_get_excluded(candidates:list)->list:

	selected=[]
	exc_mode=_EXC_MODE_DEFAULT
	for arg in candidates:
		arg_ok=arg.strip()
		if exc_mode==_EXC_MODE_DEFAULT:
			if arg_ok.lower()==_EXC_SWITCH_INC_ALL:
				exc_mode=_EXC_MODE_INCLUDE_ALL
			if arg_ok==_EXC_SWITCH_EXC_DEF:
				exc_mode=_EXC_MODE_EXCLUDE_DEFAULTS
				continue
		selected.append(arg_ok)

	return selected

def main_gather_and_copy_deps(
		path_binary:Path,
		path_dest:Path,
		exclude:list=_EXC_DEFAULTS
	)->tuple:

	print("must exclude:",exclude)

	bin_deps=fun_ldd(path_binary)

	total=len(bin_deps)
	count=0

	for thing in bin_deps:

		print(thing)

		if thing[0] is False:
			continue

		if thing[1] not in (_DEP_COMMON,_DEP_CORE):
			continue

		if thing[1]==_DEP_CORE:
			count=count+1
			continue

		if not Path(thing[3]).is_file():
			continue

		if not util_copy_library(
			thing[3],
			path_dest,
			exclude=exclude
		):
			print("failed to setup")
			continue

		count=count+1

	return (
		count==total,
		count,
		total
	)

if __name__=="__main__":

	from sys import (
		argv as sys_argv,
		exit as sys_exit
	)

	print("CLI args:",sys_argv)

	if len(sys_argv)<3:

		print("cat this script with head")
		sys_exit(0)

	arg_path_bin=1
	arg_path_dest=2
	arg_first_exc=3

	excluded_names=[]
	extra_args=len(sys_argv)>arg_first_exc

	if extra_args:
		excluded_names.extend(
			util_get_excluded(
				sys_argv[arg_first_exc:]
			)
		)

	if not extra_args:
		excluded_names.extend(_EXC_DEFAULTS)

	path_target=Path(
		sys_argv[arg_path_bin].strip()
	).resolve(strict=True)

	path_dest=Path(
		sys_argv[arg_path_dest].strip()
	).resolve(strict=True)

	result=main_gather_and_copy_deps(
		path_target,path_dest,
		exclude=excluded_names
	)

	print(result)
