#!/usr/bin/python3.9

from pathlib import Path
from typing import Optional
from utils_Any import cmd

_SYM_SEP=":"

def fun_get_package(
		path_file_str:str,
		name_only:bool=False
	)->Optional[str]:

	# NOTE: this function can work with other files as well, not
	# just libraries

	path_file=Path(path_file_str)

	result=cmd(["dpkg","-S",str(path_file)])
	ec,out,err=result
	if not ec==0:
		print(err)
		result=cmd(["dpkg","-S",str(path_file.resolve())])
		ec,out,err=result
		if not ec==0:
			print(err)
			return None

	if out is None:
		return None

	package:str=out.split()[0]
	if package.endswith(_SYM_SEP):
		package=package[:-1]

	if name_only:
		if not package.find(_SYM_SEP)==0:
			return package.split(":")[0]

	return package

if __name__=="__main__":

	from sys import argv as sys_argv

	name=fun_get_package(sys_argv[1])
	print(name)