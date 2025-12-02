#!/usr/bin/python3.9

from pathlib import Path
from typing import Union

from utils_Any import cmd

_ERR="error"
_ERR_NONEXISTING_FILE="the file does not exist"
_ERR_EMPTY="empty"

_DEP_CORE=0
_DEP_COMMON=1

_KNOWN_CORE_LIBS=(

	# i386
	"linux-gate.so.1",
	"/lib/ld-linux.so.2",

	# amd64
	"linux-vdso.so.1",
	"/lib64/ld-linux-x86-64.so.2"
)

_SYM_ARROW="=>"
_SYM_NOT_FOUND="not found"

_MSG_EXCLUDED="excluded"

def util_copy_library(
		path_lib_str:str,
		path_dest:Path,
		exclude:list
	)->bool:

	path_lib_ok=Path(path_lib_str).resolve(strict=True)
	path_lib_dest=path_dest.joinpath(f".{str(path_lib_ok)}")

	if not len(exclude)==0:

		name=Path(path_lib_str).name
		if name in exclude:
			print(_MSG_EXCLUDED,name)
			return True

		name=path_lib_ok.name
		if name in exclude:
			print(_MSG_EXCLUDED,name)
			return True

		name=path_lib_dest.name
		if name in exclude:
			print(_MSG_EXCLUDED,name)
			return True

	path_lib_dest.parent.mkdir(
		parents=True,
		exist_ok=True
	)

	result=cmd([
		"cp","-va",
		str(path_lib_ok),
		str(path_lib_dest)
	])
	if not result[0]==0:
		print(result[2])
		return False
	print(result[1])

	is_symlink=Path(path_lib_str).is_symlink()
	if is_symlink:
		path_lib_link=path_dest.joinpath(f".{str(path_lib_str)}")
		if not path_lib_dest==path_lib_link:
			path_lib_link.parent.mkdir(
				parents=True,
				exist_ok=True
			)
			result=cmd([
				"ln","-s","-r",
				str(path_lib_dest),
				str(path_lib_link)
			])
			if not result[0]==0:
				print(result[2])
				return False
			print(result[1])

	return True


def util_process_ldd_line(line:str)->tuple:

	print(f"\n{line}")

	if not line.find(_SYM_ARROW)>0:
		line_split=line.split()
		if len(line_split)==0:
			return (False,None)
		if line_split[0] not in _KNOWN_CORE_LIBS:
			return (False,None)

		return (True,_DEP_CORE,line_split[0])

	line_split=line.split(_SYM_ARROW)
	if not len(line_split)==2:
		return (False,None)

	if line_split[1].strip()==_SYM_NOT_FOUND:
		return (False,_DEP_COMMON,line_split[0])

	matched_lib=line_split[1].split()
	if not len(matched_lib)==2:
		return (True,_DEP_COMMON,line_split[0])

	if not Path(matched_lib[0]).is_absolute():
		return (False,None)

	return (
		True,
		_DEP_COMMON,
		line_split[0],
		matched_lib[0],
		matched_lib[1]
	)

def fun_ldd(path_file:Union[str,Path])->list:

	if not path_file.is_file():
		return (_ERR,_ERR_NONEXISTING_FILE)

	result=cmd(["ldd",str(path_file)])
	ecode,stdout_ok,stderr_ok=result

	if not ecode==0:
		print(_ERR,stderr_ok)
		return []

	if stdout_ok is None:
		print(_ERR,_ERR_EMPTY)
		return []

	if len(stdout_ok)==0:
		print(_ERR,_ERR_EMPTY)
		return []

	ldd_dump=stdout_ok.splitlines()

	result_fun=[]

	for line in ldd_dump:

		res=util_process_ldd_line(
			line.strip()
		)
		print(res)
		if res[0] is False:
			continue

		result_fun.append(res)

	return result_fun

if __name__=="__main__":

	from sys import argv as sys_argv

	result=fun_ldd(
		Path(sys_argv[1])
	)

	print(result)