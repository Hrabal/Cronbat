# !/usr/bin/env python

#   Copyright 2018 Federico Cerchiari <federicocerchiari@gmail.com>
#
#   this file is part of CronBat
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from setuptools import setup

from cronbat import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name="cronbat",
    version=__version__,
    author="Federico Cerchiari",
    author_email="federicocerchiari@gmail.com",
    description="Cron manager and analyzer.",
    license="APACHE 2.0",
    packages=["cronbat"],
    url="https://github.com/Hrabal/Cronbat",
    keywords=["python3", "cron", "crontab", "utility", "sysadmin", "unix"],
    download_url="https://github.com/Hrabal/Cronbat/archive/%s.tar.gz" % __version__,
    python_requires=">=3.3",
    install_requires=["classcli"],
    long_description=long_description,
)
