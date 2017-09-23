import re

from codewerdz.git.process.git_process import GitProcess

import whatthepatch

# monkeypatch whatthepatch regex
whatthepatch.patch.git_diffcmd_header = re.compile('^diff --git "?a/(.+)"? "?b/(.+)"?$')


class GitLogProcess(GitProcess):

  FORMAT_START_COMMIT = '@@@@@@@@@@'
  FORMAT_SHA = "%h"
  FORMAT_AUTHOR = "%aN"
  FORMAT_EMAIL = "%aE"
  FORMAT_DATE = "%at"
  FORMAT_DATE_ISO = "%ai"
  FORMAT_COMMIT_DATE = "%ct"
  FORMAT_COMMIT_DATE_ISO = "%ci"
  FORMAT_PARENT = "%p"
  FORMAT_TREE = "%t"
  FORMAT_SUBJECT = "%s"

  FORMAT = [
    FORMAT_SHA,
    FORMAT_AUTHOR,
    FORMAT_EMAIL,
    FORMAT_DATE,
    FORMAT_DATE_ISO,
    FORMAT_COMMIT_DATE,
    FORMAT_COMMIT_DATE_ISO,
    FORMAT_PARENT,
    FORMAT_TREE,
    FORMAT_SUBJECT
  ]

  FORMAT_STRING = "%n".join([FORMAT_START_COMMIT] + FORMAT)

  def __init__(self, since=None, until=None, limit=None, excluded_paths=None):
    params = []
    if since:
      params += ['--since=' + since]

    if until:
      params += ['--until=' + until]

    if limit:
      params += ['--max-count=' + str(limit)]

    params += [
      '--pretty=tformat:' + self.FORMAT_STRING,
      '--date=local', '--numstat', '--no-merges',
      '--follow', '-p', '--', '.'
    ]

    if excluded_paths:
      params += [":(exclude)%s" % path for path in excluded_paths]

    self.params = params
    GitProcess.__init__(self)

  def get_lines(self):
    return super(GitLogProcess, self).get_lines("log", self.params)
