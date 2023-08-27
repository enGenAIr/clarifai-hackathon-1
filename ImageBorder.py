import random

from PIL import Image, ImageOps, ImageDraw, ImageFilter, ImageChops, ImageFont


class ImageBorder:

    @staticmethod
    def basic_polaroid(img):
        width, height = img.size
        top_border = int(height * 0.05)
        side_border = int(width * 0.05)
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
        width, height = img.size
        border_height = int(height * 0.15)  # Space for text
        border_color = (255, 253, 208)  # Cream frame color

        img = ImageOps.expand(img, border=(0, border_height, 0, 0), fill=border_color)

        if text:
            draw = ImageDraw.Draw(img)
            text_font = ImageFont.truetype("path_to_your_font.ttf", 12)
            text_width, text_height = draw.textsize(text, font=text_font)
            text_position = ((width - text_width) // 2, height + border_height)
            draw.text(text_position, text, fill=(255, 255, 255), font=text_font)

        return img











