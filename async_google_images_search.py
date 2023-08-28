try:
    from bs4 import BeautifulSoup as bs
    from lxml import html
    import re
    import ssl
    import json
    import time
    import aiohttp
    import aiofiles
    import os
    import asyncio
    import progressbar
    import click
    import time
    import random
except ImportError:
    print("\n\n[!] Please install the following modules: bs4, lxml, aiohttp, aiofiles, progressbar, click\n\n")
    exit()


async def async_imageSearch(query, safe=False, validation=False, download=False, timeout=10, *args, **kwargs):
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(
        limit=0), timeout=aiohttp.ClientTimeout(total=timeout))
    query = re.sub(r'[\\/:?<>|]', '', query)
    tm = time.time()
    headers = {
        "User-Agent":
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0s Safari/537.36"
    }
    googleSearchUrl = f"https://www.google.com.au/search?q={query}&gl=AU&tbm=isch&espv=2&site=webhp&source=lnms&sa=X&ei=XosDVaCXD8TasATItgE&ved=0CAcQ_AUoAg"
    if safe == True:
        googleSearchUrl = f"https://www.google.com/search?q={query}&source=lnms&tbm=isch&safe=acitve"
    async with session.get(googleSearchUrl, headers=headers) as response:
        html = await response.text()
    htmlData = bs(html, 'lxml')
    scripts = htmlData.select('script')
    images = re.findall(
        r"AF_initDataCallback\(([^<]+)\);", str(scripts))
    imagesData = images[1]
    imagesData_fix = json.dumps(imagesData, indent=2)
    imagesData_fix_json = json.loads(imagesData_fix)
    google_images_Data_removethumbnails = re.sub(
        r'\[\"(https\:\/\/encrypted-tbn0\.gstatic\.com\/images\?.*?)\",\d+,\d+\]', '', str(imagesData_fix_json))
    google_images_fullRes = re.findall(r"(?:'|,),\[\"(https:|http.*?)\",\d+,\d+\]",
                                       google_images_Data_removethumbnails)
    finalResults = []
    for i in google_images_fullRes:
        imageURI = i.replace("\u005c\u005c", "\u002f")
        # Above line is for removing reverse solidus from the full resolution image URI
        finalResults.append(bytes(bytes(imageURI, 'ascii').decode(
            'unicode-escape'), 'ascii').decode('unicode-escape'))
    try:
        if validation == True and download == True:
            validation = False
        if validation == True:
            for i in finalResults:
                async with session.head(i, ssl=False) as response:
                    if str(response.status) != "200" or response.content_type.find("image") == -1:
                        finalResults.remove(i)
        if download == True:
            counter = 0
            bar = progressbar.ProgressBar(widgets=[' [', progressbar.Timer(), '] ', progressbar.Bar(
            ), ' (', progressbar.ETA(), ') ', ], maxval=len(finalResults)).start()
            for i in finalResults:
                try:
                    async with session.get(i, ssl=False) as response:
                        if str(response.status) == "200":
                            os.makedirs(f"./download", exist_ok=True)
                            os.makedirs(f"./download/{query}", exist_ok=True)
                            async with aiofiles.open(f"./download/{query}/{query}_{counter}.gif", 'wb') as f:
                                await f.write(await response.read())
                                counter += 1
                                bar.update(counter)

                except aiohttp.ClientResponseError as e:
                    print(f"ClientResponseError\n\n{e}")
                    counter += 1
                    finalResults.remove(i)
                except asyncio.TimeoutError as e:
                    print(f"Timeout\n\n{e}")
                    counter += 1
                    finalResults.remove(i)
                except Exception as e:
                    print(f"Exception\n\n{e}")
                    counter += 1
                    finalResults.remove(i)
            bar.finish()
            print(f"\n\n{len(finalResults)} images downloaded")
        await session.close()
    except aiohttp.ClientSSLError as e:
        assert isinstance(e, ssl.CertificateError)
    except IndexError:
        return {"error": "No results found"}
    return {"result": finalResults, "resultLength": len(finalResults), "elapsedTime": round(time.time()-tm, 2)}


randomFloat = random.random()


@click.option('--safe', '-s', default=False, help="Safe search")
@click.option('--validation', '-v', default=False, help="Validation")
@click.option('--download', '-d', default=False, help="Download")
@click.option('--timeout', '-t', default=10, help="Timeout")
@click.command()
@click.argument('query', default=randomFloat)
def main(query, safe, validation, download, timeout):
    if query == randomFloat:
        query = input("검색어를 입력해주세요: ")
        safe = input("세이프 서치(True/False | 기본값 False): ")
        validation = input("유효성 검사(True/False | 기본값 False): ")
        download = input("다운로드(True/False | 기본값 False): ")
        timeout = input("유효성 검사 & 다운로드 타임아웃(초 | 기본값 10): ")
        if safe == "":
            safe = False
        if validation == "":
            validation = False
        if download == "":
            download = False
        if timeout == "":
            timeout = 10
        if query == "":
            print("\n\n[!] 검색어를 입력해주세요.\n\n프로그램이 30초 후에 자동으로 닫힙니다.\n\n[!] Please enter a query\n\nProgram closes automatically after 30 seconds\n\n")
            time.sleep(30)
            exit()
    try:
        print(asyncio.get_event_loop().run_until_complete(async_imageSearch(
            query, bool(safe), bool(validation), bool(download), float(timeout))))
        if download == False:
            time.sleep(9999)
        else:
            print(
                f"[!] 이미지 다운로드가 ./download/{query} 폴더에 완료되었습니다.\n\n[!] Images downloaded to ./download/{query}\n\n")
            print(
                "[!] 프로그램이 30초 후에 자동으로 닫힙니다.\n\n[!] Program closes automatically after 30 seconds\n\n")
            time.sleep(30)
    except KeyboardInterrupt:
        print("\n\n[!] 프로그램이 종료되었습니다.\n\n[!] Program closed.\n\n")
        time.sleep(3)
        exit()
    except ValueError as e:
        print(e)
        print("\n\n[!] 잘못된 값을 입력하셨습니다.\n\n[!] You entered an invalid value.\n\n")
        time.sleep(3)
        exit()
    except Exception as e:
        print(f"\n\n[!] 오류가 발생했습니다.\n\n[!] An error occurred.\n\n{e}\n\n")
        time.sleep(3)
        exit()


if __name__ == "__main__":
    main()
