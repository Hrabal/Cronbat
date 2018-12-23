# -*- coding: utf-8 -*-
import os
import re
import editor
import subprocess
from pathlib import Path
from copy import copy

from sty import fg, rs

EDITOR = os.environ.get("EDITOR", "vim")


class CronDumper:
    _temp_cronbat = Path(".tempcronbat")

    def _write_crontab(self, cron_str):
        print("Writing to cron...", end=" ")
        if not cron_str:
            command = ["crontab", "-r"]
        else:
            self._temp_cronbat.write_text(cron_str)
            command = ["crontab", self._temp_cronbat]
        try:
            subprocess.check_output(command, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            if "crontab: no crontab" in e.output.decode():
                pass
            else:
                raise RuntimeError(
                    f"command '{e.cmd}' return with error (code {e.returncode}): {e.output}"
                )
        else:
            if self._temp_cronbat.exists():
                self._temp_cronbat.unlink()
        print("done.")

    def _prettify_cron(self, cron_line: str, pretty: bool = False):
        if not pretty:
            return cron_line
        if cron_line.startswith(self.CRONBAT_DELIMITER):
            line = cron_line.split("CRONBAT")
            name_parts = " ".join(line[1:-1]).split(":")
            depth = len(name_parts)
            name_parts = " => ".join(name_parts)
            return f'{fg.green}{"####" * depth}{fg.yellow}{name_parts}{rs.fg}'
        return cron_line

    def dump_cron(
        self, to_cron: bool = True, pretty: bool = False, section: str = None
    ):
        if not self.crons:
            cron_str = ""
        else:
            cron_str = "\n\n".join(
                "%s\n%s"
                % (
                    self._prettify_cron(name, pretty=pretty),
                    self._prettify_cron(self._dump_section(cron), pretty=pretty),
                )
                for name, cron in self._yield_crons(s_filter=section)
            )
        if to_cron:
            self._write_crontab(cron_str)
        return cron_str

    def _dump_section(self, section: list):
        return "\n".join(job.str for job in section.get("_jobs", []))


class Cron(CronDumper):
    CRONBAT_DELIMITER = "# CRONBAT"

    def __init__(self):
        self._crontab = self._get_crontab()
        self.crons = {}
        self.read_crontab()

    def _get_crontab(self):
        try:
            return subprocess.check_output(
                ["crontab", "-l"], stderr=subprocess.STDOUT
            ).decode("utf-8")
        except subprocess.CalledProcessError:
            return ""

    def read_crontab(self):
        section = ["main"]
        for cron_line in self._crontab.split("\n"):
            if cron_line.startswith(self.CRONBAT_DELIMITER):
                section = "".join(cron_line.split()[2:-1]).split(":")
            else:
                self._add_cron_instruction(section, cron_line)

    def _add_cron_instruction(self, key_path: list, cron_str: str):
        if cron_str:
            el = self.crons
            key_path = copy(key_path)
            while key_path:
                k = key_path.pop(0)
                el.setdefault(k, {})
                el[k].setdefault("_jobs", [])
                if not key_path:
                    el[k]["_jobs"].append(Job(cron_str))
                el = el[k]

    def _yield_crons(
        self, crondict: dict = None, parents: list = None, s_filter: str = None
    ):
        source = copy(crondict or self.crons)
        parents = parents or []
        for name, section in source.items():
            if name != "_jobs":
                if not s_filter or s_filter == name or s_filter in parents:
                    sect_name = ":".join(parents + [name])
                    cron_repr = f"{self.CRONBAT_DELIMITER} {sect_name} CRONBAT"
                    yield cron_repr, section
                if section:
                    parents.append(name)
                    yield from self._yield_crons(
                        section, parents=parents, s_filter=s_filter
                    )
                parents = []

    def edit_section(self, path: list = None):
        path = path or []
        container = self.crons
        for k in path:
            container = container.get(k, {})
        section_str = "\n".join(
            self._dump_section(c) for c in self._yield_crons(container)
        ).encode("utf-8")
        edit_result = editor.edit(contents=section_str)
        container["_jobs"] = []
        for line in edit_result.decode("utf-8").split("\n"):
            print(f"CRONLINE: {line}")
            self._add_cron_instruction(path, line)
        from pprint import pprint

        pprint(self.crons)

    def _r(self):
        self.crons = {}
        self.dump_cron()


class Job:
    CRONRE = re.compile(
        r"^\s*([^@#\s]+)\s+([^@#\s]+)\s+([^@#\s]+)\s+([^@#\s]+)"
        r"\s+([^@#\s]+)\s+([^\n]*?)(\s+#\s*([^\n]*)|$)"
    )

    def __init__(self, cron_str: str):
        self.str = cron_str
        self._minute = (
            self._hour
        ) = self._day = self._month = self._weekday = self.what = None
        self._is_comment = False
        self.read_cronjob(self.str)

    @property
    def when(self):
        return f"{self._minute} {self._hour} {self._day} {self._month} {self._weekday}"

    def read_cronjob(self, cron_str: str):
        if cron_str.startswith("#"):
            self._is_comment = True
        else:
            items = self.CRONRE.findall(cron_str)
            for i, part in enumerate(
                ("_minute", "_hour", "_day", "_month", "_weekday")
            ):
                setattr(self, part, Frequency(items[0][i], part))
            self.what = " ".join(i for i in items[0][5:] if i)
            return self

    def __repr__(self):
        return f"{self.when} {self.what}" if not self._is_comment else self.str


class Frequency:
    PARTS = {
        "_minute": (0, 59),
        "_hour": (0, 23),
        "_day": (1, 31),
        "_month": (1, 12),
        "_weekday": (0, 6),
    }

    def __init__(self, when_str: str, typ):
        self.str = when_str
        self.occurencies = list(self.parse(when_str, typ))

    @classmethod
    def parse(self, when_str: str, typ: str):
        min_r, max_r = self.PARTS[typ]
        if "," in when_str:
            return map(int, when_str.split(","))
        elif "-" in when_str:
            min_r, max_r = map(int, when_str.split("-"))
            return range(min_r, max_r + 1)
        elif "/" in when_str:
            return range(min_r, max_r + 1, int(when_str[-1]))
        elif when_str == "*":
            return range(min_r, max_r + 1)

    def __repr__(self):
        return self.str
