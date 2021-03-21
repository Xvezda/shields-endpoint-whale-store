# Copyright 2020 Xvezda <https://xvezda.com/>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
from time import time

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

# Base url of target store
BASE_URL = 'https://store.whale.naver.com'
# Valid cache time represented in seconds
CACHE_SECONDS = 14400
cache = {}


class CacheItem(BaseModel):
    item: dict
    timestamp: float


class ShieldsEndpointSchema(BaseModel):
    '''Follows endpoint schema of shields.io

    See: https://shields.io/endpoint
    '''
    # Required. Always the number 1.
    schemaVersion: int = 1
    # Required. The left text, or the empty string to omit the left side of the badge. This can be overridden by the query string.
    label: str = 'whale store'
    # Required. Can't be empty. The right text.
    message: str
    # The right color. Supports the eight named colors above, as well as hex, rgb, rgba, hsl, hsla and css named colors. This can be overridden by the query string.
    color: str = 'blue'
    # true to treat this as an error badge. This prevents the user from overriding the color. In the future it may affect cache behavior.
    isError: bool = False
    # Set the HTTP cache lifetime in seconds, which should be respected by the Shields' CDN and downstream users. Values below 300 will be ignored. This lets you tune performance and traffic vs. responsiveness. The value you specify can be overridden by the user via the query string, but only to a longer value.
    cacheSeconds: int = CACHE_SECONDS


class CacheExpired(ValueError):
    pass


res_not_found = {
    'message': 'not found',
    'isError': True,
    'color': 'critical'
}

res_internal_error = {
    'message': 'server error',
    'isError': True,
    'color': 'critical'
}

@router.get(
    '/v/{item_id}',
    response_model=ShieldsEndpointSchema,
)
async def read_item(item_id: str):
    if not re.match(r'^[a-z]{32}$', item_id):
        return {'message': 'bad id', 'isError': True, 'color': 'critical'}
    try:
        item_cache: CacheItem = cache[item_id]
        # Remove cache item when item's timestamp passed limit.
        if time() - item_cache.timestamp >= CACHE_SECONDS:
            del cache[item_id]
            raise CacheExpired('cache expired')
        item = item_cache.item
    except (KeyError, CacheExpired) as err:
        # Fetch information when cache expired or not exists.
        import httpx
        async with httpx.AsyncClient() as client:
            # Access details page to fetch required informations such as cookie
            url = '%s/detail/%s' % (BASE_URL, item_id)
            r = await client.head(url)

            if r.status_code == httpx.codes.NOT_FOUND:
                return res_not_found
            # Save url as referer
            referer = url
            match = re.search(r'xsrf-token=([^;]+)',
                              r.headers.get('set-cookie'), re.I)
            if not match:
                return res_internal_error
            xsrf_token = match.group(1)

            from urllib.parse import urlparse
            headers = {
                'Host': urlparse(BASE_URL).netloc,
                'Accept': '*/*',
                'Accept-Language': 'ko',
                'Cookie': 'XSRF-TOKEN=%s' % (xsrf_token,),
                'Referer': referer,
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-Mode': 'cors',
                'X-XSRF-TOKEN': xsrf_token,
                'x-requested-with': 'XMLHttpRequest',
            }
            r = await client.get(
                '%s/ajax/extensions/%s?hl=ko' % (BASE_URL, item_id),
                headers=headers
            )

            if r.status_code == httpx.codes.NOT_FOUND:
                return res_not_found
        # Skipping chracters that causing syntax error
        text = r.text[r.text.index('{'):]

        import json
        try:
            j = json.loads(text)
        except json.decoder.JSONDecodeError as err:
            return res_internal_error
        version = j.get('version')
        item = {'message': 'v'+version}
        # Cache item for later use
        cache[item_id] = CacheItem(item=item, timestamp=time())
    return item

