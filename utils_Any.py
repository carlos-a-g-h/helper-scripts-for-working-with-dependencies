#!/usr/bin/python3.9

from subprocess import run as sub_run,PIPE
from typing import Optional

def fix_str(data:Optional[str])->Optional[str]:

	if not isinstance(data,str):
		return None
	data_ok=data.strip()
	if len(data_ok)==0:
		return None
	return data_ok

def cmd(command:list)->tuple:

	# returns (int,Optional[str])

	print("\n$",command)

	process=sub_run(
		command,
		stdout=PIPE,
		stderr=PIPE
	)
	rcode=process.returncode
	stdout:Optional[str]=None
	stderr:Optional[str]=None
	if isinstance(process.stdout,bytes):
		stdout=fix_str(process.stdout.decode())
	if isinstance(process.stderr,bytes):
		stderr=fix_str(process.stderr.decode())

	return (rcode,stdout,stderr)

if __name__=="__main__":

	from sys import argv as sys_argv

	result=cmd(sys_argv[1:])

	print(result)