"""Record a video of the full Vicarious demo flow for review.

Drives: load → Pay $1 → watch live frames → Gamify → generated world video.
Saves a .webm to dev/. Run: uv run python dev/record_demo.py
"""
import asyncio
from pathlib import Path

from playwright.async_api import async_playwright

OUT = Path(__file__).parent / "recording"


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await browser.new_context(
            viewport={"width": 440, "height": 900},
            record_video_dir=str(OUT),
            record_video_size={"width": 440, "height": 900},
        )
        page = await ctx.new_page()
        await page.goto("http://localhost:8000/")
        await page.wait_for_timeout(1500)

        # Pay → live
        await page.click('button[onclick="pay()"]')
        await page.wait_for_timeout(4000)  # let a few real frames stream in

        # Gamify → real fal generation (~35-50s)
        await page.click("#gamifyBtn")
        # wait until the generated <video> is loaded, or time out
        try:
            await page.wait_for_function(
                "() => { const v=document.getElementById('worldvid');"
                "return v && !v.classList.contains('hidden') && v.readyState>=3; }",
                timeout=90000,
            )
        except Exception:
            pass
        await page.wait_for_timeout(6000)  # let the generated clip play on camera

        await ctx.close()  # finalizes the video
        await browser.close()

    vids = sorted(OUT.glob("*.webm"))
    print("recorded:", vids[-1] if vids else "NONE")


if __name__ == "__main__":
    asyncio.run(main())
