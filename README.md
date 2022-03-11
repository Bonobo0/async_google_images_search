# async_google_images_search

# Parameters
```
query: something you want to search for
safe: safe search
validation: check images existence
download: images download
timeout: validation & download timeout (second)
```

# Example
```
import async_google_images_search as agis
import asyncio

async def download():
    await agis.async_imageSearch(query="google",validation=False,download=True,timeout=5)

asyncio.get_event_loop().run_until_complete(download())

```
# Result
``{'result': [many images links], "resultLength": resultList length(max=100), "elapsedTime": elapsedTime(seconds)}``
# Licence
MIT
