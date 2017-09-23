from codewerdz.git.process.line_output_shell_process import LineOutputShellProcess


class GitProcess(LineOutputShellProcess):
  """A wrapper class for executing an external git command."""

  GIT_EXECUTABLE = 'git'
  GIT_PAGER_OPTION = '--no-pager'

  def __init__(self):
    pass

  def get_lines(self, subcommand, params=[]):
    """Executes an external git command and returns its output as an iterator of lines.

    Args:
        subcommand: The git subcommand to execute (e.g. 'log', 'clone', etc.)
        params: A sequence of strings to be passed as parameters to the subcommand. Default []

    Returns:
        A iterator of strings, with each string being a single line of output from the command.

    Raises:
        CalledProcessError: Raised if the shell command returns a non-zero exit code.
    """
    git_command = [GitProcess.GIT_EXECUTABLE, GitProcess.GIT_PAGER_OPTION, subcommand] + params
    return super(GitProcess, self).get_lines(git_command)
