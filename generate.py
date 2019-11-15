#!/usr/bin/env python3
# Invoke like this: ./generate.py output_$(date +%s).png

from PIL import Image
import math
import secrets
import sys


# Used only by run().
# Feel free to replace any function by your own; possibly by `generate.sample_colpoint = lambda ...`
CONTEXT = dict(
    w=1920,
    h=1080,
    colpoints_n=10,
    colpoints_margin=100,
    # Stddev of the noise added to the position:
    samplenoise_stddev=40.0,
    sample_mindist=1e-10,
    # Should be between -inf and 0.  "closer to -inf" makes the colorful blobs "sharper".
    # Positive values make everything weird.
    sample_distalpha=-1.9,
    colorspace_gamma=1.8,
    r=secrets.SystemRandom(),
)


def sample_point(ctx):
    return (ctx['colpoints_margin'] + ctx['r'].random() * (ctx['w'] - 2 * ctx['colpoints_margin']),
            ctx['colpoints_margin'] + ctx['r'].random() * (ctx['h'] - 2 * ctx['colpoints_margin']))


def sample_channel(ctx):
    return ctx['r'].random() ** ctx['colorspace_gamma']


def sample_colpoint(ctx):
    pos = sample_point(ctx)
    rgb = (sample_channel(ctx), sample_channel(ctx), sample_channel(ctx))
    return (pos, rgb)


def noisify_pos(x, y, ctx):
    return (x + ctx['r'].gauss(0, ctx['samplenoise_stddev']),
            y + ctx['r'].gauss(0, ctx['samplenoise_stddev']))


# `x` and `y` can and will be floats!
def sample_pixel_at(x, y, ctx):
    ak_r, ak_g, ak_b = 0, 0, 0
    ak_weight = 0
    for (cp_x, cp_y), (cp_r, cp_g, cp_b) in ctx['colpoints']:
        dx, dy = cp_x - x, cp_y - y
        cp_dist = math.sqrt(dx * dx + dy * dy)
        if cp_dist < ctx['sample_mindist']:
            cp_dist = ctx['sample_mindist']
        cp_weight = cp_dist ** ctx['sample_distalpha']
        ak_r += cp_weight * cp_r
        ak_g += cp_weight * cp_g
        ak_b += cp_weight * cp_b
        ak_weight += cp_weight
    ak_r /= ak_weight
    ak_g /= ak_weight
    ak_b /= ak_weight
    return (ak_r ** (1 / ctx['colorspace_gamma']), ak_g ** (1 / ctx['colorspace_gamma']), ak_b ** (1 / ctx['colorspace_gamma']))


def clamp(v):
    return min(255, max(0, int(v * 256)))


def normalize_rgb(rgb, _ctx):
    r, g, b = rgb
    return (clamp(r), clamp(g), clamp(b))


def generate_image(base_ctx):
    ctx = dict(base_ctx)  # Copy
    ctx['colpoints'] = list()
    for _ in range(ctx['colpoints_n']):
        ctx['colpoints'].append(sample_colpoint(ctx))
    data = []
    for y in range(ctx['h']):
        for x in range(ctx['w']):
            nx, ny = noisify_pos(x, y, ctx)
            rgb = normalize_rgb(sample_pixel_at(nx, ny, ctx), ctx)
            data.append(rgb)
    img = Image.new('RGB', (ctx['w'], ctx['h']))
    img.putdata(data)
    ctx['img'] = img
    return ctx


def run(dst_filename):
    ctx = generate_image(CONTEXT)
    ctx['img'].save(dst_filename, 'png')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Must provide an output filename!\nUSAGE: {} <OUTPUTFILE>'.format(sys.argv[0]), file=sys.stderr)
        exit(1)
    run(sys.argv[1])
