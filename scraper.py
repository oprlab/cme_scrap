import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://www.nbcnews.com/business",
        )
        print("--- Czysty Markdown ---")
        print(result.markdown.raw_markdown)

if __name__ == "__main__":
    asyncio.run(main())
