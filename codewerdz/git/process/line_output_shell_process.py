from subprocess import CalledProcessError, Popen, PIPE

import codewerdz


class LineOutputShellProcess(object):
  """A class for executing a shell command, and returning each line of output in an interator."""

  def get_lines(self, command):
    """Executes a shell command and returns its output as an iterator of lines.

    Args:
        command: A sequence of strings to be executed as a shell command.

    Returns:
        An iterator of strings. Each string is one line of output.

    Raises:
        CalledProcessError: Raised if the shell command returns a non-zero exit code.
    """
    codewerdz.debug("Executing    : {}".format(" ".join(command)))
    p = Popen(command, stdout=PIPE, bufsize=1)
    with p.stdout:
      for line in iter(p.stdout.readline, b''):
        yield line[:-1]

    # wait for the subprocess to exit
    return_code = p.wait()
    if return_code != 0:
      raise CalledProcessError(return_code, command)
