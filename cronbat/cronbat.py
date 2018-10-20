import re
import subprocess


class Job:
    CRONRE = re.compile(r'^\s*([^@#\s]+)\s+([^@#\s]+)\s+([^@#\s]+)\s+([^@#\s]+)'
                        r'\s+([^@#\s]+)\s+([^\n]*?)(\s+#\s*([^\n]*)|$)')

    def __init__(self, cron_str: str):
        self.str = cron_str
        self._minute = self._hour = self._day = self._month = self._weekday = self.what = None
        self.read_cronjob(self.str)

    @property
    def when(self):
        return f'{self._minute} {self._hour} {self._day} {self._month} {self._weekday}'

    def read_cronjob(self, cron_str: str):
        items = self.CRONRE.findall(cron_str)
        self._minute, self._hour, self._day, self._month, self._weekday = items[0][:5]
        self.what = ' ' .join(i for i in items[0][5:] if i)
        return self

    def __repr__(self):
        return f'{self.when} | {self.what}'


class Cron:

    def __init__(self):
        self._crontab = subprocess.check_output(['crontab', '-l']).decode('utf-8')
        self.crons = {}
        self.read_crontab()

    def read_crontab(self):
        section = ['main', ]
        for cron_line in self._crontab.split('\n'):
            if cron_line.startswith('# CRONBAT'):
                section = ''.join(cron_line.split()[2:-2]).split(':')
            else:
                self._update_cron_section(section, cron_line)

    def _update_cron_section(self, key_path: list, cron_str: str):
        if cron_str:
            el = self.crons
            while key_path:
                k = key_path.pop(0)
                el.setdefault(k, {})
                el[k].setdefault('jobs', [])
                if not key_path:
                    el[k]['jobs'].append(Job(cron_str))
                el = el[k]
