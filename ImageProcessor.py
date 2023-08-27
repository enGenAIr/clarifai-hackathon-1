import textwrap
from turtle import st

from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw, ImageFont
from ImageBorder import ImageBorder
import numpy as np

class ImageProcessor:
    def __init__(self, image):
        self.image = image

    # def apply_filter(self, filter_option):
    #     filters = {
    #         'Blur': ImageFilter.BLUR,
    #         "Black & White": ImageFilter.UnsharpMask(radius=2, percent=150),
    #         "Dramatic": ImageEnhance.Contrast(self.image),
    #     }
    #     if filter_option in filters:
    #         self.image = self.image.filter(filters[filter_option])

    def apply_filter(self, filter_option):
        self.image = self.return_filter(filter_option)


    def return_filter(self, filter_name):
        if filter_name == "Original":
            return self.image
        elif filter_name == "Black & White":
            grayscale = ImageOps.grayscale(self.image)
            return grayscale.convert("RGB")
        elif filter_name == "Dramatic":
            enhancer = ImageEnhance.Contrast(self.image)
            return enhancer.enhance(1.5)
        elif filter_name == "Vignette":
            vintage_filter = self.image.convert("RGB")

            # Apply Gaussian blur
            vintage_filter = vintage_filter.filter(ImageFilter.GaussianBlur(radius=2))

            # Apply color adjustments for the retro effect
            enhancer = ImageEnhance.Color(vintage_filter)
            vintage_filter = enhancer.enhance(0.7)  # Reduce color saturation

            enhancer = ImageEnhance.Brightness(vintage_filter)
            vintage_filter = enhancer.enhance(0.8)  # Reduce brightness

            enhancer = ImageEnhance.Contrast(vintage_filter)
            vintage_filter = enhancer.enhance(1.2)  # Increase contrast

            # Apply color tint (brownish tone)
            for y in range(vintage_filter.height):
                for x in range(vintage_filter.width):
                    r, g, b = vintage_filter.getpixel((x, y))
                    r = min(255, int(r * 1.2))
                    g = min(255, int(g * 0.9))
                    b = min(255, int(b * 0.7))
                    vintage_filter.putpixel((x, y), (r, g, b))

            return vintage_filter
        elif filter_name == "Sepia":
            sepia_filter = self.image.copy()

            for y in range(sepia_filter.height):
                for x in range(sepia_filter.width):
                    r, g, b = sepia_filter.getpixel((x, y))
                    new_r = int(0.272 * r + 0.534 * g + 0.131 * b)
                    new_g = int(0.349 * r + 0.686 * g + 0.168 * b)
                    new_b = int(0.393 * r + 0.769 * g + 0.189 * b)
                    sepia_filter.putpixel((x, y), (new_r, new_g, new_b))

            return sepia_filter
        elif filter_name == "Inverted Color":
            invert_filter = self.image.copy()

            for y in range(invert_filter.height):
                for x in range(invert_filter.width):
                    r, g, b = invert_filter.getpixel((x, y))
                    inverted_r = 255 - r
                    inverted_g = 255 - g
                    inverted_b = 255 - b
                    invert_filter.putpixel((x, y), (inverted_r, inverted_g, inverted_b))

            return invert_filter
        elif filter_name == "Comic Filter":
            comic_filter = self.image.copy()

            for y in range(comic_filter.height):
                for x in range(comic_filter.width):
                    r, g, b = comic_filter.getpixel((x, y))
                    new_r = abs(g - b + g + r) % 256
                    new_g = abs(b - g + b + r) % 256
                    new_b = abs(b - g + b + r) % 256
                    comic_filter.putpixel((x, y), (new_r, new_g, new_b))

            return comic_filter
        elif filter_name == "Oil Painting":
            brush_size = 5
            oil_painting_filter = self.image.copy()

            width, height = oil_painting_filter.size
            pixels = np.array(oil_painting_filter)

            for y in range(brush_size, height - brush_size):
                for x in range(brush_size, width - brush_size):
                    window = pixels[y - brush_size: y + brush_size + 1, x - brush_size: x + brush_size + 1]

                    r_values = window[:, :, 0].flatten()
                    g_values = window[:, :, 1].flatten()
                    b_values = window[:, :, 2].flatten()

                    new_r = np.median(r_values)
                    new_g = np.median(g_values)
                    new_b = np.median(b_values)

                    pixels[y, x] = [new_r, new_g, new_b]

            return Image.fromarray(pixels.astype(np.uint8))
        elif filter_name == "Sharp":
          return self.image.filter(ImageFilter.UnsharpMask(radius=2, percent=250))
        elif filter_name == "Water Color":
            brush_size = 8
            image_array = np.array(self.image)
            height, width, channels = image_array.shape

            result_array = np.zeros_like(image_array)

            for y in range(brush_size, height - brush_size):
                for x in range(brush_size, width - brush_size):
                    x0, y0 = x - brush_size, y - brush_size
                    x1, y1 = x + brush_size, y + brush_size
                    region = image_array[y0:y1, x0:x1]

                    # Apply median filter to create blending effect
                    filtered_region = np.median(region, axis=(0, 1))

                    result_array[y, x] = filtered_region

            return Image.fromarray(result_array.astype(np.uint8))
        elif filter_name == "Cool":
            return ImageEnhance.Color(self.image).enhance(0.9)
        elif filter_name == "Warm":
            enhancer = ImageEnhance.Color(self.image)
            return enhancer.enhance(3.5)
        elif filter_name == "Blur":
            return self.image.filter(ImageFilter.GaussianBlur(radius=3))
        elif filter_name == "Solarize":
            solarized = ImageOps.solarize(self.image, threshold=170)
            return solarized

        elif filter_name == "Pop Art":
            pop_art = self.image.convert("RGB")
            enhancer = ImageEnhance.Color(pop_art)
            pop_art = enhancer.enhance(4.0)  # Adjust this for stronger or weaker effect
            return pop_art
        elif filter_name == "Lomo":
            lomo = self.image.convert("RGB")
            enhancer = ImageEnhance.Color(lomo)
            lomo = enhancer.enhance(1.5)
            wide = lomo.width
            high = lomo.height
            pixels = lomo.load()
            for y in range(high):
                for x in range(wide):
                    r, g, b = pixels[x, y]
                    tr = int(r * 0.9)
                    tg = int(g * 1.1)
                    if tg > 255:
                        tg = 255
                    tb = b
                    pixels[x, y] = tr,tg,tb
            return lomo
        else:
            raise ValueError("Filter not implemented!")
    def resize(self, width, height):
        self.image = self.image.resize((width, height))

    def add_text(self, text, position_option, font_color, bg_color=None, font_size=20):
        draw = ImageDraw.Draw(self.image)
        try:
            font = ImageFont.truetype("Arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()
            st.warning("Using default font. Font size will not be adjustable.")

        wrapped_text = textwrap.fill(text, width=30)
        text_bbox = draw.textbbox((0, 0), wrapped_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        position_map = {
            'Top Left': (10, 10),
            'Top Center': ((self.image.width - text_width) // 2, 10),
            'Top Right': (self.image.width - text_width - 10, 10),
            'Bottom Left': (10, self.image.height - text_height - 10),
            'Bottom Center': ((self.image.width - text_width) // 2, self.image.height - text_height - 10),
            'Bottom Right': (self.image.width - text_width - 10, self.image.height - text_height - 10),
            'Center': ((self.image.width - text_width) // 2, (self.image.height - text_height) // 2)
        }

        position = position_map[position_option]

        if bg_color:
            draw.rectangle([position, (position[0] + text_width, position[1] + text_height)], fill=bg_color)

        draw.text(position, wrapped_text, fill=font_color, font=font)

    def save(self, path):
        self.image.save(path)
    def apply_border(self, border_type, text=None):
        if border_type == 'Polaroids':
            self.image = ImageBorder.basic_polaroid(self.image)
        elif border_type == 'Vintage Frame':
            self.image = ImageBorder.vintage_frame(self.image)
        elif border_type == 'Wooden Frame':
            self.image = ImageBorder.wooden_frame(self.image)
        elif border_type == 'Bohemian Bliss Frame':
            self.image = ImageBorder.bohemian_bliss_frame(self.image)

        elif border_type == 'Filmstrip Border':
            self.image = ImageBorder.filmstrip_border(self.image, text)
        elif border_type == 'Grunge Border':
            self.image = ImageBorder.grunge_border(self.image, text)
        elif border_type == 'Pixel Frame':
            self.image = ImageBorder.pixel_frame(self.image)
        elif border_type == 'Framed Border':
            self.image = ImageBorder.pixel_frame(self.image)
        elif border_type == 'Cartoon Frame':
            self.image = ImageBorder. cartoon_frame(self.image)
        elif border_type == 'Bubble Frame':
            self.image = ImageBorder. bubble_frame(self.image)
        elif border_type == 'Glitch Frame':
            self.image = ImageBorder. glitch_frame(self.image)
