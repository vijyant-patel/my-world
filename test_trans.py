import asyncio
from googletrans import Translator
import sys
import json

async def main():
    try:
        translator = Translator()
        text = "Hello, how are you? Multithreading is a concept in programming."
        res = await translator.translate(text, dest='hi')
        with open("trans_out.json", "w", encoding="utf-8") as f:
            json.dump(res.extra_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Error:", e)

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

asyncio.run(main())
