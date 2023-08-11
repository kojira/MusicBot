import aiohttp
import lxml.html
import codecs
import re

async def get_sound_info(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            text = await response.text('utf-8')
            html = lxml.html.fromstring(text)

            nana_prefix = "https://nana-music.com"

            page_info = {}
            page_info["image"] = html.cssselect('meta[property="og:image"]')[0].get('content')
            page_info["user_name"] = html.xpath("//div[@class='post-user-name']")[0].text_content().strip()
            page_info["icon_url"] = html.xpath("//div[@class='post-user']")[0][0][0].attrib["src"]
            page_info["user_url"] = nana_prefix+html.xpath("//div[@class='post-user']")[0][0].attrib["href"]
            sound_url_base = html.xpath("/html/body/script[1]")[0].text_content().strip()
            m = re.search(r"sound_url=\"(.*?\.m4a)\"", sound_url_base)
            page_info["sound_url"] = codecs.decode(m.groups()[0], 'unicode-escape')
            
            page_info["artist_name"] = html.xpath("//div[@class='post-artist']")[0][0].text_content().strip()
            page_info["title"] = html.xpath("//div[@class='post-title']")[0][0].text_content().strip()
            page_info["play_counts"] = int(html.xpath("//li[@class='count__list-play']")[0].text_content().strip())
            page_info["applause_counts"] = int(html.xpath("//li[@class='count__list-applause']")[0].text_content().strip())
            page_info["comment_counts"] = int(html.xpath("//li[@class='count__list-comment']")[0].text_content().strip())
            api_path = re.search(r"(/v2/posts/[0-9]+/)", text)
            page_info["api_url"] = nana_prefix+api_path.groups()[0]

            return page_info


async def countup_play_count(api_url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url+"play") as response:
                text = await response.text('utf-8')
    except:
        import sys
        import traceback
        import datetime
        exc_type, exc_value, exc_traceback = sys.exc_info()
        err_text = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
        sys.stderr.write(err_text)
        print(err_text)

    return text


async def main(url):
    page_info = await get_sound_info(url)
    print(page_info)


async def count_up(url):
    page_info = await get_sound_info(url)
    print(page_info)
    response = await countup_play_count(page_info['api_url'])
    print("response",response)


if __name__ == '__main__':
    import asyncio
    url = "https://nana-music.com/sounds/053a0a3f"
    asyncio.run(main(url))
    asyncio.run(count_up(url))

