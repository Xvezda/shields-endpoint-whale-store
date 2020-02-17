import re
from time import time

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

BASE_URL = 'https://store.whale.naver.com'
CACHE_SECONDS = 14400

cache = {}


class CacheItem(BaseModel):
    item: dict
    timestamp: float


class ShieldsEndpointSchema(BaseModel):
    schemaVersion: int = 1
    label: str = 'whale store'
    message: str
    color: str = 'blue'
    isError: bool = False
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
        if time() - item_cache.timestamp >= CACHE_SECONDS:
            del cache[item_id]
            raise CacheExpired('cache expired')
        item = item_cache.item
    except (KeyError, CacheExpired) as err:
        import httpx
        async with httpx.AsyncClient() as client:
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
        cache[item_id] = CacheItem(item=item, timestamp=time())
    return item

