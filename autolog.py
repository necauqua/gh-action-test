
import subprocess

latest_tag = subprocess.run(['git', 'describe', '--abbrev=0'], capture_output=True) \
                .stdout \
                .decode('utf-8') \
                .strip()

log_cmd = ['git', 'log', '--reverse', '--format=%b']

if latest_tag:
    log_cmd.extend(['HEAD', '^' + latest_tag])

log = subprocess.run(log_cmd, capture_output=True) \
        .stdout \
        .decode('utf-8') \
        .split('\n')

changes = {}
current = None
for line in log:
    if line.endswith(':'):
        current = changes.get(line := line[:-1].lower()) or []
        changes[line] = current
    elif line.startswith('  - '):
        current.append(line[4:])

for section, items in changes.items():
    print('### ' + section.capitalize())
    for item in items:
        print('  - ' + item)
    print()

