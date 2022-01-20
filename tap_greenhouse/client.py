import json
import requests
import requests.exceptions
import singer
import time
import urllib

LOGGER = singer.get_logger()


class GreenhouseAPI:
    URL_TEMPLATE = 'https://harvest.greenhouse.io'
    MAX_RETRIES = 10

    def __init__(self, config):
        self.api_key = config['api_key']
        self.base_url = self.URL_TEMPLATE

    def get(self, url):
        if not url.startswith('https://'):
            url = f'{self.base_url}{url}'

        for num_retries in range(self.MAX_RETRIES):
            LOGGER.info(f'greenhouse get request {url}')
            resp = requests.get(
                url,
                auth=(self.api_key, '')
            )
            LOGGER.info(f'Logged')

            try:
                resp.raise_for_status()
            except requests.exceptions.RequestException:
                if resp.status_code == 429 and num_retries < self.MAX_RETRIES:
                    retry_after = resp.headers['Retry-after']
                    LOGGER.info('api query greenhouse rate limit', extra={
                        'retry_after': retry_after,
                        'subdomain': self.subdomain
                    })
                    time.sleep(int(retry_after))
                elif resp.status_code >= 500 and num_retries < self.MAX_RETRIES:
                    LOGGER.info('api query greenhouse 5xx error', extra={
                        'subdomain': self.subdomain
                    })
                    time.sleep(10)
                else:
                    raise Exception(f'greenhouse query error: {resp.status_code}')

            if resp and resp.status_code == 200:
                break
        return resp

    def post(self, url, params):

        if not url.startswith('https://'):
            url = f'{self.base_url}/{url}'

        resp = requests.post(
            url,
            json=params,
            auth=(self.username, self.password)
        )

        return resp.json()
