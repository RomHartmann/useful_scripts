from subprocess import Popen, PIPE
sCommand = "ssh pc7600nr3 cat /home/table/TileMoveTable/logBook.txt"
oProc = Popen(sCommand, stdin=PIPE, stdout=PIPE, shell=True)
(sStdout, sErr) = oProc.communicate()

sOut = subprocess.check_output(sCommand.split(' '))

print sStdout



