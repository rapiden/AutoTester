import os
import sys
import colorsys
import pickle
from PIL import Image, ImageDraw
from Exceptions import ImageComparatorError


class PKLGenerator:
    @staticmethod
    def pkl_to_image(pkl_file):
        try:
            with open(pkl_file, 'rb') as f:
                dic_pattern = pickle.load(f)

            img_result = PKLGenerator.draw_image(dic_pattern)

        except EOFError:
            raise ImageComparatorError(f'Invalid .pkl file: {pkl_file}')

        return img_result, dic_pattern

    @staticmethod
    def draw_image(dic_pattern):
        img_result = Image.new(size=dic_pattern['Size'], mode='RGBA')
        draw = ImageDraw.Draw(img_result)
        for pixel in dic_pattern['Data']:
            int_x = pixel['X']
            int_y = pixel['Y']
            tpl_rgba = pixel['RGBA']

            draw.point((int_x, int_y), tpl_rgba)
        return img_result

    @staticmethod
    def generate(png_file, r, g, b, a, rp_x, rp_y, pkl_file, show=True):
        """
        :param png_file: PNG File name
        :param r: R color
        :param g: G color
        :param b: B color
        :param a: A color
        :param rp_x: Reffernce Point X
        :param rp_y: Reffernce Point Y
        :param pkl_file: PKL Filename
        :param show: show to result image or not (default: show)
        :return: PKL File
        """
        rgba_image = Image.open(png_file)
        dic_pattern = PKLGenerator.get_pattern(rgba_image.convert('RGBA'), (r, g, b, a), (rp_x, rp_y))

        # Save pkl
        with open(pkl_file, 'wb') as f:
            pickle.dump(dic_pattern, f, pickle.HIGHEST_PROTOCOL)

        # Draw image and show if asked to
        if show:
            PKLGenerator.draw_image(dic_pattern).show()

    @staticmethod
    def show(pkl_file):
        """
        :param pkl_file: PKL File to show
        :return:
        """
        if os.path.isfile(pkl_file) is False:
            return print("Could not find GoldenImage.")

        img_result, dic_pattern = PKLGenerator.pkl_to_image(pkl_file)

        print("Pattern Date:")
        print("-------------")

        print("RP Offset (w,h): " + str(dic_pattern["RP_Offset"]))
        print("Pattern Box (X0,Y0,X1,Y1): " + str(dic_pattern["Box"]))
        print("Pattern Size (w,h): " + str(dic_pattern["Size"]))

        img_result.show()

    @staticmethod
    def get_pattern(imgRGBAImage, tplTransRGBA, tplRP=()):

        dicTransparentImage = {}
        lstMaskArry = []
        dicPixData = {}
        intXstart = 0
        intYstart = 0

        RPxOffset = None
        RPyOffset = None

        pixdata = imgRGBAImage.load()
        width, height = imgRGBAImage.size
        for y in range(height):
            for x in range(width):
                # print(pixdata[x, y])
                if pixdata[x, y] != tplTransRGBA:
                    dicPixData['X'] = x
                    dicPixData['Y'] = y
                    dicPixData['RGBA'] = pixdata[x, y]
                    dicPixData['HLS'] = PKLGenerator.GetPixelHSL(dicPixData['RGBA'])

                    lstMaskArry.append(dicPixData)
                    dicPixData = {}

        startX = min(lstMaskArry, key=lambda x: x['X'])
        startY = min(lstMaskArry, key=lambda x: x['Y'])
        EndX = max(lstMaskArry, key=lambda x: x['X'])
        EndY = max(lstMaskArry, key=lambda x: x['Y'])

        if (tplRP != None):
            print(tplRP)
            RPxOffset = tplRP[0] - startX['X']
            RPyOffset = tplRP[1] - startY['Y']

            print("RP Offset: " + str((RPxOffset, RPyOffset)))

        tplObjectBox = (startX['X'], startY['Y'], EndX['X'], EndY['Y'])
        tplObjectSize = ((EndX['X'] - startX['X']) + 1, (EndY['Y'] - startY['Y']) + 1)

        dicTransparentImage['Data'] = lstMaskArry
        dicTransparentImage['Box'] = tplObjectBox
        dicTransparentImage['Size'] = tplObjectSize
        dicTransparentImage['RP_Offset'] = (RPxOffset, RPyOffset)

        # Crop Pattern to match BOX (Set Pattern 0,0 to BOX upper left)
        for pixel in dicTransparentImage['Data']:
            pixel['X'] = pixel['X'] - dicTransparentImage['Box'][0]
            pixel['Y'] = pixel['Y'] - dicTransparentImage['Box'][1]

        print(dicTransparentImage['Size'])

        ##    for dicData in dicTransparentImage['Data']:
        ##        print(str(dicData["HLS"]))

        return dicTransparentImage

    @staticmethod
    def GetPixelHSL(tplRGBA):
        r = tplRGBA[0] / 255.
        g = tplRGBA[1] / 255.
        b = tplRGBA[2] / 255.

        # print(colorsys.rgb_to_hls(r, g, b))

        h, l, s = colorsys.rgb_to_hls(r, g, b)

        return (h * 240, l * 240, s * 240)

    @staticmethod
    def cmd_execute():
        lst_arguments = sys.argv
        script_name = lst_arguments[0]
        if len(lst_arguments) < 2:
            print(f"Usage: python {script_name} [filename.png]")
        elif len(lst_arguments) == 2:
            PKLGenerator.show(lst_arguments[1])
        elif len(lst_arguments) == 9:
            png_file = lst_arguments[1]
            if os.path.isfile(png_file) is False:
                return print("Could not find GoldenImage PNG.")
            color_r = int(lst_arguments[2])
            color_g = int(lst_arguments[3])
            color_b = int(lst_arguments[4])
            color_a = int(lst_arguments[5])
            rp_x = float(lst_arguments[6])
            rp_y = float(lst_arguments[7])
            pkl_file = str(lst_arguments[8])
            PKLGenerator.generate(png_file, color_r, color_g, color_b, color_a, rp_x, rp_y, pkl_file)
        else:
            print(f"Usage: python {script_name} [filename.png] [R] [G] [B] [A] [RPx] [RPy] [filename.pkl]")


if __name__ == "__main__":
    PKLGenerator.cmd_execute()
