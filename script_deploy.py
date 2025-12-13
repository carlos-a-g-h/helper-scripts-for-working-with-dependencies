#!/usr/bin/python3.9

# Given a directory and a list of packages, the contents of the
# packages will be copied to the specified directory

# Usage:
#
# program /path/to/dir pkg1 pkg2 pkg3... pkgN

from pathlib import Path

from utils_Any import cmd
from utils_packages import fun_get_files

def main_deploy_deps(
		path_dest:Path,
		packages:list,
	)->tuple:

	list_of_paths=fun_get_files(packages)

	if len(list_of_paths)==0:
		return (False,0,0)

	total=len(list_of_paths)
	count=0

	for f in list_of_paths:

		dest=path_dest.joinpath(f".{f}")
		dest.parent.mkdir(
			parents=True,
			exist_ok=True
		)

		ec,out,err=cmd(["cp","-va",f,str(dest)])
		if not ec==0:
			print(err)
			continue

		count=count+1

	return (
		total==count,
		total,
		count,
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

	arg_path_dest=1
	arg_path_targets=2

	results=main_deploy_deps(
		Path(sys_argv[arg_path_dest]),
		sys_argv[arg_path_targets:]
	)

	print(results)

	if results[0] is False:
		sys_exit(1)
