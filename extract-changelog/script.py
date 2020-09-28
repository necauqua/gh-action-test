#!/usr/bin/python

import sys, subprocess

def git(args):
    _args = ['git']
    _args.extend(args.split(' '))
    return subprocess.run(_args, capture_output=True) \
               .stdout \
               .decode('utf-8') \
               .strip() \
               .split('\n')


def parse_log(start_ref=None, end_ref=None):
    cmd = 'log --reverse --format=%b'
    if start_ref:
        cmd += ' ' + start_ref
    if end_ref:
        cmd += ' ^' + end_ref
    log = {}
    current = []
    for line in git(cmd):
        if line.endswith(':'):
            line = line[:-1].lower()
            if line not in log:
                log[line] = []
            current = log[line]
        elif line.startswith('  - '):
            current.append(line[4:])
    return log


def format_log(log, indent=''):
    s = ''
    for section, items in log.items():
        s += f'{indent}{section}:\n'
        for item in items:
            item = item.replace('\'', '\'\'')
            s += f'{indent}- \'{item}\'\n'
    return s[:-1]


def main():
    filename = len(sys.argv) > 1 and sys.argv[1] or 'changelog.yml'
    root_commit = len(sys.argv) > 2 and sys.argv[2]

    cmd = f'for-each-ref --sort=-creatordate --format %(refname)|%(creatordate:unix) refs/tags'
    if root_commit:
        cmd += ' --contains ' + root_commit
    tags = git(cmd)

    with open(filename, 'w') as f:
        f.write('--- # Changelog\n')

        # no tags -> everything is unreleased
        if tags == ['']:
            log = parse_log('HEAD', root_commit) # the whole log
            if log:
                f.write('unreleased:\n' + format_log(log, '  ') + '\n')
            else:
                f.write('unreleased: {}\n')
            f.write('released: {}\n') # and then we have no tags
            return

        last_tag, last_date = tags.pop(0).split('|')

        unreleased = parse_log('HEAD', last_tag)
        if unreleased != ['']:
            f.write('unreleased:\n' + format_log(unreleased, '  ') + '\n')
        else:
            f.write('unreleased: {}\n')

        tags.append(root_commit and (root_commit + '|'))

        s = ''
        for tag in tags:
            tag, date = tag and tag.split('|') or (None, '')
            log = parse_log(last_tag, tag)

            if not log:
                continue

            s += f'- {last_tag[10:]}:\n    date: {last_date}\n    log:\n' \
                    + format_log(log, '      ') + '\n'

            last_tag = tag
            last_date = date

        if s:
            f.write(f'released: \n{s}')
        else:
            f.write('released: {}\n')

if __name__ == '__main__':
    main()

