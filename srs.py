import asyncio
import logging
from utils import find_free_port
from flag import random_flag_index
from aiohttp import web

closers = []
runners = []

async def homepage_handler(request):
    return web.HTTPFound('/index.html')

async def homepage(port=8001):
    app = web.Application()
    app.router.add_route('*', '/', homepage_handler)
    app.router.add_static(prefix="/", path="/var/www/html/srs/")
    runner= web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", port)
    logging.info(f"{site.name} starting")
    await site.start()
    runners.append(runner)
    return

class ClosingHandler:
    def __init__(self, exit_event):
        self.exit_event = exit_event

    def next_port():
        return self.next_port

    async def default(self, request):
        self.exit_event.set()
        self.next_port = find_free_port()
        data = {
            "now": request.url.port,
            "next": self.next_port,
            "flag-slice": random_flag_index(),
        }
        return web.json_response(data)

# single request server
async def srs(port=None):

    # create app handler and closing event
    closing_time = asyncio.Event()
    closing_task = asyncio.create_task(closing_time.wait())
    closers.append(closing_time)
    handler = ClosingHandler(closing_time)

    # add handler to new application runner
    app = web.Application()
    app.add_routes([web.get("/", handler.default)])
    runner = web.AppRunner(app)
    await runner.setup()

    # start app on a specific tcp port
    if port == None:
        port = find_free_port()
    site = web.TCPSite(runner, "0.0.0.0", port)
    logging.info(f"{site.name} starting")
    try:
        await site.start()
    except OSError:
        logging.warn(f"port {port} already in use, trying a different one")
        await srs()

    # wait for closing event
    await closing_task
    logging.info(f"{site.name} closing")
    await runner.cleanup()

    await srs(handler.next_port)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    loop = asyncio.get_event_loop()

    loop.create_task(homepage())

    for i in range(100):
        loop.create_task(srs())

    try:
        loop.run_forever()
    except:
        logging.info("\nexiting...")
    finally:
        for c in closers:
            c.set()  # trigger close event which runs runner.cleanup()
        for r in runners:
            loop.create_task(r.cleanup())
