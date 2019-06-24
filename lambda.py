import json
import os
from pathlib import Path
import re
import string

import boto3
import git

from datetime import datetime, timedelta
import time


s3 = boto3.client('s3')
bucket_name = 'sloccloccode'

def lambda_handler(event, context):
    # Contains an array containing the params, so ?=something=test it will have something as a key
    # print(event["queryStringParameters"])

    if 'path' not in event:
        return {
            "statusCode": 400,
            "statusDescription": "400",
            "isBase64Encoded": False,
            "headers": {
                "Content-Type": "text/html"
            },
            "body": '''You be invalid'''
        }

    filename, url, path = process_path(event['path'])

    if filename == None or url == None or path == None:
        return {
            "statusCode": 400,
            "statusDescription": "400",
            "isBase64Encoded": False,
            "headers": {
                "Content-Type": "text/html"
            },
            "body": '''You be invalid'''
        }

    get_process_file(filename=filename, url=url, path=path)

    with open('/tmp/' + filename, encoding='utf-8') as f:
        content = f.read()

    j = json.loads(content)
    s = format_count(sum([x['Lines'] for x in j]))

    text_length = '250'
    if len(s) <= 3:
        text_length = '200'

    return {
        "statusCode": 200,
        "statusDescription": "200 OK",
        "isBase64Encoded": False,
        "headers": {
            "Content-Type": "image/svg+xml;charset=utf-8"
        },
        "body": '''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="100" height="20"><linearGradient id="b" x2="0" y2="100%"><stop offset="0" stop-color="#bbb" stop-opacity=".1"/><stop offset="1" stop-opacity=".1"/></linearGradient><clipPath id="a"><rect width="100" height="20" rx="3" fill="#fff"/></clipPath><g clip-path="url(#a)"><path fill="#555" d="M0 0h69v20H0z"/><path fill="#4c1" d="M69 0h31v20H69z"/><path fill="url(#b)" d="M0 0h100v20H0z"/></g><g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="110"> <text x="355" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="590">Total lines</text><text x="355" y="140" transform="scale(.1)" textLength="590">Total lines</text><text x="835" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="''' + text_length + '''">''' + s + '''</text><text x="835" y="140" transform="scale(.1)" textLength="''' + text_length + '''">''' + s + '''</text></g> </svg>'''
    }


def get_process_file(filename, url, path):
    s = boto3.resource('s3')
    o = s.Object(bucket_name, filename)

    try:
        unixtime = s3time_to_unix(o.last_modified)
    except:
        # force an update in this case
        unixtime = time.time() - 186400

    diff = int(time.time() - unixtime)
    if diff < 86400:
        o.download_file('/tmp/' + filename)
    else:
        clone_and_process(filename=filename, url=url, path=path)


def clone_and_process(filename, url, path):
    download_scc()

    os.chdir('/tmp')
 
    os.system('rm -rf /tmp/scc-tmp-path')
    git.exec_command('clone', '--depth=1', url, 'scc-tmp-path',cwd='/tmp')
    
    os.system('./scc -f json -o /tmp/' + filename + ' scc-tmp-path')

    with open('/tmp/' + filename, 'rb') as f:
        s3.upload_fileobj(f, bucket_name, filename)
    
    os.system('rm -rf /tmp/scc-tmp-path')


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


def process_path(path):
    path = re.sub('', '', path, flags=re.MULTILINE )

    s = [clean_string(x) for x in path.lower().split('/') if x != '']

    if len(s) != 3:
        return None, None, None

    # Cheap clean check
    for x in s:
        if x == '':
            return None, None, None

    # URL for cloning
    url = 'https://'

    if s[0] == 'github':
        url += 'github.com/'
    if s[0] == 'bitbucket':
        url += 'bitbucket.org/'
    if s[0] == 'gitlab':
        url += 'gitlab.com/'
 
    url += s[1] + '/'
    url += s[2] + '.git'

    # File for json
    filename = s[0]
    filename += '.' + s[1]
    filename += '.' + s[2] + '.json'

    # Need path
    path = s[2]

    return (filename, url, path)


def clean_string(s):
    valid = string.ascii_lowercase
    valid += '-'
    valid += '.'

    clean = ''

    for c in s:
        if c in valid:
            clean += c

    return clean


def format_count(count):
    ranges = [
        (1e18, 'E'),
        (1e15, 'P'),
        (1e12, 'T'),
        (1e9, 'G'),
        (1e6, 'M'),
        (1e3, 'k'),
    ]

    for x, y in ranges:
        if count >= x:
            t = str(round(count / x, 1))
            if len(t) > 3:
                t = t[:t.find('.')]
            return t + y

    return str(count)


if __name__ == '__main__':
    
    # last_modified = '2019-06-22 07:13:19+00:00'
    # unixtime = s3time_to_unix(last_modified)

    # diff = int(time.time() - unixtime)
    # print(diff > 86400)
    # if diff < 86400:
    #     print('pull from s3 and return')
    # else:
    #     print('clone him and reprocess')

    x, y, z = process_path('/github/boyter/really-cheap-chatbot/')
    print(x, y, z)
    '''
    https://gitlab.com/esr/loccount.git
    https://bitbucket.org/grumdrig/pq-web.git
    https://github.com/boyter/scc.git
    '''

    print(format_count(100))
    print(format_count(1000))
    print(format_count(2500))
    print(format_count(436465))
    print(format_count(263804))
    print(format_count(86400))

    # s3 = boto3.resource('s3')
    # o = s3.Object('sloccloccode','github.boyter.really-cheap-chatbot.json')
    # print(o.last_modified)
    # o.download_file('/tmp/github.boyter.really-cheap-chatbot.json')