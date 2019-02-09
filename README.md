# [s3recon](https://s3recon.readthedocs.io/en/latest/)

[![PyPi release](https://img.shields.io/pypi/v/s3recon.svg)](https://pypi.org/project/s3recon/)
[![Downloads](https://pepy.tech/badge/s3recon)](https://pepy.tech/project/s3recon)
[![Documentation Status](https://readthedocs.org/projects/s3recon/badge/?version=latest)](https://s3recon.readthedocs.io/en/latest/?badge=latest)

Amazon S3 bucket finder and crawler.

[Check out the s3recon docs](https://s3recon.readthedocs.io/en/latest/)

## Installation

```bash
$ pip install s3recon
```

## Usage
```text

usage: s3recon [-h] [-o file] [-t seconds] word_list [word_list ...]

positional arguments:
  word_list                      read words from one or more <word-list> files

optional arguments:
  -h, --help                     show this help message and exit
  -o file, --output file         write output to <file> (default: stdout)
  -p, --public                   only include 'public' buckets in the output
  -t seconds, --timeout seconds  http request timeout in <seconds> (default: 30)
  -v, --version                  show program's version number and exit
  
```

## Example

#### 1. Download a word-list. The [SecLists](https://github.com/clarketm/s3recon/edit/master/README.md) repository has a multitude of word-lists to chose from. For this example, let's download the sample word-list included in this repository.
```bash
$ curl -sSfL -o "word-list.txt" "https://raw.githubusercontent.com/clarketm/s3recon/master/data/words.txt"
```

#### 2. Run `s3recon` against the `word-list.txt` file and output the `public` S3 buckets to a json file named `results.json`.

```bash
$ s3recon "word-list.txt" -o "results.json" --public

- PRIVATE https://s3.sa-east-1.amazonaws.com/test-lyft
- PRIVATE https://s3.ap-south-1.amazonaws.com/test.amazon
+ PUBLIC https://walmart-dev.s3.us-east-1.amazonaws.com
- PRIVATE https://s3.ap-southeast-1.amazonaws.com/apple-prod
- PRIVATE https://walmart.s3.ap-southeast-1.amazonaws.com
...
```

#### 3. Inspect the `results.json` file to see the S3 buckets you have discovered!

```bash
$ cat "results.json"
```

```json
{
    "public": {
        "total": 12,
        "hits": [
            "https://walmart-dev.s3.us-east-1.amazonaws.com",
            "https://apple-production.s3.ap-southeast-1.amazonaws.com",
            ...
        ]
    }
}
```

> **Note:** to include `private` buckets in the results omit the `-p, --public` flag from the command.

#### 4. Crawl the results list and enumerate the static files located in each bucket
Coming soon!


## FAQ
#### Q: How do I configure this utility?
#### A: 
`s3recon` can be configure using a yaml configuration file located in either the current working directory (e.g. `./s3recon.yml`) or your home diretory (e.g. `~/s3recon.yml`).

The following is the list of configurable values:
```yaml
# s3recon.yml

separators: ["-", "_", "."]
environments: ["", "backup", "backups", ...]
regions: ["ap-northeast-1", "ap-northeast-2", ...]
```

> To see the full list of configurable values (and their **defaults**) please refer to the [s3recon.yml](https://github.com/clarketm/s3recon/blob/master/s3recon/s3recon.yml) file in this repository. 


#### Q: How do I customize the AWS regions used in the recon?
#### A: 
The AWS *regions* can be altered by setting the `regions` array in your `s3recon.yml` configuration file. 
```yaml
# s3recon.yml

regions: [ "us-west-2", ...]
```


#### Q: How do I customize the values of the environment used in the recon?
#### A: 
The *environments* are modifiers permuted with each item of the *word-list* (and the *separator*) to construct the bucket value in request.
The value can be altered by setting the `environments` array in your `s3recon.yml` configuration file.

For example, to only search lines from the word-list *verbatim* (i.e. without modification) you can set this value to an empty array. 
```yaml
# s3recon.yml

environments: []
```

## Going Forward

- [] Create `crawl` command to crawl public/private buckets found in `find` stage.
- [] Separate out `find` and `crawl` as subcommands.
- [] Store discovered buckets in a NoSQL database.

## License

MIT &copy; [**Travis Clarke**](https://blog.travismclarke.com/)
