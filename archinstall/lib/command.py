import shlex
import subprocess
import sys
from time import sleep
import json
from pathlib import Path

from colors import Colors, colored, level_logging


class SysCommand:

    def __init__(
        self,
        cmd,
        cwd = None,
        message = None,
        debug = False,
        pipes = None,
        ):

        try:
            self.cmd = shlex.split(cmd)
        except Exception as error:
            raise ValueError(f'No se puedo realizar un split de "{cmd}"\n{error}')

        if cwd is not None:
            if Path(cwd).is_dir():
                self.cwd = cwd
            else:
                raise TypeError(f'La ruta {cmd} no es un directorio')
        else:
            self.cwd = cwd

        self.message = message
        self.debug = debug
        self.pipes = pipes

        self.run()

    def __repr__(self):
        return self.stdout

    def __str__(self):
        return self.stdout

    def _command(self, cmd=None, stdin=None):
        if cmd is None:
            cmd = self.cmd

        if stdin is None:
            stdin = subprocess.PIPE
        else:
            stdin = stdin.stdout

        return subprocess.Popen(
            cmd,
            cwd = self.cwd,
            stdin = stdin,
            stdout = subprocess.PIPE,
            stderr = subprocess.STDOUT,
            shell = False,
        )

    def _progress(self, process):
        while process.poll() is None and not self.debug and self.message is not None:
            sys.stdout.write(f'{colored("[*   ]", Colors.cyan)} {self.message} \r')
            sleep(0.15)
            sys.stdout.write(f'{colored("[ *  ]", Colors.cyan)} {self.message} \r')
            sleep(0.15)
            sys.stdout.write(f'{colored("[  * ]", Colors.cyan)} {self.message} \r')
            sleep(0.15)
            sys.stdout.write(f'{colored("[   *]", Colors.cyan)} {self.message} \r')
        if self.debug:
            for line in process.stdout:
                print(line.decode('UTF-8').strip(), flush=True)

    def _process_output(self, process):
        self._progress(process)

        stdout, stderr = process.communicate()

        self.stdout = stdout.decode('UTF-8').strip()
        self.stderr = self.stdout

        return_code = int(process.returncode)
        if return_code == 0:
            self.return_code = 0
        else:
            self.return_code = 3

    def run(self) -> None:
        command_output = None
        if self.pipes:
            main_command = self._command()
            previous_command = main_command
            
            pipe_command = None
            for pipe in self.pipes:
                try:
                    pipe_list = shlex.split(pipe)
                except Exception as error:
                    raise ValueError(f'String incorrecto para un split: "{pipe}"\n{error}')
                
                pipe_command = self._command(cmd = pipe_list, stdin=previous_command)
                previous_command = pipe_command

            command_output = pipe_command
        else:
            command_output = self._command()

        self._process_output(command_output)

        if self.return_code == 0:
            if self.message is not None:
                sys.stdout.write(f"{level_logging('[OK]', level=self.return_code)} {self.message}  \n")
                print(self.stdout)
        else:
            if self.message is not None:
                sys.stdout.write(f"{level_logging('[--]', level=self.return_code)} {self.message}  \n")
                print(self.stdout)

    def split(self):
        return self.stdout.split('\n')

    def json(self, key=None):
        if self.stdout.startswith('{'):
            output = json.loads(self.stdout)
            if key is None:
                return output
            else:
                return output[key]
        return None        
