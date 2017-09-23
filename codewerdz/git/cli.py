import urlparse
import codewerdz
import codewerdz.git

from codewerdz.git.process.git_process import GitProcess
from codewerdz.git.log.log_command import log as log_cli_command
from codewerdz.git.metrics.metrics_command import metrics as metrics_cli_command

import click


@click.group(chain=True)
@click.option('--verbose', is_flag=True, help="Will print verbose messages.")
@click.option('-q', '--quiet', is_flag=True, help="Will not print any log messages.")
@click.version_option(codewerdz.git.__version__)
@click.option('--repo-name', help="Name of the repo.")
@click.option('--repo-url', help="URL to the repo.")
@click.option('--date-range-start', help="Starting date of commits to analyze.", default=None)
@click.option('--date-range-end', help="Ending date of commits to analyze.", default=None)
@click.option('--commits-limit', help="Limit for how many commits to process.", default=None)
@click.option('--exclude-path', help="A glob pattern to exclude.", multiple=True, default=[])
@click.option('--docs-pattern', help="A glob pattern to match doc files.", multiple=True, default=codewerdz.git.DEFAULT_DOCS_PATTERNS)
@click.option('--comments-are-docs', is_flag=True, help="Consider comments in code to be docs.")
@click.pass_context
def cli(ctx, verbose, quiet, repo_name, repo_url, date_range_start, date_range_end, commits_limit, exclude_path, docs_pattern, comments_are_docs):
  """ codewerdz-git CLI main entry point."""

  if quiet:
    codewerdz.LOGLEVEL = codewerdz.LOGLEVEL_QUIET

  # note: verbose overrides quiet
  if verbose:
    codewerdz.LOGLEVEL = codewerdz.LOGLEVEL_DEBUG

  # guess repo url and name if not provided explictly
  if not repo_url:
    repo_url = guess_repo_url()
  if not repo_name:
    repo_name = guess_repo_name(repo_url)

  # set global context to hold program options
  ctx.obj = {
    'repo_name': repo_name,
    'repo_url': repo_url,
    'date_range_start': date_range_start,
    'date_range_end': date_range_end,
    'commits_limit': commits_limit,
    'exclude_path': exclude_path,
    'docs_pattern': docs_pattern,
    'comments_are_docs': comments_are_docs
  }

  # Print Options
  codewerdz.debug("Options:")
  codewerdz.debug("")

  codewerdz.debug("Repo Name    : {}".format(repo_name))
  codewerdz.debug("Repo URL     : {}".format(repo_url))
  if date_range_start:
    codewerdz.debug("Start Date   : {}".format(date_range_start))
  if date_range_end:
    codewerdz.debug("End Date     : {}".format(date_range_end))
  if commits_limit:
    codewerdz.debug("Commits Limit: {}".format(commits_limit))

  if exclude_path:
    codewerdz.debug("Excluded     : {}".format(', '.join(sorted(exclude_path))))

  codewerdz.debug("Docs Pattern : {}".format(', '.join(sorted(docs_pattern))))
  codewerdz.debug("Doc Comments : {}".format(comments_are_docs))


def guess_repo_url():
  """Attempts to guess the repo url by extracting the URL from the origin remote"""
  git_process = GitProcess()
  return list(git_process.get_lines("ls-remote", ["--get-url", "origin"]))[0]


def guess_repo_name(git_url):
  """Attempts to guess the repo url by extracting the URL from the origin remote"""
  return urlparse.urlparse(git_url).path[1:].split(':')[-1]

# Add subcommands to the CLI interpretter
cli.add_command(log_cli_command)
cli.add_command(metrics_cli_command)
