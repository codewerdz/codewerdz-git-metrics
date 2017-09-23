from codewerdz.git.log.git_log_process import GitLogProcess
from codewerdz.git.log.git_log_parser import GitLogParser
from codewerdz.git.streaming_json_list_printer import StreamingJsonListPrinter

import click


@click.command()
@click.pass_context
def log(ctx):

  options = ctx.obj

  commits = iterate_commits(
    options['docs_pattern'],
    options['comments_are_docs'],
    options['date_range_start'],
    options['date_range_end'],
    options['commits_limit'],
    options['exclude_path']
  )

  # Output JSON
  StreamingJsonListPrinter.dump(commits)


def iterate_commits(docs_pattern, comments_are_docs, date_range_start, date_range_end, commits_limit, exclude_path):
  # Iterate Git Log and Parse Commits
  parser = GitLogParser(docs_pattern, comments_are_docs)
  log = GitLogProcess(since=date_range_start, until=date_range_end, limit=commits_limit, excluded_paths=exclude_path)
  return parser.parse(log.get_lines())
