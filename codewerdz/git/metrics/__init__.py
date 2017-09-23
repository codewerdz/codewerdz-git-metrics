import copy

EMPTY_REPO_METRICS = {
  'contributor_count': 0,
  'contributor_docs_count': 0,
  'contributor_code_count': 0,
  'contributor_docs_list': [],
  'contributor_code_list': [],
  'contributor_only_docs_count': 0,
  'contributor_only_code_count': 0,
  'contributor_only_docs_list': [],
  'contributor_only_code_list': [],
  'contributor_stats': {}
}

EMPTY_CONTRIBUTOR_METRICS = {
  "commit_count": 0,
  "chars_changed_count": 0,

  "code_count": 0,
  "docs_count": 0,

  "only_code_count": 0,
  "only_docs_count": 0,

  "code_chars_count": 0,
  "docs_chars_count": 0,

  "docs_density_avg": 0.0,
  "docs_density_max": 0.0,
  "docs_density_min": 0.0,

  "code_density_avg": 0.0,
  "code_density_max": 0.0,
  "code_density_min": 0.0,

  "docs_to_code_avg": 0.0,
  "docs_to_code_max": 0.0,
  "docs_to_code_min": 0.0,

  # 'commit_docs_dwell_avg': 0,
  # 'commit_docs_dwell_max': 0,
  # 'commit_docs_dwell_min': 0,
  # 'commit_code_dwell_avg': 0,
  # 'commit_code_dwell_max': 0,
  # 'commit_code_dwell_min': 0,
  # 'commit_docs_velocity': 0.0,
  # 'commit_docs_inertia': 0.0,
  # 'commit_docs_drift': 0,
}

EMPTY_REPO_METRICS.update(EMPTY_CONTRIBUTOR_METRICS)

DEFAULT_METRICS = METRICS_CHOICES = EMPTY_REPO_METRICS.keys()

EMPTY_METRICS_PRECISIONS = {
  'total': copy.deepcopy(EMPTY_REPO_METRICS),
  'yearly': {},
  'monthly': {},
  'weekly': {},
  'daily': {}
}

DEFAULT_PRECISION = PRECISION_CHOICES = EMPTY_METRICS_PRECISIONS.keys()
