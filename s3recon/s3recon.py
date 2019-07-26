#!/usr/bin/env python3
from asyncio import get_event_loop, gather
from collections import defaultdict
from datetime import datetime
from json import dumps
from logging import getLogger, basicConfig, INFO
from os import environ
from pathlib import Path
from random import choice
from sys import path
from warnings import filterwarnings

import requests
from mergedeep import merge
from requests import RequestException
from urllib3.exceptions import InsecureRequestWarning
from yaml import safe_load as load

if not __package__:
    path.insert(0, str(Path(Path(__file__).parent.parent.parent)))

from s3recon import __version__
from s3recon.constants import useragent_list, format_list
from s3recon.mongodb import MongoDB, Hit, Access

filterwarnings("ignore", category=InsecureRequestWarning)

logger = getLogger(__name__)

# TODO: opt to change log-level
basicConfig(format="%(message)s", level=INFO)


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
    except RequestException:
        pass

    return exists, public


def find_bucket(url, timeout, db):
    exists, public = bucket_exists(url, timeout)

    if exists:
        access = Access.PUBLIC if public else Access.PRIVATE
        access_key = repr(access)
        access_word = str(access).upper()
        logger.info(f"{access_key} {access_word} {url}")

        hit = Hit(url, access)
        if db and hit.is_valid():
            db.update({"url": url}, dict(hit))
        return Hit(url, access)

    return None


def collect_results(hits):
    d = defaultdict(list)
    for hit in hits:
        url = hit.url
        access = repr(hit.access)
        d[access].append(url)

    return d.get(repr(Access.PRIVATE), []), d.get(repr(Access.PUBLIC), [])


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
            c = load(open(c, "r")) or {}
            merge(config, c)
        except (IOError, TypeError):
            pass

    return config


def json_output_template(key, total, hits, exclude):
    return {} if exclude else {key: {"total": total, "hits": hits}}


def main(words, timeout, output, use_db, only_public):
    start = datetime.now()
    loop = get_event_loop()

    config = read_config()
    database = config.get("database")
    regions = config.get("regions") or [""]
    separators = config.get("separators") or [""]
    environments = config.get("environments") or [""]

    url_list = {
        f.format(
            region=f"s3.{region}" if region else "s3",
            word=word,
            sep=sep if env else "",
            env=env,
        )
        for f in format_list
        for region in regions
        for word in words
        for sep in separators
        for env in environments
    }

    tasks = gather(
        *[
            loop.run_in_executor(
                None,
                find_bucket,
                url,
                timeout,
                MongoDB(host=database["host"], port=database["port"])
                if use_db
                else None,
            )
            for url in url_list
        ]
    )
    hits = filter(bool, loop.run_until_complete(tasks))

    private, public = collect_results(hits)

    if output:
        json_result = {
            **json_output_template(
                str(Access.PRIVATE), len(private), private, only_public
            ),
            **json_output_template(str(Access.PUBLIC), len(public), public, False),
        }

        output.write(dumps(json_result, indent=4))
        logger.info(f"Output written to file: {output.name}")

    stop = datetime.now()
    logger.info(f"Complete after: {stop - start}")


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
        help="write output to <file>",
    )
    parser.add_argument(
        "-d", "--db", action="store_true", help="write output to database"
    )
    parser.add_argument(
        "-p",
        "--public",
        action="store_true",
        help="only include 'public' buckets in the output",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=int,
        metavar="seconds",
        default=30,
        help="http request timeout in <seconds> (default: 30)",
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    # parser.add_argument("words", nargs="?", type=argparse.FileType("r"), default=stdin, help="list of words to permute")
    parser.add_argument(
        "word_list",
        nargs="+",
        type=argparse.FileType("r"),
        help="read words from one or more <word-list> files",
    )
    args = parser.parse_args()

    output = args.output
    db = args.db
    timeout = args.timeout
    public = args.public
    words = {l.strip() for f in args.word_list for l in f}

    main(words=words, timeout=timeout, output=output, use_db=db, only_public=public)


if __name__ == "__main__":
    cli()
