
import yaml, sys, os

from datetime import datetime


def section(header, log):
    s = f'## {header}\n'
    for key in sorted(log.keys()):
        s += f'### {key.capitalize()}\n'
        for item in log[key]:
            s += f'  - {item}\n'
    return s + '\n'


def read_all(filename):
    with open(filename) as f:
        return f.read()


def main():
    changelog_file, tag_format, date_format, unreleased_header, filename = sys.argv[1:6]
    template_file = len(sys.argv) > 5 and sys.argv[6]

    template = template_file and read_all(template_file) or '{changelog}'
    changelog = read_all(changelog_file)

    data = yaml.safe_load(changelog)

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

    with open(filename, 'w') as f:
        f.write(template.format(changelog=s[:-1]))

if __name__ == '__main__':
    main()

