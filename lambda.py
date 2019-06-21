import json
import boto3
from pathlib import Path
import subprocess
import os
import git

s3 = boto3.client('s3')

def lambda_handler(event, context):
    download_scc()

    os.chdir('/tmp')
 
    if os.path.exists('/tmp/really-cheap-chatbot') == False:
        git.exec_command('clone', '--depth=1', 'https://github.com/boyter/really-cheap-chatbot.git', cwd='/tmp')
    os.system('./scc -f json -o /tmp/github.boyter.really-cheap-chatbot.json really-cheap-chatbot')

    with open("/tmp/github.boyter.really-cheap-chatbot.json", "rb") as f:
        s3.upload_fileobj(f, "sloccloccode", "github.boyter.really-cheap-chatbot.json")

    with open('/tmp/github.boyter.really-cheap-chatbot.json', encoding='utf-8') as f:
        content = f.read()

    j = json.loads(content)
    s = str(sum([x['Lines'] for x in j]))

    return {
        "statusCode": 200,
        "statusDescription": "200 OK",
        "isBase64Encoded": False,
        "headers": {
            "Content-Type": "image/svg+xml;charset=utf-8"
        },
        "body": '''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="100" height="20"><linearGradient id="b" x2="0" y2="100%"><stop offset="0" stop-color="#bbb" stop-opacity=".1"/><stop offset="1" stop-opacity=".1"/></linearGradient><clipPath id="a"><rect width="100" height="20" rx="3" fill="#fff"/></clipPath><g clip-path="url(#a)"><path fill="#555" d="M0 0h69v20H0z"/><path fill="#4c1" d="M69 0h31v20H69z"/><path fill="url(#b)" d="M0 0h100v20H0z"/></g><g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="110"> <text x="355" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="590">Total lines</text><text x="355" y="140" transform="scale(.1)" textLength="590">Total lines</text><text x="835" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="210">''' + s + '''</text><text x="835" y="140" transform="scale(.1)" textLength="210">''' + s + '''</text></g> </svg>'''
    }


def download_scc():
    my_file = Path("/tmp/scc")
    if os.path.exists('/tmp/scc') == False:
        with open('/tmp/scc', 'wb') as f:
            s3.download_fileobj('sloccloccode', 'scc', f)
    os.system('chmod +x /tmp/scc')


if __name__ == '__main__':
    with open('github.boyter.really-cheap-chatbot.json', encoding='utf-8') as f:
        content = f.read()

    j = json.loads(content)
    print(sum([x['Lines'] for x in j]))