try:
    from PIL import Image, ImageDraw, ImageFont, ImageOps
except ImportError:
    import Image, ImageDraw, ImageFont, ImageOps
from cStringIO import StringIO

BLACK = (0, 0, 0, 255)
TRANSPARENT = (0, 0, 0, 0)


class CaptchaImage:

    def __init__(self, text, font=ImageFont.load_default()):
        self.text = " " + text + " "
        size = font.getsize(self.text)
        self.img = Image.new('RGBA', size, BLACK)
        draw = ImageDraw.Draw(self.img)
        draw.text((0, 0), self.text, font=font, fill=TRANSPARENT)
        self.mask = self.img.split()[3]

    def deform_text(self):
        import random
        project = lambda orig, dist: orig + random.randint(-1 * dist, dist)

        divisions = len(self.text) / 2
        distorsion = dict(x=10, y=30)
        margin_img_size = (
            self.img.size[0] + (2 * distorsion['x']),
            self.img.size[1] + (2 * distorsion['y']),
        )
        margins_img = Image.new('RGBA', margin_img_size, TRANSPARENT)
        margins_img.paste(self.img, (distorsion['x'], distorsion['y']))
        self.img = margins_img

        last_projected_x = last_projected_y = 0
        mesh = []
        for pos in xrange(divisions+1):
            x0 = self.img.size[0] / divisions * pos
            x1 = self.img.size[0] / divisions * (pos + 1)
            y0 = 0
            y1 = self.img.size[1]

            projected_x = project(x1, distorsion['x'])
            projected_y = project(y0, distorsion['y'])

            mesh.append((
                (x0, y0, x1, y1),
                (
                    last_projected_x, last_projected_y,
                    x0, y1,
                    x1, y1,
                    projected_x, projected_y,
                ),
            ))
            last_projected_x, last_projected_y = projected_x, projected_y

        self.img = self.img.transform(self.img.size, Image.MESH, mesh, Image.BICUBIC)
        self.img = self.img.crop(self.img.getbbox())

    def colorize_text(self, color_file):
        col_img = Image.open(color_file, 'r')
        col_img = col_img.resize(self.img.size)
        self.img = Image.composite(self.img, col_img, mask=self.mask)

    def make_transparent_bg(self):
        transparent_img = Image.new('RGBA', self.img.size, TRANSPARENT)
        reverted_mask = ImageOps.invert(self.mask)
        self.img = Image.composite(self.img, transparent_img, mask=reverted_mask)

    def get_image(self, format='PNG'):
        result = StringIO()
        self.img.save(result, format)
        result.seek(0)
        return result.read()
