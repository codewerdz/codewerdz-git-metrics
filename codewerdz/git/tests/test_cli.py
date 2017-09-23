import codewerdz

from click.testing import CliRunner
from codewerdz.git.cli import cli
from unittest import TestCase


class TestCLI(TestCase):
  def test_print_version(self):
    runner = CliRunner()
    result = runner.invoke(cli, ['--version'])
    assert result.exit_code == 0
    assert result.output.endswith('version %s\n' % codewerdz.git.__version__)
