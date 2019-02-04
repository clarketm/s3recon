# [s3recon](https://s3recon.readthedocs.io/en/latest/)

[![PyPi release](https://img.shields.io/pypi/v/s3recon.svg)](https://pypi.org/project/s3recon/)
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
  -t seconds, --timeout seconds  http request timeout in <seconds> (default: 30)
  
```


## License

MIT &copy; [**Travis Clarke**](https://blog.travismclarke.com/)
