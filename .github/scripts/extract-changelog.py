
import subprocess

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
    for section, items in log.items():
        print(f'{indent}{section}:')
        for item in items:
            item = item.replace('\'', '\'\'')
            print(f'{indent}- \'{item}\'')


def main():
    tags = git(f'for-each-ref --sort=-creatordate --format %(refname)|%(creatordate:unix) refs/tags')

    print('--- # Changelog')

    # no tags -> everything is unreleased
    if not tags:
        log = parse_log() # the whole log
        if log != ['']:
            print('unreleased:')
            format_log(log, '  ')
        else:
            print('unreleased: {}')
        print('released: {}') # and then we have no tags
        return

    last_tag, last_date = tags.pop(0).split('|')

    unreleased = parse_log('HEAD', last_tag)
    if unreleased != ['']:
        print('unreleased:')
        format_log(unreleased, '  ')
    else:
        print('unreleased: {}')

    print('released:')
    tags.append(None)

    for tag in tags:
        tag, date = tag and tag.split('|') or (None, None)
        log = parse_log(last_tag, tag)

        if not log:
            continue

        print(f'- {last_tag[10:]}:\n    date: {last_date}\n    log:')
        
        format_log(log, '      ')
        
        last_tag = tag
        last_date = date

if __name__ == '__main__':
    main()

