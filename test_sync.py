import asyncio
from googletrans import Translator
import sys

def translate_to_roman(text):
    async def run_translation():
        try:
            translator = Translator()
            res = await translator.translate(text, dest='hi')
            translations = res.extra_data.get('translation', [])
            for item in translations:
                if isinstance(item, list) and len(item) >= 3 and isinstance(item[2], str):
                    return item[2].replace('।', '.')
        except Exception as e:
            return str(e)
        return None
        
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(run_translation())
        loop.close()
        return result
    except Exception as e:
        return str(e)

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

print(translate_to_roman("Multithreading is awesome."))
