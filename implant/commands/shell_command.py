import sys
import os
from subprocess import Popen, PIPE
from command import Command

COMMAND_LINE = "cl"

class ShellCommand(Command):
    
    display_name = "Shell Command"
    index = {COMMAND_LINE:"Command Line"}
    
    def execute(self, args):
        
        cmd_line = args[COMMAND_LINE]
        print cmd_line
        success = True
        cmd_line = cmd_line.split()

        p = Popen(cmd_line, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        results = p.communicate()[0]
        results = results.decode()

        return success, results
        