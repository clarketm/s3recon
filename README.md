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

#### 1. Download a word-list. The [SecLists](https://github.com/clarketm/s3recon/edit/master/README.md) repository has a multitude of word-lists to choice from. For this example let's download the sample word-list included in this repository.
```bash
$ curl -sSfL -o word-list.txt "https://raw.githubusercontent.com/clarketm/s3recon/master/data/words.txt" | tar -xz
```

#### 2. Run `s3recon` against the `word-list.txt` file and output the `public` bucket results to a json file named `results.json`.

```bash
$ s3recon "word-list.txt" -o "results.json" --public

- PRIVATE https://s3.sa-east-1.amazonaws.com/test-lyft
- PRIVATE https://s3.ap-south-1.amazonaws.com/test.amazon
+ PUBLIC https://walmart-dev.s3.us-east-1.amazonaws.com
- PRIVATE https://s3.ap-southeast-1.amazonaws.com/apple-prod
- PRIVATE https://walmart.s3.ap-southeast-1.amazonaws.com
...
```

#### 3. Inspect the `results.json` file to see the S3 buckets 💰 you have discovered!

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

> Note: to limit the results set to **only** *public* buckets use the `-p, --public` flag.

#### 4. Crawl the results list and enumerate the static files available in each bucket
Coming soon!


## FAQ
#### Q: How do I configure this utility?
#### A: 
`s3recon` can be configure using a yaml configuration file location in either the current working directory (e.g. `./s3recon.yml`) or the users home diretory (e.g. `~/s3recon.yml`).

List of configurable values:
```yaml
# s3recon.yml

separators: ["-", "_", "."]
environments: ["", "backup", "backups", ...]
regions: ["ap-northeast-1", "ap-northeast-2", ...]
```

> To see the full list of configurable values (and their **defaults**) please refer to the [s3recon.yml](https://github.com/clarketm/s3recon/blob/master/s3recon/s3recon.yml) configuration file. 


#### Q: How do I customize the AWS regions used in the recon?
#### A: 
The AWS region can be altered by setting the `regions` array in your `s3recon.yml`. 
```yaml
# s3recon.yml

regions: [ "us-west-2", ...]
```


#### Q: How do I customize the values of the environment modifiers used in the recon?
#### A: 
The environment modifier are modifiers permuted with each item of the word-list and separator to for the bucket value in the lookup.
The value can be altered by setting the `environments` array in your `s3recon.yml`.

For example, to only search lines from the word-list *verbatim* you can set this value to an empty array or an array with an empty string. 
```yaml
# s3recon.yml

environments: []

# same effect as:
environments: [""]
>  


## Going Forward

- [] Create `crawl` command to crawl public/private buckets found in `find` stage and output filenames.
- [] Separate out `find` and `crawl` as subcommands.
- [] Store discovered buckets in a NoSQL datastore.

## License

MIT &copy; [**Travis Clarke**](https://blog.travismclarke.com/)
