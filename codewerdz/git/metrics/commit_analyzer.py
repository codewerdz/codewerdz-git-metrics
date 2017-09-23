import copy
import codewerdz.git.metrics
import codewerdz
import datetime
import iso8601


class CommitAnalyzer(object):
  def __init__(self):
    pass

  def analyze_commits(self, commits, metrics_precisions, metric_names):

    metrics = copy.deepcopy(codewerdz.git.metrics.EMPTY_METRICS_PRECISIONS)

    total = get_precision('total', metrics, metrics_precisions)
    yearly = get_precision('yearly', metrics, metrics_precisions)
    monthly = get_precision('monthly', metrics, metrics_precisions)
    weekly = get_precision('weekly', metrics, metrics_precisions)
    daily = get_precision('daily', metrics, metrics_precisions)

    for commit in commits:
      chars_changed = 0
      chars_of_code = 0
      chars_of_docs = 0
      contributor = "{} <{}>".format(commit['author'], commit['email'])

      # rollup stats from diffs
      for diff in commit['diffs']:
        stats = diff['stats']
        chars_changed += stats['chars_changed']
        chars_of_code += stats['chars_of_code']
        chars_of_docs += stats['chars_of_docs']

      commit_metrics = copy.deepcopy(codewerdz.git.metrics.EMPTY_CONTRIBUTOR_METRICS)
      commit_metrics['commit_count'] = 1

      if chars_of_code > 0:
        commit_metrics['code_count'] = 1
        if chars_of_docs == 0:
          commit_metrics['only_code_count'] = 1

      if chars_of_docs > 0:
        commit_metrics['docs_count'] = 1
        if chars_of_code == 0:
          commit_metrics['only_docs_count'] = 1

      commit_metrics['chars_changed_count'] = chars_changed
      commit_metrics['code_chars_count'] = chars_of_code
      commit_metrics['docs_chars_count'] = chars_of_docs

      commit_metrics['docs_density_avg'] = chars_of_docs / float(chars_changed) if chars_changed > 0 else 0.0
      commit_metrics['docs_density_min'] = commit_metrics['docs_density_max'] = commit_metrics['docs_density_avg']

      commit_metrics['code_density_avg'] = chars_of_code / float(chars_changed) if chars_changed > 0 else 0.0
      commit_metrics['code_density_min'] = commit_metrics['code_density_max'] = commit_metrics['code_density_avg']

      # NOTE: Unlike others, if code == 0: value is 1.0
      commit_metrics['docs_to_code_avg'] = chars_of_docs / float(chars_of_code) if chars_of_code > 0 else 1.0
      commit_metrics['docs_to_code_min'] = commit_metrics['docs_to_code_max'] = commit_metrics['docs_to_code_avg']

      if total is not None:
        # total stats
        accumulate_metrics(total, commit_metrics, contributor)

      year = commit['commit_date_iso'][:4]
      if yearly is not None:
        # yearly
        if year not in yearly:
          yearly[year] = copy.deepcopy(codewerdz.git.metrics.EMPTY_REPO_METRICS)
        accumulate_metrics(yearly[year], commit_metrics, contributor)

      if monthly is not None:
         # monthly
        month = "{0}-month{1:0>2}".format(year, month_of_year(commit['commit_date_iso']))
        if month not in monthly:
          monthly[month] = copy.deepcopy(codewerdz.git.metrics.EMPTY_REPO_METRICS)
        accumulate_metrics(monthly[month], commit_metrics, contributor)

      if weekly is not None:
        # weekly
        week = "{0}-week{1:0>2}".format(year, week_of_year(commit['commit_date_iso']))
        if week not in weekly:
          weekly[week] = copy.deepcopy(codewerdz.git.metrics.EMPTY_REPO_METRICS)
        accumulate_metrics(weekly[week], commit_metrics, contributor)

      if daily is not None:
        # daily
        day = "{0}-day{1:0>3}".format(year, day_of_year(commit['commit_date_iso']))
        if day not in daily:
          daily[day] = copy.deepcopy(codewerdz.git.metrics.EMPTY_REPO_METRICS)
        accumulate_metrics(daily[day], commit_metrics, contributor)

    if total is not None:
      accumulate_contributor_metrics(total)
      filter_metrics(total, metric_names)

    if yearly is not None:
      for year in yearly:
        accumulate_contributor_metrics(yearly[year])
        filter_metrics(yearly[year], metric_names)

    if monthly is not None:
      for month in monthly:
        accumulate_contributor_metrics(monthly[month])
        filter_metrics(monthly[month], metric_names)

    if weekly is not None:
      for week in weekly:
        accumulate_contributor_metrics(weekly[week])
        filter_metrics(weekly[week], metric_names)

    if daily is not None:
      for day in daily:
        accumulate_contributor_metrics(daily[day])
        filter_metrics(daily[day], metric_names)

    return metrics


def get_precision(name, metrics, metrics_precisions):
  if name not in metrics_precisions:
    del metrics[name]
    return None
  return metrics[name]


def filter_metrics(accumulator, metric_names):
  if 'contributor_stats' in accumulator:
    for contributor in accumulator['contributor_stats']:
      filter_metrics(accumulator['contributor_stats'][contributor], metric_names)

  def remove_key(key):
    del accumulator[key]

  map(remove_key, filter(lambda key: key not in metric_names, accumulator.keys()))


def accumulate_contributor_metrics(accumulator):

  contributor_docs_list = accumulator['contributor_docs_list']
  contributor_only_docs_list = accumulator['contributor_only_docs_list']
  contributor_code_list = accumulator['contributor_code_list']
  contributor_only_code_list = accumulator['contributor_only_code_list']

  for contributor_key in accumulator['contributor_stats'].keys():
    contributor_metrics = accumulator['contributor_stats'][contributor_key]

    if contributor_metrics['docs_count'] > 0:
      contributor_docs_list.append(contributor_key)
      if contributor_metrics['code_count'] == 0:
        contributor_only_docs_list.append(contributor_key)

    if contributor_metrics['code_count'] > 0:
      contributor_code_list.append(contributor_key)
      if contributor_metrics['docs_count'] == 0:
        contributor_only_code_list.append(contributor_key)

    accumulator['contributor_count'] = len(accumulator['contributor_stats'].keys())
    accumulator['contributor_docs_count'] = len(contributor_docs_list)
    accumulator['contributor_code_count'] = len(contributor_code_list)
    accumulator['contributor_only_docs_count'] = len(contributor_only_docs_list)
    accumulator['contributor_only_code_count'] = len(contributor_only_code_list)


def accumulate_metrics(accumulator, sample, contributor):
  # commit counts
  accumulator['commit_count'] += sample['commit_count']
  accumulator['code_count'] += sample['code_count']
  accumulator['docs_count'] += sample['docs_count']
  accumulator['only_code_count'] += sample['only_code_count']
  accumulator['only_docs_count'] += sample['only_docs_count']
  accumulator['chars_changed_count'] += sample['chars_changed_count']
  accumulator['code_chars_count'] += sample['code_chars_count']
  accumulator['docs_chars_count'] += sample['docs_chars_count']

  # throw out 1.0 values for max
  if accumulator['docs_density_max'] < sample['docs_density_max'] and sample['docs_density_max'] != 1.0:
    accumulator['docs_density_max'] = sample['docs_density_max']

  # throw out 0.0 values for min
  if (accumulator['docs_density_min'] == 0.0 or (accumulator['docs_density_min'] > sample['docs_density_min'] and sample['docs_density_min'] != 0.0)):
    accumulator['docs_density_min'] = sample['docs_density_min']

  accumulator['docs_density_avg'] = (
    accumulator['commit_count'] * accumulator['docs_density_avg'] + sample['docs_density_avg']
    ) / (accumulator['commit_count'] + 1)

  # throw out 1.0 values for max
  if accumulator['code_density_max'] < sample['code_density_max'] and sample['code_density_max'] != 1.0:
    accumulator['code_density_max'] = sample['code_density_max']

  # throw out 0.0 values for min
  if (accumulator['code_density_min'] == 0.0 or (accumulator['code_density_min'] > sample['code_density_min'] and sample['code_density_min'] != 0.0)):
    accumulator['code_density_min'] = sample['code_density_min']

  accumulator['code_density_avg'] = (
    accumulator['commit_count'] * accumulator['code_density_avg'] + sample['code_density_avg']
    ) / (accumulator['commit_count'] + 1)

  # keep all positive values for max, since we can exceed 1.0 for this measure
  if accumulator['docs_to_code_max'] < sample['docs_to_code_max']:
    accumulator['docs_to_code_max'] = sample['docs_to_code_max']

  # throw out 0.0 values for min
  if (accumulator['docs_to_code_min'] == 0.0 or (accumulator['docs_to_code_min'] > sample['docs_to_code_min'] and sample['docs_to_code_min'] != 0.0)):
    accumulator['docs_to_code_min'] = sample['docs_to_code_min']

  accumulator['docs_to_code_avg'] = (
    accumulator['commit_count'] * accumulator['docs_to_code_avg'] + sample['docs_to_code_avg']
    ) / (accumulator['commit_count'] + 1)

  # contributor stats
  if 'contributor_stats' in accumulator:
    contributors = accumulator['contributor_stats']
    if not contributor in contributors:
      contributors[contributor] = copy.deepcopy(codewerdz.git.metrics.EMPTY_CONTRIBUTOR_METRICS)

    accumulate_metrics(contributors[contributor], sample, None)


class UTC(datetime.tzinfo):
  """UTC"""

  def utcoffset(self, dt):
    return datetime.timedelta(0)

  def tzname(self, dt):
    return "UTC"

  def dst(self, dt):
    return datetime.timedelta(0)


def parse_git_iso(isodate_string):
  # eg: 2017-05-13 17:22:39 -0700
  return iso8601.parse_date(isodate_string.replace(" -", "-").replace(" +", "+"))


def week_of_year(isodate_string):
  """ NOTE: Not ISO week number... TODO, decide if we care about this or not... """
  date = parse_git_iso(isodate_string)
  return ((date - datetime.datetime(date.year, 1, 1, tzinfo=UTC())).days // 7) + 1


def day_of_year(isodate_string):
  date = parse_git_iso(isodate_string)
  return date.timetuple().tm_yday


def month_of_year(isodate_string):
  date = parse_git_iso(isodate_string)
  return date.timetuple().tm_mon
