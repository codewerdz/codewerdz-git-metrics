import fnmatch

import codewerdz.git
from codewerdz.git.log.git_log_process import GitLogProcess

import click
import whatthepatch


class GitLogParser(object):
  def __init__(self, docs_pattern=codewerdz.git.DEFAULT_DOCS_PATTERNS, comments_are_docs=False):
    self.comments_are_docs = comments_are_docs
    self.docs_pattern = docs_pattern

  def parse(self, log_output):
    """
    Parses the structured log output that GitLogCommand produces into commit hashes.
    Output is a iterator of commit hashes.
    A commit hash has the following structure:
    {
      'sha': '<string (7 digit git object id)>',
      'author': '<string>',
      'email': '<string>',
      'date': '<integer> (unix-timestamp)',
      'date_iso': '<string> (iso formatted date)',
      'commit_date': '<integer> (unix-timestamp)',
      'commit_date_iso': '<string> (iso formatted date)',
      'parent': '<string (7 digit git object id)>',
      'tree': '<string (7 digit git object id)>',
      'subject': '<string>',
      // NOTE: This is the output from numstats, which is redundant to the info in
      // diffs list, but sometimes, this is all that is available. Should fix this in the model!
      'stats': [
        { // one hash per file diff!
          'path': '<string (filename)>',
          'del': '<integer> (count of lines)',
          'ins': '<integer> (count of lines)'
        },
        // ...
      ],
      'diffs': [
        { // one hash per file diff!
          'filename': '<string (filename)>',
          "stats": {
            "lines_added": '<integer>',
            "lines_removed": '<integer>',
            "lines_changed": '<integer>',
            "lines_of_code": '<integer>',
            "lines_of_docs": '<integer>',
            "chars_added": '<integer>',
            "chars_removed": '<integer>',
            "chars_changed": '<integer>',
            "chars_of_code": '<integer>',
            "chars_of_docs": '<integer>',
            "is_docfile": '<boolean>'
          },
          'diff_lines': '<string> (all lines of diff, in a single string)'
        }
        // ...
      ]
    }
    """
    commit_lines = []
    for line in log_output:
      if line == GitLogProcess.FORMAT_START_COMMIT:
        if commit_lines:
          commit = self._commit_hash(commit_lines)
          if commit:
            yield commit
        commit_lines = []
      else:
        commit_lines.append(line)
    if commit_lines:
      commit = self._commit_hash(commit_lines)
      if commit:
        yield commit

  def _commit_hash(self, lines):
    lines = dict(enumerate(lines))

    commit = {}

    commit['sha'] = lines.get(GitLogProcess.FORMAT.index(GitLogProcess.FORMAT_SHA))
    if not commit['sha']:
      return None

    commit['author'] = lines.get(GitLogProcess.FORMAT.index(GitLogProcess.FORMAT_AUTHOR))
    commit['email'] = lines.get(GitLogProcess.FORMAT.index(GitLogProcess.FORMAT_EMAIL))
    commit['date'] = lines.get(GitLogProcess.FORMAT.index(GitLogProcess.FORMAT_DATE))
    commit['date_iso'] = lines.get(GitLogProcess.FORMAT.index(GitLogProcess.FORMAT_DATE_ISO))
    commit['commit_date'] = lines.get(GitLogProcess.FORMAT.index(GitLogProcess.FORMAT_COMMIT_DATE))
    commit['commit_date_iso'] = lines.get(GitLogProcess.FORMAT.index(GitLogProcess.FORMAT_COMMIT_DATE_ISO))
    commit['parent'] = lines.get(GitLogProcess.FORMAT.index(GitLogProcess.FORMAT_PARENT))
    commit['tree'] = lines.get(GitLogProcess.FORMAT.index(GitLogProcess.FORMAT_TREE))
    commit['subject'] = lines.get(GitLogProcess.FORMAT.index(GitLogProcess.FORMAT_SUBJECT))
    offset = len(GitLogProcess.FORMAT) + 1

    # commit stats
    numstats = self._slurp_numstats(lines.values()[offset:])
    commit['stats'] = filter(lambda x: " => " not in x['path'], numstats)
    offset += len(numstats) + 1

    # commit diffs
    commit['diffs'] = self._slurp_diffs(lines.values()[offset:])
    return commit

  def _slurp_numstats(self, lines):
    numstats = []

    for line in lines:
      if not line or not (line[0].isdigit() or line[0] == '-'):
        break
      fields = line.split('\t')
      numstats.append(dict(zip(['ins', 'del', 'path'], fields)))

    return numstats

  def _slurp_diffs(self, lines):
    diffs = []
    diff_blob = None
    for line in lines:
      if line.startswith("diff --git "):
        if diff_blob is not None:
          diffs.append(self._parse_diff(diff_blob))
        diff_blob = line
      else:
        diff_blob += "\n" + line

    if diff_blob is not None:
      diffs.append(self._parse_diff(diff_blob))

    return diffs

  def _parse_diff(self, diff_lines):
    filename = self._parse_header_filename(diff_lines)
    changes = whatthepatch.patch.parse_unified_diff(diff_lines)

    stats = {}
    # if changes:
    stats = self.analyze_changes(filename, changes)

    result = {
      'filename': filename,
      'stats': stats,
      'diff_lines': diff_lines
    }
    return result

  def _parse_header_filename(self, diff_lines):
    # this method is largely meant to deal with the bug
    # described in https://github.com/cscorley/whatthepatch/issues/4

    if not diff_lines:
      return ''

    try:
      diff_lines = diff_lines.splitlines()
    except AttributeError:
      pass

    # findall_regex returns an array of indexes where RE matched
    standard_headers = whatthepatch.snippets.findall_regex(
      diff_lines, whatthepatch.patch.git_diffcmd_header)
    # take the first located header and extract the filenames from it
    if not standard_headers:
      # log this so we can debug why certain headers won't parse.
      click.echo('WARNING: Could not parse this header:\n%s\n' % '\n'.join(diff_lines), err=True)
      return ''

    matches = whatthepatch.patch.git_diffcmd_header.match(diff_lines[standard_headers[0]])
    old_filename = matches.group(1)
    new_filename = matches.group(2)
    if new_filename == '/dev/null':
      return old_filename
    return new_filename

  def _is_doc_file(self, filename):
    if not filename:
      return False

    return any([fnmatch.fnmatch(filename, pattern) for pattern in self.docs_pattern])

  def _is_comment(self, change):
    # massage the subject a bit
    if not change:
      return False
    content = (change[2] or '').strip()
    COMMENT_PREFIXES = ["#", "//", "/*", "* ", "*/", "'''", '"""']
    COMMENT_SUFFIXES = ["*/", "'''", '"""']
    return any((
      any(map(content.startswith, COMMENT_PREFIXES)),
      any(map(content.endswith, COMMENT_SUFFIXES))
      ))

  def analyze_changes(self, filename, changes):
    """
    This function analyzes a single set of changes to a file,
    returning a hash of stats derived from those changes.

    This is meant to be overriden/patched by users of this class.

    The default implementation derives the following stats:

    * lines_changed - Total lines changed in the diff
    * lines_added - Total lines added in the diff
    * lines_removed - Total lines removed in the diff
    * lines_of_docs - Total lines of documentation changed in the diff (add/remove)
    * lines_of_code - Total lines of code changed in the diff (add/remove)

    * chars_changed - Total characters changed in the diff
    * chars_added - Total characters added in the diff
    * chars_removed - Total characters removed in the diff
    * chars_of_docs - Total characters of docs changed in the diff (add/remove)
    * chars_of_code - Total characters of code changed in the diff (add/remove)

    * is_docfile - True if the file is a doc file
    """

    lines_added = 0
    lines_removed = 0
    lines_changed = 0
    lines_of_docs = 0
    lines_of_code = 0

    chars_added = 0
    chars_removed = 0
    chars_changed = 0
    chars_of_docs = 0
    chars_of_code = 0

    is_doc_file = self._is_doc_file(filename)

    for change in (changes or []):
      # change is a tuple like (added, deleted, content)
      # where added is the line number of add
      # and deleted is the line number of the delete
      # and content is the affected line
      # if added and deleted are both specified, it's a context line
      # and not part of the actual delta, so should be ignored for
      # stats collection
      if (change[0] is None or change[1] is None) and not (change[0] == change[1]):
        lines_changed += 1
        chars_changed += len(change[2])

        if change[0] is None:
          lines_added += 1
          chars_added += len(change[2])
        elif change[1] is None:
          lines_removed += 1
          chars_removed += len(change[2])

        # This section attempts to determine if a change was code or docs
        # by some basic heuristics. If the filename matches on of the docs_patterns,
        # all lines will be considered docs. For all other files,
        # if comments_are_docs is enabled, we'll check each line, and if the line starts
        # or ends with some common comment characters, we'll consider it docs.
        # There is handling for C-style block comments, but not Python triple-quote style
        # has some problems.
        #
        # This detection system will miss the majority of the body of a block comment
        # in the Python triple quote style. Detection for this could *possibly*
        # be added, by detecting open/close blocks, but would only work for some
        # cases, where an entire contiguous block comment was present in the diff,
        # but since a diff does not always include the full content, if there is a
        # gap of some ommitted lines that were not changed, or included for context
        # it would be impossible to determine if a given line is, or is not within a
        # comment block, as the block could have been closed in an unmodified line
        # which was not included in the diff.

        if (is_doc_file or (self.comments_are_docs and self._is_comment(change))):
          lines_of_docs += 1
          chars_of_docs += len(change[2])
        else:
          lines_of_code += 1
          chars_of_code += len(change[2])

    return {
      'lines_added': lines_added,
      'lines_removed': lines_removed,
      'lines_changed': lines_changed,
      'lines_of_docs': lines_of_docs,
      'lines_of_code': lines_of_code,
      'chars_added': chars_added,
      'chars_removed': chars_removed,
      'chars_changed': chars_changed,
      'chars_of_docs': chars_of_docs,
      'chars_of_code': chars_of_code,
      'is_docfile': is_doc_file
    }
