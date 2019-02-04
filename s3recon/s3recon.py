#!/usr/bin/env python3

from asyncio import get_event_loop, gather
from collections import defaultdict
from datetime import datetime
from json import dumps
from os import environ
from pathlib import Path
from random import choice
from sys import stdout, path
from warnings import filterwarnings

import requests
from mergedeep import merge
from urllib3.exceptions import InsecureRequestWarning
from yaml import load

if not __package__:
    path.insert(0, str(Path(Path(__file__).parent.parent.parent)))


from s3recon.constants import (
    useragent_list,
    format_list,
    public_key,
    private_key,
    public_text,
    private_text,
)

filterwarnings("ignore", category=InsecureRequestWarning)


def bucket_exists(url, timeout):
    exists = False
    public = False

    try:
        res = requests.head(
            url,
            headers={"User-Agent": choice(useragent_list)},
            verify=False,
            timeout=timeout,
        )
        # TODO: handle redirects
        status_code = res.status_code
        exists = status_code != 404
        public = status_code == 200
    except Exception:
        pass

    return exists, public


def find_bucket(url, timeout):
    exists, public = bucket_exists(url, timeout)

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
    config = {}

    config_hierarchy = [
        Path(Path(__file__).parent, "s3recon.yml"),  # default
        Path(Path.home(), "s3recon.yaml"),
        Path(Path.home(), "s3recon.yml"),
        Path(Path.cwd(), "s3recon.yaml"),
        Path(Path.cwd(), "s3recon.yml"),
        Path(environ.get("S3RECON_CONFIG") or ""),
    ]

    for c in config_hierarchy:
        try:
            c = load(open(c, "r"))
            merge(config, c)
        except Exception as e:
            pass

    return config


def main(words, timeout, output):
    start = datetime.now()
    loop = get_event_loop()

    config = read_config()
    regions = config.get("regions")
    separators = config.get("separators")
    environments = config.get("environments")

    url_list = {
        f.format(region=region, word=word, sep=sep if env else "", env=env)
        for f in format_list
        for region in regions
        for word in words
        for sep in separators
        for env in environments
    }

    r = loop.run_until_complete(
        gather(
            *[loop.run_in_executor(None, find_bucket, url, timeout) for url in url_list]
        )
    )

    private, public = collect_results(r)
    stop = datetime.now()

    print(f"Complete after: {(stop - start).strftime('%H:%M:%S')}")
    print(f"Output written to: {output.name}")

    output.write(
        dumps(
            {
                "private": {"total": len(private), "hits": private},
                "public": {"total": len(public), "hits": public},
            },
            indent=4,
        )
    )


def cli():
    import argparse

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=lambda prog: argparse.HelpFormatter(
            prog, max_help_position=35, width=100
        ),
    )
    parser.add_argument(
        "-o",
        "--output",
        type=argparse.FileType("w"),
        metavar="file",
        default=stdout,
        help="write output to <file> (default: stdout)",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=int,
        metavar="seconds",
        default=30,
        help="http request timeout in <seconds> (default: 30)",
    )
    # parser.add_argument("words", nargs="?", type=argparse.FileType("r"), default=stdin, help="list of words to permute")
    parser.add_argument(
        "word_list",
        nargs="+",
        type=argparse.FileType("r"),
        help="read input from one or more <word-list> each containing a list of words to permute",
    )
    args = parser.parse_args()

    output = args.output
    timeout = args.timeout
    words = {l.strip() for f in args.word_list for l in f}

    main(words=words, timeout=timeout, output=output)


if __name__ == "__main__":
    cli()
