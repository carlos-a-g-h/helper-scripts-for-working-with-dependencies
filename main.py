#!/usr/bin/python3.9

from pathlib import Path

from utils_ldd import (

	_DEP_COMMON,
	_DEP_CORE,

	fun_ldd,
	util_copy_library,
)

from utils_packages import fun_get_package

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

	# Given a binary to an executable or a library, this function
	# will gather all of its associated dependencies in the current
	# system and it will preserve their structure in the destination
	# directory and reproduce their symlinks
	# This is useful for stuff like making appimages for example

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

def main_trace_deps(
		path_binary:Path,
		path_dest:Path,
		exclude:list=_EXC_DEFAULTS
	)->tuple:
	pass

	# Given a binary to an executable or a library, this function
	# uses ldd on it and then uses dpkg to get the name of each
	# involved package and prints a report (or multiple reports)
	# regarding all of the packages

	print("must exclude:",exclude)

	bin_deps=fun_ldd(path_binary)

	# # Include main binary
	# bin_deps.append(
	# 	Path(path_binary).resolve()
	# )

	total=len(bin_deps)+1
	count=0

	packages=[]

	name=fun_get_package(
		str(path_binary)
	)
	if name is None:
		print(
			"WARN, no package detected for:",
			path_binary
		)
	if name is not None:
		count=count+1

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

		name=fun_get_package(thing[3])
		if name is None:
			continue

		count=count+1

		if name in packages:
			print("already listed:",name)
			continue

		packages.append(name)

	print("Writting report...")
	path_report=path_dest.joinpath(
		f"{path_binary.name}.packages.txt"
	)
	with open(path_report,"wt") as f:
		for p in packages:
			f.write(f" {p}")

	return (
		count==total,
		count,
		total,
		packages
	)

if __name__=="__main__":

	from sys import (
		argv as sys_argv,
		exit as sys_exit
	)

	joblist=(_JOB_GATHER,_JOB_TRACE)

	if len(sys_argv)==1:
		print("Jobs:",joblist)
		sys_exit(0)

	job=sys_argv[1]
	if job not in joblist:
		sys_exit(1)

	# NOTE about the exclusions:
	#
	# By default, the names in the "_DATA_EXCLUDED_BY_DEFAULT" container are excluded,
	# so in order to get absolutely everything, you need to use "all"
	#
	# In the example of the hyphen, the names in "_DATA_EXCLUDED_BY_DEFAULT" are NOT excluded

	print("CLI args:",sys_argv)

	if job==_JOB_GATHER:

		arg_path_bin=2
		arg_path_dest=3
		arg_first_exc=4

		# Usage:
		#
		# program gather /path/to/binary /path/to/new/dir
		# program gather /path/to/binary /path/to/new/dir lib1 lib2 lib3 .... libN
		# program gather /path/to/binary /path/to/new/dir lib1 lib2 lib3 .... libN -
		# program gather /path/to/binary /path/to/new/dir all
		#

		excluded_names=[]
		extra_args=len(sys_argv)>arg_first_exc

		if extra_args:
			excluded_names.extend(
				util_get_excluded(
					sys_argv[4:]
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

	if job==_JOB_TRACE:

		arg_path_bin=2
		arg_path_dest=3
		arg_first_exc=4

		# Usage:
		#
		# program trace /path/to/binary /path/to/dir
		# program trace /path/to/binary /path/to/dir lib1 lib2 ... libN -
		# program trace /path/to/binary /path/to/dir lib1 lib2 ... libN
		# program trace /path/to/binary /path/to/dir all

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

		result=main_trace_deps(
			path_target,path_dest,
			exclude=excluded_names
		)

		print(result)
