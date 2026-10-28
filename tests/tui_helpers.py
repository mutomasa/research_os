"""TUI テストの共通ヘルパー。"""

import asyncio

from textual.content import Content

from research_os.tui.app import ResearchOSApp


def run(coro_fn, app=None, size=(120, 36)):
    """Textual の run_test を pytest-asyncio なしで回す。"""
    app = app or ResearchOSApp(research_theme="vision tactile world model")

    async def main():
        async with app.run_test(size=size) as pilot:
            await coro_fn(app, pilot)

    asyncio.run(main())


def text_of(widget) -> str:
    return widget.render().plain


def title_of(widget) -> str:
    return Content.from_markup(widget.border_title).plain
