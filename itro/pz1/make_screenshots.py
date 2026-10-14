# Renders the validator console log and XSLT results to PNG for the report (headless Chrome).
# Run after `mvnw compile exec:java > output/validation-log.txt`: python make_screenshots.py
import html
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).parent.resolve()
IMG = HERE / 'img'
OUT = HERE / 'car-rental-specs' / 'output'
CHROME = Path.home() / 'AppData/Local/Google/Chrome/Application/chrome.exe'
IMG.mkdir(exist_ok=True)

log = (OUT / 'validation-log.txt').read_text(encoding='utf-8')
sections = {
    'log-xml': log.split('== 3.')[0],
    'log-generated': '== 3.' + log.split('== 3.')[1].split('== 4.')[0],
    'log-invalid-xml': '== 4.' + log.split('== 4.')[1].split('== 5.')[0],
    'log-json': '== 5.' + log.split('== 5.')[1],
}


def shot(name, url, size):
    with tempfile.TemporaryDirectory() as profile:  # isolated profile: never touches the user's running Chrome
        subprocess.run([str(CHROME), '--headless=new', f'--user-data-dir={profile}', '--disable-gpu',
                        '--hide-scrollbars', f'--window-size={size}', f'--screenshot={IMG / (name + ".png")}', url],
                       capture_output=True, timeout=120)
    trim(IMG / (name + '.png'))
    print(name, (IMG / (name + '.png')).exists())


def trim(png):
    from PIL import Image, ImageChops  # crop the empty background below/right of the content
    im = Image.open(png).convert('RGB')
    bg = Image.new('RGB', im.size, im.getpixel((im.width - 1, im.height - 1)))
    box = ImageChops.difference(im, bg).getbbox()
    if box:
        im.crop((0, 0, min(im.width, box[2] + 24), min(im.height, box[3] + 24))).save(png)


with tempfile.TemporaryDirectory() as tmp:
    for name, text in sections.items():
        lines = text.strip().count('\n') + 1
        page = Path(tmp) / f'{name}.html'
        page.write_text('<html><body style="margin:0;background:#1e1e1e"><pre style="font:13px Consolas,monospace;'
                        'color:#d4d4d4;padding:12px;margin:0;white-space:pre-wrap">' + html.escape(text.strip()) +
                        '</pre></body></html>', encoding='utf-8')
        shot(name, page.as_uri(), f'1300,{lines * 18 + 40}')

shot('xslt-all', (OUT / 'car-rental.html').as_uri(), '1200,1750')
shot('xslt-filtered', (OUT / 'car-rental-available.html').as_uri(), '1200,1250')
