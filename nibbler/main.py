#! /usr/local/bin/python
import asyncio, aiohttp
import signal, os
import base64

class GracefulKiller:
  kill_now = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self,signum, frame):
    self.kill_now = True


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


async def dispatch_worker(http_session=None, path=None):
    url = f"http://localhost:8000{path}"
    print(f"About to POST {url}")
    return await http_session.post(url)


async def mark_complete(http_session=None, nibble_id=None):
    print(f"Marking complete for nibble {nibble_id}")
    url = f"http://{vendor}/nibble/{nibble_id}/complete"
    return await http_session.get(url)


async def mark_error(http_session=None, nibble_id=None):
    print(f"Marking error for nibble {nibble_id}")
    url = f"http://{vendor}/nibble/{nibble_id}/error"
    return await http_session.get(url)
from pprint import pprint as pp

async def send_nibbles_init(job = None, http_session=None, data=None):
    url = f"http://{vendor}/nibbles/{job}/init"
    pp(data)
    print("Sending that^^ to vendor!")
    return await http_session.post(url, json=data)


async def main(vendor, job, delay):
    await asyncio.sleep(2)
    killer = GracefulKiller()
    job = base64.b64encode(job.encode('ascii')).decode('ascii')
    url = f"http://{vendor}/job/lease/{job}"
    while not killer.kill_now:
        await asyncio.sleep(delay/1000)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()
                if resp.status == 201:
                    token = data['token']
                    results = await dispatch_worker(http_session=session, path=token)
                    if results.status == 200:
                        if token == '/init/nibbles':
                            nibbles_data = await results.json()
                            await send_nibbles_init(job=job, http_session=session, data=nibbles_data)
                        print("Good!")
                        await mark_complete(http_session=session, nibble_id=data['nibble_id'])
                    else:
                        print("Bad result from worker")
                        pp(results)
                        await mark_error(http_session=session, nibble_id=data['nibble_id'])
                else:
                    pp(resp)
                    print("Bad results from vendor!!", flush=True)
                    # await mark_error(http_session=session, nibble_id=data['nibble_id'])
                print(resp.status)
                print(await resp.text())
        print("doing something in a loop ...", flush=True)

    print("Exiting!")

if __name__ == "__main__":
    vendor = os.environ.get('VENDOR_URL', '')
    job = os.environ.get('JOB_KEY', 'fetch-symbols')
    delay = int(os.environ.get('DELAY_MS', '1000'))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(vendor=vendor, job=job, delay=delay))
    loop.close()
