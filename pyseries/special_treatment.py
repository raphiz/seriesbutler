import re

special_handling = [
    {
        'from': 'http\:\/\/vidbull.com\/.*',
        'to': 'vidbull: ignored!'
    },
    {
        'from': '(http|https)\:\/\/([^\/]*)\/embed-([^-]*)-[0-9]*x[0-9]*.html',
        'to': '{0}://{1}/{2}'
    }
]


def convert(url):
    for elm in special_handling:
        match = re.fullmatch(elm['from'], url)
        if match:
            return elm['to'].format(*match.groups())
    return url
