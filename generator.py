"""
This program generate matrix gif, that show the letters into the screen and moving it
"""
import os
import math
import shutil
from random import randint

from PIL import Image, ImageDraw, ImageFont
import imageio

# global variables
image_width, image_height = (1920, 1080)  # the size of images and gif
frames = 150  # frames in the gif

min_letter_height: int = 30
max_letter_height: int = 31

letter_height: float = (max_letter_height + min_letter_height) / 2  # avarage letter's height
column_letters_count: int = math.ceil(image_height / letter_height)  # letters in one column

letters_font: dict = {}  # dict for font objects for each letter


class LettersColumn:
    letters: list = []
    white_symbol_index: int = 0  # index in letters that shows which the letter should be white color
    _green_count_letters: int = 6  # the count of green color letters before the white color letters

    def change_white_symbol_index(self):
        self.white_symbol_index += 1

        # in the end of column, green letters should be all showed and cleared
        # after the column is fully cleared, it'll create new letters and start showing from begin of column
        # before showing from begin, it'd pass 2 images
        if (self.white_symbol_index - self._green_count_letters) + 2 > column_letters_count:
            self.white_symbol_index = 0
            # self.generate_column_letters()

    # generate letters for one column
    def generate_column_letters(self):
        self.letters = [self.get_random_char() for y in range(column_letters_count)]

    # random char from unicode
    def get_random_char(self):
        return chr(randint(45, 90))

    def define_white_symbol_index(self):
        self.white_symbol_index = randint(0, len(self.letters) - 1)

    @staticmethod
    def get_green_count_letters():
        return LettersColumn._green_count_letters


class ImageDataGenerator:
    def __init__(self):
        self.generate_columns()

    def generate_image(self) -> Image:
        image = Image.new('RGBA', (image_width, image_height), (0, 0, 0))
        draw = ImageDraw.Draw(image)

        column_index = 0
        letter_x = 0
        while letter_x < image_width:
            column = self.columns[column_index]
            column_index += 1

            column_info = self.generate_column_info(column, letter_x)
            column.change_white_symbol_index()

            for letter_info in column_info['letters']:
                draw.text((letter_info['x'], letter_info['y']), letter_info['letter'], letter_info['color'],
                          letter_info['font'])

            letter_x += column_info['column_width']

        return image

    # get need font size that symbol will have need letter height
    def get_fixed_font(self, letter: str):
        font_size = 32

        while True:
            font = ImageFont.truetype('font.ttf', int(font_size))
            letter_height = font.getsize(letter)[1]

            if max_letter_height >= letter_height >= min_letter_height:
                return font

            if letter_height > max_letter_height:
                font_size /= 2
            if letter_height < min_letter_height:
                font_size += 1

    # return info about each letters, in the column
    def generate_column_info(self, column: LettersColumn, letter_x: int) -> dict:
        column_info = {
            'letters': []
        }
        column_width = 0
        letter_y = 0

        # iterate the letters array, generate info about each letter
        for index in range(len(column.letters)):
            letter = column.letters[index]

            font = self.get_font(letter)
            # if it doesn't in dict, save it 
            if letter not in letters_font:
                letters_font[letter] = font

            letter_width, letter_height = font.getsize(letter)
            color = self.get_symbol_color(column.white_symbol_index, index)

            column_info['letters'].append({
                'color': color,
                'font': font,
                'letter': letter,
                'x': letter_x,
                'y': letter_y
            })

            letter_y += letter_height  # add the letter height for position for next symbol

            # set column width as the biggest letter width in the column
            if column_width < letter_width:
                column_width = letter_width

        column_info['column_width'] = column_width  # the width of the column
        return column_info

    def get_font(self, letter):
        # if dict have the font object for need letter get it, otherwise find it
        if letter in letters_font:
            font = letters_font[letter]
        else:
            font = self.get_fixed_font(letter)

        return font

    def get_symbol_color(self, white_letter_index: int, index: int):
        # white letter
        if white_letter_index == index:
            color = (255, 255, 255, 255)  # white color
        # the letters that after white letter or letters that don't green, should be transparent
        elif white_letter_index < index or white_letter_index - LettersColumn.get_green_count_letters() > index:
            color = 'black'  # transparent color
        else:
            color = (0, 128, 0)  # green color

        return color

        # generate columns

    def generate_columns(self):
        columns = []

        for column_count in range(100):
            column = LettersColumn()
            column.generate_column_letters()
            column.define_white_symbol_index()

            columns.append(column)

        self.columns = columns


def main():
    images = []  # images for gif
    generator = ImageDataGenerator()

    if os.path.exists('images'):
        shutil.rmtree('images')
    os.makedirs('images')

    image_index = 1
    while image_index <= frames:
        image = generator.generate_image()
        image.save(f'images/image{image_index}.png')

        images.append(imageio.imread(f'images/image{image_index}.png'))
        image_index += 1

    imageio.mimsave('hacker.gif', images)  # create gif


if __name__ == '__main__':
    main()
