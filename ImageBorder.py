import math
import random

from PIL import Image, ImageOps, ImageDraw, ImageFilter, ImageChops, ImageFont


class ImageBorder:

    @staticmethod
    def basic_polaroid(img):
        width, height = img.size
        top_border = int(height * 0.02)
        side_border = int(width * 0.02)
        bottom_border = int(height * 0.25)
        borders = (side_border, top_border, side_border, bottom_border)
        return ImageOps.expand(img, border=borders, fill="white")
    @staticmethod
    def vintage_frame(img):
        width, height = img.size
        border_width = int(width * 0.1)
        border_color = (248, 227, 196)  # Cream color for a vintage feel
        img = ImageOps.expand(img, border=border_width, fill=border_color)
        draw = ImageDraw.Draw(img)
        for i in range(border_width):
            draw.rectangle([i, i, width - i - 1, height - i - 1],
                           outline=(240 - (i // 3), 220 - (i // 3), 190 - (i // 3)))
        return img
    @staticmethod
    def framed_border(img, text=None):
        width, height = img.size
        frame_width = int(width * 0.08)
        frame_color = (100, 100, 100)  # Dark gray frame

        img = ImageOps.expand(img, border=frame_width, fill=frame_color)

        if text:
            draw = ImageDraw.Draw(img)
            text_font = ImageFont.truetype("path_to_your_font.ttf", 12)
            text_width, text_height = draw.textsize(text, font=text_font)
            text_position = (frame_width // 2, (height - text_height) // 2)
            draw.text(text_position, text, fill=(255, 255, 255), font=text_font)

        return img
    @staticmethod
    def grunge_border(img, text=None):
        width, height = img.size
        border_width = int(width * 0.05)
        border_color = (160, 160, 160)  # Grayish border

        img = ImageOps.expand(img, border=border_width, fill=border_color)

        if text:
            draw = ImageDraw.Draw(img)
            text_font = ImageFont.truetype("path_to_your_font.ttf", 12)
            text_width, text_height = draw.textsize(text, font=text_font)
            text_position = ((width - text_width) // 2, height + border_width)
            draw.text(text_position, text, fill=(0, 0, 0), font=text_font)

        return img
    @staticmethod
    def filmstrip_border(img, text=None):
        border_color = "white"
        left_border, top_border, right_border, bottom_border = 10, 50, 10, 10
        new_img = Image.new("RGB", (img.width + left_border + right_border,
                                    img.height + top_border + bottom_border), border_color)
        new_img.paste(img, (left_border, top_border))
        draw = ImageDraw.Draw(new_img)
        for x in range(0, new_img.width, 4):
            for y in range(0, new_img.height, 4):
                if (x + y) % 8 == 0:
                    draw.point((x, y), fill="brown")
        return new_img



    @staticmethod
    def bohemian_bliss_frame(img):
        # Bohemian Bliss: Patterned borders with a tribal touch
        left_border, top_border, right_border, bottom_border = 20, 20, 20, 60
        pattern_colors = ["#FFD700", "#FF4500", "#4B0082", "#6B8E23"]
        new_img = Image.new("RGB", (img.width + left_border + right_border,
                                    img.height + top_border + bottom_border), "#D2B48C")  # Tan background
        new_img.paste(img, (left_border, top_border))
        draw = ImageDraw.Draw(new_img)

        for i in range(0, left_border):
            for y in range(0, new_img.height):
                if (i + y) % 4 == 0:
                    draw.point((i, y), fill=random.choice(pattern_colors))

        for i in range(new_img.width - right_border, new_img.width):
            for y in range(0, new_img.height):
                if (i + y) % 4 == 0:
                    draw.point((i, y), fill=random.choice(pattern_colors))

        for i in range(0, top_border):
            for x in range(0, new_img.width):
                if (i + x) % 4 == 0:
                    draw.point((x, i), fill=random.choice(pattern_colors))

        for i in range(new_img.height - bottom_border, new_img.height):
            for x in range(0, new_img.width):
                if (i + x) % 4 == 0:
                    draw.point((x, i), fill=random.choice(pattern_colors))

        return new_img

    @staticmethod
    def pixel_frame(img):
        # Crystalline Contour: Shimmering crystal-like edges
        border_color = "#A9ACB6"
        left_border, top_border, right_border, bottom_border = 50, 50, 50, 50
        new_img = Image.new("RGB", (img.width + left_border + right_border,
                                    img.height + top_border + bottom_border), border_color)
        new_img.paste(img, (left_border, top_border))
        draw = ImageDraw.Draw(new_img)
        for x in range(0, new_img.width, 5):
            for y in [y for y in range(0, top_border, 5)] + [y for y in
                                                             range(new_img.height - bottom_border, new_img.height, 5)]:
                crystal_color = random.choice(["#FFFFFF", "#D3D3D3", "#C0C0C0"])
                draw.rectangle((x, y, x + 5, y + 5), fill=crystal_color)
        for y in range(0, new_img.height, 5):
            for x in [x for x in range(0, left_border, 5)] + [x for x in
                                                              range(new_img.width - right_border, new_img.width, 5)]:
                crystal_color = random.choice(["#FFFFFF", "#D3D3D3", "#C0C0C0"])
                draw.rectangle((x, y, x + 5, y + 5), fill=crystal_color)

        return new_img
    @staticmethod
    def cartoon_frame(img):
        # Holographic Halo: Shimmering border with a holographic effect
        border_color = "#DAA520"  # goldenrod
        left_border, top_border, right_border, bottom_border = 10, 20, 10, 30
        new_img = Image.new("RGB", (img.width + left_border + right_border,
                                    img.height + top_border + bottom_border), border_color)
        new_img.paste(img, (left_border, top_border))
        draw = ImageDraw.Draw(new_img)
        halo_colors = ["#EE82EE", "#ADD8E6", "#FFB6C1", "#90EE90"]

        for i in range(100):  # Random holographic patterns
            x = random.randint(0, new_img.width)
            y = random.randint(0, top_border)
            s = random.randint(5, 20)
            draw.rectangle((x - s, y - s, x + s, y + s), fill=random.choice(halo_colors), outline="#DAA520", width=2)

            y = random.randint(new_img.height - bottom_border, new_img.height)
            draw.rectangle((x - s, y - s, x + s, y + s), fill=random.choice(halo_colors), outline="#DAA520", width=2)

        return new_img

    @staticmethod
    def bubble_frame(img):
        # Ice Frost: Icy, frosty edge around the image
        border_thickness = 30
        new_img = Image.new("RGB", (img.width + 2 * border_thickness, img.height + 2 * border_thickness),
                            "pink")  # Light blue background
        new_img.paste(img, (border_thickness, border_thickness))

        draw = ImageDraw.Draw(new_img)
        for _ in range(100):
            x = random.randint(0, new_img.width)
            y = random.randint(0, border_thickness)
            length = random.randint(10, 30)
            draw.arc((x - length, y - length, x + length, y + length), 0, 180, fill="#FFFFFF")

            y = new_img.height - y
            draw.arc((x - length, y - length, x + length, y + length), 180, 360, fill="#FFFFFF")

        return new_img

    @staticmethod
    def glitch_frame(img):
        # Adds a digital glitch effect on the borders
        border_thickness = 40
        new_img = ImageOps.expand(img, border=border_thickness, fill='black')
        for y in range(new_img.height):
            if y % 15 == 0:
                shift = int((border_thickness / 2) * (0.5 - random.random()))
                part = new_img.crop((0, y, new_img.width, y + 15))
                new_img.paste(part, (shift, y))
        return new_img

    @staticmethod
    def wooden_frame(img):
        texture_path = 'frame.jpg'
        border_thickness = 50

        # Load the wood texture
        texture = Image.open(texture_path)

        # Create an expanded image with white borders
        bordered_img = Image.new('RGB', (img.width + 2 * border_thickness, img.height + 2 * border_thickness), 'white')
        bordered_img.paste(img, (border_thickness, border_thickness))

        # Create the wooden texture mask: White for areas to retain the wood texture, black for other areas
        mask = Image.new('L', bordered_img.size, 0)
        mask.paste(255,
                   (border_thickness, border_thickness, img.width + border_thickness, img.height + border_thickness))

        # Tile the wood texture to cover the entire image
        tiled_texture = Image.new('RGB', bordered_img.size)
        for i in range(0, bordered_img.width, texture.width):
            for j in range(0, bordered_img.height, texture.height):
                tiled_texture.paste(texture, (i, j))

        # Composite the bordered image and the tiled texture using the mask
        result = Image.composite(bordered_img, tiled_texture, mask)

        return result



