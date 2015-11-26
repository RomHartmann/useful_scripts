#pexpect method

import pexpect
import sys

child = pexpect.spawn("ssh {0}".format(sAccount))
# redirect output to stdout
child.logfile_read = sys.stdout

child.expect('Password for tiledemo@CERN.CH:')
child.sendline(sPass)

child.expect("$")
child.sendline("rm ~/.mozilla/firefox/*/.parentlock")

# Wait for the process to close its output
child.expect(pexpect.EOF)



OR


# subprocess method for simple password entering
from subprocess import Popen, PIPE
oProc = Popen(sCommand, stdin=PIPE, shell=True)
oProc.communicate(sPass)