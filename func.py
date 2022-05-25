import os
import re
import shutil
import unicodedata

def rm_if_exists(path, tree=False):
    if os.path.exists(path):
        if tree:
            shutil.rmtree(path)
        else:
            os.remove(path)

def mkdir(path):
    rm_if_exists(path, True)
    os.makedirs(path)

def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')

async def download_image(bot, user_id, file_id, filename):
    file_info = await bot.get_file(file_id)
    file = await bot.download_file(file_info.file_path)
    with open(f"tmp/{user_id}/{filename}.png", 'wb') as f:
        f.write(file)
    return f"tmp/{filename}.png"