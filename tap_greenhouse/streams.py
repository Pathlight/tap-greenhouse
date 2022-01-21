import datetime
import pytz
import singer

from singer.utils import strptime_to_utc, strftime as singer_strftime


LOGGER = singer.get_logger()


class Stream():
    name = None
    replication_method = None
    key_properties = None
    stream = None
    view_id_key = None
    datetime_fields = None
    url = None
    results_key = None

    def __init__(self, client=None, start_date=None):
        self.client = client
        if start_date:
            self.start_date = start_date
        else:
            self.start_date = datetime.datetime.min.strftime('%Y-%m-%d')

    def is_selected(self):
        return self.stream is not None

    def update_bookmark(self, state, value):
        current_bookmark = singer.get_bookmark(state, self.name, self.replication_key)
        if value and value > current_bookmark:
            singer.write_bookmark(state, self.name, self.replication_key, value)

    def transform_value(self, key, value):
        if key in self.datetime_fields and value:
            value = strptime_to_utc(value)
            # reformat to use RFC3339 format
            value = singer_strftime(value)

        return value

class EEOC(Stream):
    name = 'eeoc'
    replication_method = 'INCREMENTAL'
    key_properties = ['application_id']
    replication_key = 'submitted_at'
    incremental_search_key='submitted_after'
    url = '/v1/eeoc'
    datetime_fields = set([
        'submitted_before', 'submitted_after'
    ])
    results_key = 'data'

    def paging_get(self, url):
        per_page = 500
        url = url+f'&per_page={per_page}'
        
        while True:
            r = self.client.get(url)
            data = r.json()
            for record in data:  
                yield record
            if 'next' in r.links:
                url = r.links['next']['url']
            else:
                break

    def sync(self, state, config):
        try:
            sync_thru = singer.get_bookmark(state, self.name, self.replication_key)
        except TypeError:
            sync_thru = self.start_date
        
        processed_url = self.url+f'?{self.incremental_search_key}={sync_thru}'
        
        for row in self.paging_get(processed_url):
            values = {k: self.transform_value(k, v) for (k, v) in row.items()}
            yield(self.stream, values)

class Applications(Stream):
    name = 'applications'
    replication_method = 'INCREMENTAL'
    key_properties = ['id']
    replication_key = 'last_activity_at'
    incremental_search_key='updated_after',
    url = '/v1/applications'
    datetime_fields = set([
        'updated_before', 'updated_after'
    ])
    results_key = 'data'

    def paging_get(self, url):
        per_page = 500
        url = url+f'&per_page={per_page}'
        
        while True:
            r = self.client.get(url)
            data = r.json()
            for record in data:  
                yield record
            if 'next' in r.links:
                url = r.links['next']['url']
            else:
                break

    # def sync(self, ticket_id, sync_thru):
    def sync(self, state, config):
        try:
            sync_thru = singer.get_bookmark(state, self.name, self.replication_key)
        except TypeError:
            sync_thru = self.start_date
        
        processed_url = self.url+f'?{self.incremental_search_key}={sync_thru}'
        
        for row in self.paging_get(processed_url):
            values = {k: self.transform_value(k, v) for (k, v) in row.items()}
            yield(self.stream, values)

class Candidates(Stream):
    name = 'candidates'
    replication_method = 'INCREMENTAL'
    key_properties = ['id']
    replication_key = 'last_activity_at'
    incremental_search_key='last_activity_after',
    url = '/v1/candidates'
    datetime_fields = set([
        'submitted_before', 'submitted_after'
    ])
    results_key = 'data'

    def paging_get(self, url):
        per_page = 500
        url = url+f'&per_page={per_page}'
        
        while True:
            r = self.client.get(url)
            data = r.json()
            for record in data:  
                yield record
            if 'next' in r.links:
                url = r.links['next']['url']
            else:
                break

    # def sync(self, ticket_id, sync_thru):
    def sync(self, state, config):
        try:
            sync_thru = singer.get_bookmark(state, self.name, self.replication_key)
        except TypeError:
            sync_thru = self.start_date
        
        processed_url = self.url+f'?{self.incremental_search_key}={sync_thru}'
        
        for row in self.paging_get(processed_url):
            values = {k: self.transform_value(k, v) for (k, v) in row.items()}
            yield(self.stream, values)

STREAMS = {
    "eeoc": EEOC,
    "applications": Applications,
    "candidates": Candidates,
}
