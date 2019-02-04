private_key = "-"
private_text = "PRIVATE"
public_key = "+"
public_text = "PUBLIC"

format_list = [
    "https://s3.{region}.amazonaws.com/{word}{sep}{env}",
    "https://s3.{region}.amazonaws.com/{env}{sep}{word}",
    "https://{word}{sep}{env}.s3.{region}.amazonaws.com",
    "https://{env}{sep}{word}.s3.{region}.amazonaws.com",
]

region_list = [
    "ap-northeast-1",
    "ap-northeast-2",
    "ap-northeast-3",
    "ap-south-1",
    "ap-southeast-1",
    "ap-southeast-2",
    "ca-central-1",
    "cn-north-1",
    "cn-northwest-1",
    "eu-central-1",
    "eu-north-1",
    "eu-west-1",
    "eu-west-2",
    "eu-west-3",
    "sa-east-1",
    "us-east-1",  # or ""
    "us-east-2",
    "us-west-1",
    "us-west-2",
]

env_list = [
    "",
    "backup",
    "backups",
    "dev",
    "development",
    "prod",
    "production",
    "stage",
    "staging",
    "test",
    "testing",
]

sep_list = ["-", "_", "."]

useragent_list = [l.strip() for l in open("./useragents.txt", "r")]

# word_list = [l.strip() for l in open("./words.txt", "r")]
word_list = ["sinclair"]
