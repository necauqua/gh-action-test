
import yaml, sys, os

from datetime import datetime

date_format = '1%F'
tag_format = '[{tag}] {date}'
unreleased_header = 'Unreleased'


def section(header, log):
    s = f'## {header}\n'
    for key in sorted(log.keys()):
        s += f'### {key.capitalize()}\n'
        for item in log[key]:
            s += f'  - {item}\n'
    return s + '\n'


def main():
    folder = os.path.dirname(os.path.realpath(__file__))
    with open(folder + '/changelog-template.md') as f:
        data = yaml.safe_load(sys.stdin.read())

        log = data['unreleased']
        s = ''
        if log:
            s += section(unreleased_header, log)

        for release in data['released']:
            tag, data = next(iter(release.items()))
            date, log = data['date'], data['log']
            date = datetime.utcfromtimestamp(date).strftime(date_format)
            if log:
                s += section(tag_format.format(tag=tag, date=date), log)

        print(f.read().format(changelog=s.strip()))

if __name__ == '__main__':
    main()

