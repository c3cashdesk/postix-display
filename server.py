import asyncio
import sys

from aiohttp import web
import pygame
from pygame.locals import QUIT


DEBUG = True
IMAGE = pygame.image.load('assets/closed.png')
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SURFACE = None


async def display_image(app):
    try:
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

            SURFACE.blit(
                source=IMAGE,
                dest=(
                    (SCREEN_WIDTH - IMAGE.get_rect().w)/2,
                    (SCREEN_HEIGHT - IMAGE.get_rect().h)/2,
                ),
            )
            pygame.display.flip()
            await asyncio.sleep(0.1)

    except asyncio.CancelledError:
        pass
    finally:
        pass  # cleanup


async def start_background_tasks(app):
    app['display_image'] = app.loop.create_task(display_image(app))


async def cleanup_background_tasks(app):
    app['display_image'].cancel()
    await app['display_image']


async def serve_open(request):
    global IMAGE
    IMAGE = pygame.image.load('assets/open.png')
    return web.Response()


async def process_next(request):
    global IMAGE
    PATTERN = [2, 1, 2, 1]  # 'c' in morse
    PAUSE = 0.3
    image_open = pygame.image.load('assets/open.png')
    image_inv = pygame.image.load('assets/open-inv.png')

    IMAGE = image_open
    await asyncio.sleep(PAUSE)
    for part in PATTERN:
        IMAGE = image_inv
        await asyncio.sleep(part * PAUSE)
        IMAGE = image_open
        await asyncio.sleep(PAUSE)


async def serve_next(request):
    asyncio.ensure_future(process_next(request))
    return web.Response()


async def serve_close(request):
    global IMAGE
    IMAGE = pygame.image.load('assets/closed.png')
    return web.Response()


def main():
    global SURFACE
    pygame.init()
    SURFACE = pygame.display.set_mode(
        (SCREEN_WIDTH, SCREEN_HEIGHT),  # resolution=,
        not pygame.FULLSCREEN if DEBUG else pygame.FULLSCREEN,  # flags=
        8,  # depth=
    )

    app = web.Application()
    app.router.add_post('/open', serve_open)
    app.router.add_post('/next', serve_next)
    app.router.add_post('/close', serve_close)
    app.on_startup.append(start_background_tasks)
    app.on_cleanup.append(cleanup_background_tasks)

    web.run_app(app)


if __name__ == '__main__':
    main()
