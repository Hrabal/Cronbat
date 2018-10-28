import os
import re
import editor
import subprocess
from copy import copy

EDITOR = os.environ.get('EDITOR', 'vim')


class Cron:

    def __init__(self):
        self._crontab = self._get_crontab()
        self.crons = {}
        self.read_crontab()

    def _get_crontab(self):
        return subprocess.check_output(['crontab', '-l']).decode('utf-8')

    def _write_crontab(self, cron_str):
        return subprocess.check_output(['echo', f'"{cron_str}"', '|', 'crontab', '-'])

    def read_crontab(self):
        section = ['main', ]
        for cron_line in self._crontab.split('\n'):
            if cron_line.startswith('# CRONBAT'):
                section = ''.join(cron_line.split()[2:-1]).split(':')
            else:
                self._add_cron_instruction(section, cron_line)

    def _add_cron_instruction(self, key_path: list, cron_str: str):
        if cron_str:
            el = self.crons
            key_path = copy(key_path)
            while key_path:
                k = key_path.pop(0)
                el.setdefault(k, {})
                el[k].setdefault('jobs', [])
                if not key_path:
                    el[k]['jobs'].append(Job(cron_str))
                el = el[k]

    def _yield_crons(self, crondict: dict=None, parents: list=None):
        source = copy(crondict or self.crons)
        parents = parents or []
        for name, section in source.items():
            yield '# CRONBAT %s CRONBAT' % ':'.join(parents + [name, ]), section
            if section:
                parents.append(name)
                yield from self._yield_crons(section, parents=parents)
            parents = []

    def dump_cron(self):
        cron_str = '\n\n'.join('%s\n%s' % (
            name,
            self._dump_section(cron)
        ) for name, cron in self._yield_crons())
        self._write_crontab(cron_str)

    def _dump_section(self, section: list):
        return '\n'.join(job.str for job in section.get('jobs', []))

    def edit_section(self, path):
        container = self.crons
        for k in path:
            container = container.get(k, {})
        edit_result = editor.edit(contents=self._dump_section(container).encode('utf-8'))
        container['jobs'] = []
        for line in edit_result.decode('utf-8').split('\n'):
            self._add_cron_instruction(path, line)


class Job:
    CRONRE = re.compile(r'^\s*([^@#\s]+)\s+([^@#\s]+)\s+([^@#\s]+)\s+([^@#\s]+)'
                        r'\s+([^@#\s]+)\s+([^\n]*?)(\s+#\s*([^\n]*)|$)')

    def __init__(self, cron_str: str):
        self.str = cron_str
        self._minute = self._hour = self._day = self._month = self._weekday = self.what = None
        self._is_comment = False
        self.read_cronjob(self.str)

    @property
    def when(self):
        return f'{self._minute} {self._hour} {self._day} {self._month} {self._weekday}'

    def read_cronjob(self, cron_str: str):
        if cron_str.startswith('#'):
            self._is_comment = True
        else:
            items = self.CRONRE.findall(cron_str)
            for i, part in enumerate(('_minute', '_hour', '_day', '_month', '_weekday')):
                setattr(self, part, Frequency(items[0][i], part))
            self.what = ' ' .join(i for i in items[0][5:] if i)
            return self

    def __repr__(self):
        return f'{self.when} {self.what}' if not self._is_comment else self.str


class Frequency:
    PARTS = {
        '_minute': (0, 59),
        '_hour': (0, 23),
        '_day': (1, 31),
        '_month': (1, 12),
        '_weekday': (0, 6)
    }

    def __init__(self, when_str: str, typ):
        self.str = when_str
        self.occurencies = list(self.parse(when_str, typ))

    @classmethod
    def parse(self, when_str: str, typ: str):
        min_r, max_r = self.PARTS[typ]
        if ',' in when_str:
            return map(int, when_str.split(','))
        elif '-' in when_str:
            min_r, max_r = map(int, when_str.split('-'))
            return range(min_r, max_r + 1)
        elif '/' in when_str:
            return range(min_r, max_r + 1, int(when_str[-1]))
        elif when_str == '*':
            return range(min_r, max_r + 1)

    def __repr__(self):
        return self.str
