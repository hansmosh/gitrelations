"""gitrelations

Get number of times two files are in the same git commit
"""
import sys
import subprocess
from collections import defaultdict


IGNORE_FILE_LIST = [
    ".eslintignore",
    "yarn.lock",
    "package.json",
]


def main():
    """Script entrypoint

    Usage: gitrelations <filename>
    """
    filename = sys.argv[1]
    git_filename = _git_filename(filename)
    relations = _relations()
    _print_results(relations[git_filename])


def _print_results(tofiles):
    """Print git relations in human readable form"""
    sortable = []
    for filename, count in tofiles.items():
        sortable.append((count, filename))
    sortable.sort(reverse=True)
    for count, tofile in sortable[:10]:
        print("  {}  {}".format(count, tofile))


def _relations():
    """Get number of times two files are in the same git commit

    Returns:
        - dict(dict(int))): for each file, a key with each other file that has
          shared a git commit and the number of times.
    """
    relations = defaultdict(lambda: defaultdict(int))
    for i in range(100):
        git_command = ("git diff-tree --no-commit-id --name-only -r "
                       "HEAD{}..HEAD{}".format("^"*(i+1), "^"*i))
        process = subprocess.Popen(git_command.split(), stdout=subprocess.PIPE)
        output = [filename for filename in
                  process.communicate()[0].decode().split('\n') if filename]
        if not output:
            # fix: break on last commit, not just any commit with nothing
            break
        for fromfile in output:
            for tofile in output:
                if fromfile != tofile and tofile not in IGNORE_FILE_LIST:
                    relations[fromfile][tofile] += 1
    return relations


def _git_filename(filename):
    """Get a files full git path"""
    git_command = ("git ls-tree --full-name --name-only HEAD "
                   "{}".format(filename))
    process = subprocess.Popen(git_command.split(), stdout=subprocess.PIPE)
    return process.communicate()[0].decode().split('\n')[0]


if __name__ == "__main__":
    main()
