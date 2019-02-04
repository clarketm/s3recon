```eval_rst
.. meta::
   :description: s3recon: Amazon S3 bucket finder and crawler.

.. title:: s3recon
```

# [s3recon](https://pypi.org/project/s3recon/)

```eval_rst
Version |version|

.. image:: https://img.shields.io/pypi/v/s3recon.svg
    :target: https://pypi.org/project/s3recon/

.. image:: https://pepy.tech/badge/s3recon
    :target: https://pepy.tech/project/s3recon
    
```

**Amazon S3 bucket finder and crawler.**

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

MIT © [**Travis Clarke**](https://blog.travismclarke.com/)

