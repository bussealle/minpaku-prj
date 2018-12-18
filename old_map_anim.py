import json
import sys
import pytz
from datetime import datetime
from PIL import Image, ImageDraw, ImageColor, ImageFont


def draw_transparent_text(src_canvas, pos, fill, alpha, text, font):
    mask = Image.new("L", src_canvas.size, 1)
    draw_canvas = Image.new("RGB", src_canvas.size, "#FFFFFF")
    draw_canvas.putalpha(mask)

    draw = ImageDraw.Draw(draw_canvas)
    for p in pos:
        draw.ellipse(p, fill=fill)
    del draw

    src_canvas.putalpha(mask)
    img = Image.blend(src_canvas, draw_canvas, alpha).convert("RGB")
    draw = ImageDraw.Draw(img)
    draw.text((50,50), text, font=font, fill=ImageColor.getrgb("black"))
    del draw
    return img

def make_cir(radius,center):
    zoom = 3333/800
    center = (center[0]*zoom,center[1]*zoom)
    return (center[0]-radius,center[1]-radius,center[0]+radius,center[1]+radius)

backimg = Image.open('minpaku_map_vectored.png')
canvas_size = backimg.size
draw = ImageDraw.Draw(backimg)
UUID = "5acf2bbbb7221801b3da001c4d3514ae"
fontpath = "Ricty-Regular.ttf" #{}"/Users/admin/Library/Fonts/Ricty-Regular.ttf"
fontsize = 100
beacon_pos = {'1':(696,269), '2':(521,235), '3':(354,235), '6':(66,202), '7':(128,325), '8':(153,524), '9':(70,589), '10':(249,325), '11':(260,563), '12':(328,393), '13':(427,560), '14':(461,469), '15':(535,383)}

images = []
alpha = 0.2
fill = ImageColor.getrgb("red")
jst = pytz.timezone('Asia/Tokyo')

with open('log_2018-11-19_16-39-14.json') as f:
    df = json.load(f)

beacons = df['beacons']
print(len(beacons))

for beacon in beacons:
    data = beacon['data']
    time = beacon['time']
    text = datetime.fromtimestamp(int(time)).astimezone(jst).strftime('%Y-%m-%d %H:%M:%S')
    font = ImageFont.truetype(fontpath, fontsize, encoding="utf-8")
    pos = []
    d = data.get(UUID)
    if d :
        rssi = d['rssi'][0]
        txp = d['txp'][0]
        num = d['minor']
        radius = pow(10, (txp - rssi) / 20) #meter
        center = beacon_pos[str(num)]
        pos.append(make_cir(radius*150,center))
    canvas = draw_transparent_text(backimg, pos=pos, fill=fill, alpha=alpha, text=text, font=font)
    canvas = canvas.resize((350, 350), Image.HAMMING)
    images.append(canvas)
    #canvas.save('newimage.png', "PNG")
    #break

images[0].save('result.gif', save_all=True, append_images=images[1:], optimize=True, duration=60, loop=0)
