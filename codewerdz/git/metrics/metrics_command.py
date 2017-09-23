import datetime
import json
import sys

import codewerdz
import codewerdz.git
import codewerdz.git.cli

from codewerdz.git.metrics.commit_analyzer import CommitAnalyzer
from codewerdz.git.log.log_command import iterate_commits

import click


@click.command()
@click.option('--metrics-precision', help="Precision levels to output.", multiple=True, default=codewerdz.git.metrics.DEFAULT_PRECISION, type=click.Choice(codewerdz.git.metrics.PRECISION_CHOICES))
@click.option('--metric', help="Metrics to output.", multiple=True, default=codewerdz.git.metrics.DEFAULT_METRICS, type=click.Choice(codewerdz.git.metrics.METRICS_CHOICES))
@click.pass_context
def metrics(ctx, metrics_precision, metric):

  options = ctx.obj.copy()

  # Print Options
  codewerdz.debug("Precision    : {}".format(', '.join(sorted(metrics_precision))))
  codewerdz.debug("Metrics      : {}".format(', '.join(sorted(metric))))

  # Iterate Log and Parse Commits
  commits = iterate_commits(
    options['docs_pattern'],
    options['comments_are_docs'],
    options['date_range_start'],
    options['date_range_end'],
    options['commits_limit'],
    options['exclude_path']
  )

  # Analyze Commits
  analyzer = CommitAnalyzer()
  analysis_results = analyzer.analyze_commits(commits, metrics_precision, metric)

  # Prepare Output
  output = {'repos': {}}
  output['repos'][options['repo_name']] = {
    "url": options['repo_url'],
    "analysis_date": json_date(datetime.datetime.utcnow()),
    "date_range": {
      "start_date": options['date_range_start'],
      "end_date": options['date_range_end']
    },
    "metrics": analysis_results
  }

  # Output JSON
  sys.stdout.write(json.dumps(output, sort_keys=True, indent=2))


def json_date(d):
  return d.isoformat()[:-3] + "Z"
