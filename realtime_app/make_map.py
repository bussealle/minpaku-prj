import json
import sys
import pytz
from datetime import datetime
from PIL import Image, ImageDraw, ImageColor, ImageFont


backimg = Image.open('minpaku_map_vectored.png')
canvas_size = backimg.size
draw = ImageDraw.Draw(backimg)
UUID = "5acf2bbbb7221801b3da001c4d3514ae"
SCALE = 150
fontpath = "data/Ricty-Regular.ttf" #{}"/Users/admin/Library/Fonts/Ricty-Regular.ttf"
fontsize = 100
with open('beacons.json','r') as bjson:
    beacon_pos = json.load(bjson)

images = []
alpha = 0.2
fill = ImageColor.getrgb("red")
jst = pytz.timezone('Asia/Tokyo')

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
    pixelzoom = 3333/800
    center = (center[0]*pixelzoom,center[1]*pixelzoom)
    return (center[0]-radius,center[1]-radius,center[0]+radius,center[1]+radius)

def make_map(beacon):
    data = beacon['data']
    time = beacon['time']
    text = datetime.fromtimestamp(int(time)).astimezone(jst).strftime('%Y-%m-%d %H:%M:%S')
    font = ImageFont.truetype(fontpath, fontsize, encoding="utf-8")
    pos = []
    ds = data.get(UUID)
    if ds :
        new_ds = []
        for i in range(len(ds)):
            d = ds[i]
            minor = d['minor']
            if minor in [x['minor'] for x in new_ds]:
                continue
            temp = [x for x in ds if x['minor']==minor]
            new_rssi = sum([x['rssi'][0] for x in temp])/len(temp)
            new_txp = sum([x['txp'][0] for x in temp])/len(temp)
            d['rssi'][0] = new_rssi
            d['txp'][0] = new_txp
            new_ds.append(d)
        for d in new_ds:
            rssi = d['rssi'][0]
            txp = d['txp'][0]
            num = d['minor']
            radius = pow(10, (txp - rssi) / 20) #meter
            center = beacon_pos[str(num)]['position']
            #print(radius)
            pos.append(make_cir(radius*SCALE,center))
    canvas = draw_transparent_text(backimg, pos=pos, fill=fill, alpha=alpha, text=text, font=font)
    canvas = canvas.resize((350, 350), Image.HAMMING)
    #images.append(canvas)
    canvas.save('map.png', "PNG")

#images[0].save('result.gif', save_all=True, append_images=images[1:], optimize=True, duration=60, loop=0)
