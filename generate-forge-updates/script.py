
import urllib.request, yaml, json, sys, re, os

def read_all(filename):
    with open(filename) as f:
        return f.read()


def get_versions():
    with urllib.request.urlopen('https://launchermeta.mojang.com/mc/game/version_manifest.json') as url:
        data = json.loads(url.read().decode())
        res = []
        for v in data['versions']:
            if v['type'] == 'release':
                version = v['id']
                if version.count('.') == 1:
                    version += '.0'
                res.append(version)
        return res


def section(log):
    s = ''
    for key in sorted(log.keys()):
        s += f'### {key.capitalize()}\n'
        for item in log[key]:
            s += f'  - {item}\n'
    return s + '\n'


def main():
    changelog = os.getenv('INPUT_CHANGELOG')
    template = os.getenv('INPUT_TEMPLATE')
    filename = os.getenv('INPUT_FILENAME')

    result = template and json.loads(read_all(template)) or {}

    version_format = re.compile('v([0-9.]+)-([a-z0-9.-]+)')

    versions = get_versions()

    changelog = yaml.safe_load(read_all(changelog))
    unreleased, released = changelog['unreleased'], changelog['released']

    recomended = {}

    for release in released:
        version, log = next(iter(release.items()))
        if match := version_format.match(version):
            mcversion, modversion = match.groups()
            for v in versions:
                if v.startswith(mcversion):
                    if v.endswith('.0'):
                        v = v[:-2]

                    if not v in recomended:
                        recomended[v] = modversion

                    if not v in result:
                        result[v] = {}

                    result[v][modversion] = section(log['log'])[:-1]
    
    if not 'promos' in result:
        result['promos'] = {}

    promos = result['promos']

    for mcversion, modversion in recomended.items():
        promos[f'{mcversion}-recommended'] = modversion
        promos[f'{mcversion}-latest'] = modversion

    with open(filename, 'w') as f:
        json.dump(result, f)
        f.write('\n')

if __name__ == '__main__':
    main()

