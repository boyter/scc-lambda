import json
import os
from pathlib import Path

import boto3
import git

from datetime import datetime, timedelta
import time


s3 = boto3.client('s3')
bucket_name = 'sloccloccode'

def lambda_handler(event, context):

    print(event)
    
    # Contains an array containing the params, so ?=something=test it will have something as a key
    print(event["queryStringParameters"])

    get_process_file()

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


def get_process_file():
    s = boto3.resource('s3')
    o = s.Object(bucket_name,'github.boyter.really-cheap-chatbot.json')
    unixtime = s3time_to_unix(o.last_modified)

    diff = int(time.time() - unixtime)
    if diff < 86400:
        o.download_file('/tmp/github.boyter.really-cheap-chatbot.json')
    else:
        clone_and_process()


def clone_and_process():
    download_scc()

    os.chdir('/tmp')
 
    if os.path.exists('/tmp/really-cheap-chatbot') == False:
        git.exec_command('clone', '--depth=1', 'https://github.com/boyter/really-cheap-chatbot.git', cwd='/tmp')
    os.system('./scc -f json -o /tmp/github.boyter.really-cheap-chatbot.json really-cheap-chatbot')

    with open("/tmp/github.boyter.really-cheap-chatbot.json", "rb") as f:
        s3.upload_fileobj(f, bucket_name, "github.boyter.really-cheap-chatbot.json")


def download_scc():
    my_file = Path("/tmp/scc")
    if os.path.exists('/tmp/scc') == False:
        with open('/tmp/scc', 'wb') as f:
            s3.download_fileobj(bucket_name, 'scc', f)
    os.system('chmod +x /tmp/scc')


def s3time_to_unix(last_modified):
    datetime_object = datetime.strptime(str(last_modified).split(' ')[0], '%Y-%m-%d')
    unixtime = time.mktime(datetime_object.timetuple())
    return unixtime


if __name__ == '__main__':
    
    last_modified = '2019-06-22 07:13:19+00:00'
    unixtime = s3time_to_unix(last_modified)

    diff = int(time.time() - unixtime)
    print(diff > 86400)
    if diff < 86400:
        print('pull from s3 and return')
    else:
        print('clone him and reprocess')


    # s3 = boto3.resource('s3')
    # o = s3.Object('sloccloccode','github.boyter.really-cheap-chatbot.json')
    # print(o.last_modified)
    # o.download_file('/tmp/github.boyter.really-cheap-chatbot.json')