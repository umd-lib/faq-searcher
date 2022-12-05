import json
import logging
import furl
import os
import requests

from flask import Flask, request
from dotenv import load_dotenv
from waitress import serve
from paste.translogger import TransLogger

load_dotenv('../.env')

env = {}
for key in ('LIBANSWERS_API_BASE', 'IID', 'NO_RESULTS_URL', 'MODULE_URL'):
    env[key] = os.environ.get(key)
    if env[key] is None:
        raise RuntimeError(f'Missing environment variable: {key}')

siteid = env['IID']
no_results_url = env['NO_RESULTS_URL']
module_url = env['MODULE_URL']

debug = os.environ.get('FLASK_DEBUG')

logger = logging.getLogger('faq-searcher')
loggerWaitress = logging.getLogger('waitress')

if debug:
    logger.setLevel(logging.DEBUG)
    loggerWaitress.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
    loggerWaitress.setLevel(logging.INFO)

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


@app.route('/')
def root():
    return {'status': 'ok'}


@app.route('/ping')
def ping():
    return {'status': 'ok'}


@app.route('/search')
def search():
    args = request.args

    # Check query param
    if 'q' not in args or args['q'] == '':
        return {
            'error': {
                'msg': 'q parameter is required',
            },
        }, 400

    # Libanswers api only seems to work with spaces as +
    query = args['q'].replace(" ", "+")

    limit = 3
    if 'per_page' in args and args['per_page'] != "":
        limit = int(args['per_page'])

    offset = 0
    page = 1
    if 'page' in args and args['page'] != "":
        page = int(args['page'])
        if page > 1:
            offset = limit * (page - 1) + 1

    logger.debug(f'Pagination debug offset={offset} page={page} limit={limit}')

    # Prepare OCLC API search
    params = {
        'iid': siteid,
        'limit': limit,
    }

    full_query_url = env['LIBANSWERS_API_BASE'] + query

    search_url = furl.furl(full_query_url)

    # Execute Libanswers API search
    try:
        response = requests.get(search_url.url, params=params)
    except Exception as err:
        logger.error(f'Search error at url'
                     '{search_url.url}, params={params}\n{err}')

        return {
            'endpoint': 'faq',
            'error': {
                'msg': f'Search error',
            },
        }, 500

    if response.status_code not in [200, 206]:
        logger.error(f'Received {response.status_code} with q={query}')

        return {
            'endpoint': 'faq',
            'error': {
                'msg': f'Received {response.status_code} for q={query}',
            },
        }, 500

    logger.debug(f'Submitted url={search_url.url}, params={params}')
    logger.debug(f'Received response {response.status_code}')

    json_content = json.loads(response.text)
    total_records = get_total_records(json_content)

    module_link = module_url + query

    api_response = {
        'endpoint': 'faq',
        'query': query,
        'per_page': limit,
        'page': page,
        'total': total_records,
        'module_link': module_link,
    }

    if total_records != 0:
        api_response['results'] = build_response(json_content)
    else:
        api_response['error'] = build_no_results()

    return api_response


def build_no_results():
    return {
        'msg': 'No Results',
        'no_results_url': no_results_url,
    }


def build_response(json_content):
    results = []
    if 'search' in json_content:
        search = json_content['search']
        if 'results' in search:
            for item in search['results']:
                topics = None
                if 'topics' in item:
                    topics = ", ".join(item['topics'])
                results.append({
                    'title': item['question'],
                    'item_format': 'web_page',
                    'link': item['url'],
                    'description': topics,
                })
    return results


def get_total_records(json_content):
    if 'search' not in json_content:
        return None
    search = json_content['search']
    if 'numFound' not in search:
        return None
    return int(search['numFound'])


if __name__ == '__main__':
    # This code is not reached when running "flask run". However the Docker
    # container runs "python app.py" and host='0.0.0.0' is set to ensure
    # that flask listens on port 5000 on all interfaces.

    # Run waitress WSGI server
    serve(TransLogger(app, setup_console_handler=True),
          host='0.0.0.0', port=5000, threads=10)
