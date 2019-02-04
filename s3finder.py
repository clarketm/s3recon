import datetime
import warnings
from asyncio import get_event_loop, gather
from collections import defaultdict, Mapping
from copy import deepcopy
from functools import reduce
from random import choice

import requests
import yaml
from urllib3.exceptions import InsecureRequestWarning

from constants import (
    useragent_list,
    format_list,
    env_list,
    region_list,
    sep_list,
    word_list,
    public_key,
    private_key,
    public_text,
    private_text,
)

warnings.filterwarnings("ignore", category=InsecureRequestWarning)


def bucket_exists(url, useragent):
    exists = False
    public = False

    try:
        res = requests.head(url, headers={"User-Agent": useragent}, verify=False, timeout=30)
        # TODO: handle redirects
        status_code = res.status_code
        exists = status_code != 404
        public = status_code == 200
    except Exception as e:
        # print(e, end="\n")
        pass

    return exists, public


def find_bucket(url, useragent):
    exists, public = bucket_exists(url, useragent)

    if exists:
        access = public_key if public else private_key
        access_word = public_text if public else private_text
        print(f"{access} {access_word} {url}", end="\n")
        return access, url

    return None


def collect_results(r):
    d = defaultdict(list)
    for access, url in filter(bool, r):
        d[access].append(url)

    return d.get("-", []), d.get("+", [])


def read_config():
    from pathlib import Path
    config = {}

    config_hierarchy = [
        Path(Path.home(), 's3finder.yaml'),
        Path(Path.home(), 's3finder.yml'),
        Path(Path.cwd(), 's3finder.yaml'),
        Path(Path.cwd(), 's3finder.yml'),
    ]

    for c in config_hierarchy:
        try:
            c = yaml.load(open(c, "r"))
            deepmerge(config, c)
        except Exception as e:
            pass

    return config

def deepmerge(target, *sources):
    """
    :param target:
    :param *sources:
    """

    def _deepmerge(target, source):
        """
        :param target:
        :param source:
        """
        for key in source:
            if key in target:
                if isinstance(target[key], Mapping) and isinstance(
                        source[key], Mapping
                ):
                    # If the key for both `target` and `source` are Mapping types, then recurse.
                    _deepmerge(target[key], source[key])
                elif target[key] == source[key]:
                    # If a key exists in both objects and the values are `same`, the value from the `target` object will be used.
                    pass
                else:
                    # If a key exists in both objects and the values are `different`, the value from the `source` object will be used.
                    target[key] = deepcopy(source[key])
            else:
                # If the key exists only in `source`, the value from the `source` object will be used.
                target[key] = deepcopy(source[key])
        return target

    return reduce(_deepmerge, sources, target)


def main(envs, formats, regions, seps, useragents, words):
    start = datetime.datetime.now()
    loop = get_event_loop()

    url_list = {
        f.format(region=region, word=word, sep=sep if env else "", env=env)
        for f in formats
        for region in regions
        for word in words
        for sep in seps
        for env in envs
    }

    r = loop.run_until_complete(
        gather(*[loop.run_in_executor(None, find_bucket, url, choice(useragents)) for url in url_list])
    )

    private, public = collect_results(r)
    total = len(url_list)
    hits = len(private) + len(public)
    stop = datetime.datetime.now()


def cli():
    import argparse

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=35, width=100),
    )
    parser.add_argument("-e", "--envs", metavar="file", default=env_list, help="env list")
    parser.add_argument("-f", "--formats", metavar="file", default=format_list, help="format list")
    parser.add_argument("-r", "--regions", metavar="file", default=region_list, help="region list")
    parser.add_argument("-s", "--seps", metavar="file", default=sep_list, help="separator list")
    parser.add_argument("-u", "--useragents", metavar="file", default=useragent_list, help="useragent list")
    parser.add_argument("-w", "--words", metavar="file", default=word_list, help="word list")

    main(**vars(parser.parse_args()))


if __name__ == "__main__":
    # cli()
    c = read_config()
    print(c)
