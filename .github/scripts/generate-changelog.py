
import subprocess

def git(args):
    _args = ['git']
    _args.extend(args.split(' '))
    return subprocess.run(_args, capture_output=True) \
               .stdout \
               .decode('utf-8') \
               .strip() \
               .split('\n')

sorted_tag_refs = git('for-each-ref --sort=-creatordate --format %(refname) refs/tags')

# the 'root' tag
sorted_tag_refs.append(None)

ranges = []

prev = 'HEAD'
for tag in sorted_tag_refs:
    ranges.append((prev, tag))
    prev = tag

for start, end in ranges:
    log_cmd = 'log --reverse --format=%b ' + start
    if end:
        log_cmd += ' ' + start
    log = git('log --reverse --format=%b ' + start + (end and (' ^' + end) or ''))

    changes = {}
    current = None
    for line in log:
        if line.endswith(':'):
            current = changes.get(line := line[:-1].lower()) or []
            changes[line] = current
        elif line.startswith('  - '):
            current.append(line[4:])

    if start == 'HEAD':
        if changes:
            print('## Unreleased\n')
    else:
        print('\n## [' + start[10:] + ']\n')

    for section, items in changes.items():
        print('### ' + section.capitalize())
        for item in items:
            print('  - ' + item)
        print()

