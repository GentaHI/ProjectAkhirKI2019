import click
from PIL import Image


class Steganography(object):

    @staticmethod
    def __int_to_bin(rgb):
        """merubah tuple integer ke binary (string) tuple.

        :param rgb: An integer tuple (e.g. (220, 110, 96))
        :return: A string tuple (e.g. ("00101010", "11101011", "00010110"))
        """
        r, g, b = rgb
        return ('{0:08b}'.format(r),
                '{0:08b}'.format(g),
                '{0:08b}'.format(b))

    @staticmethod
    def __bin_to_int(rgb):
        """merubah binary (string) tuple ke integer tuple.

        :param rgb: A string tuple (e.g. ("00101010", "11101011", "00010110"))
        :return: Return an int tuple (e.g. (220, 110, 96))
        """
        r, g, b = rgb
        return (int(r, 2),
                int(g, 2),
                int(b, 2))

    @staticmethod
    def __merge_rgb(rgb1, rgb2):
        """menggabungkan kedua RGB tuples.

        :param rgb1: A string tuple (e.g. ("00101010", "11101011", "00010110"))
        :param rgb2: Another string tuple
        (e.g. ("00101010", "11101011", "00010110"))
        :return: An integer tuple with the two RGB values merged.
        """
        r1, g1, b1 = rgb1
        r2, g2, b2 = rgb2
        rgb = (r1[:4] + r2[:4],
               g1[:4] + g2[:4],
               b1[:4] + b2[:4])
        return rgb

    @staticmethod
    def merge(img1, img2):
        """menggambungkan kedua citra.Citra kedua yang akan digabungkan ke citra pertama.

        :param img1: First image
        :param img2: Second image
        :return: new merged image.
        """

        # mengecek dimensi atau ukuran foto
        if img2.size[0] > img1.size[0] or img2.size[1] > img1.size[1]:
            raise ValueError('Citra 2 tidak boleh lebih besar dari citra 1!')

        # Mendapat map pixel kedua foto
        pixel_map1 = img1.load()
        pixel_map2 = img2.load()

        # membuat foto baru sebagai foto stego
        new_image = Image.new(img1.mode, img1.size)
        pixels_new = new_image.load()

        for i in range(img1.size[0]):
            for j in range(img1.size[1]):
                rgb1 = Steganography.__int_to_bin(pixel_map1[i, j])

                # menggunankan value 0 ataupixel hitam untuk nilai default
                rgb2 = Steganography.__int_to_bin((0, 0, 0))

                # Mengecek posisi agar tepat sasaran untuk foto kedua
                if i < img2.size[0] and j < img2.size[1]:
                    rgb2 = Steganography.__int_to_bin(pixel_map2[i, j])

                # menggabungkan kedua pixel dan dikonversike integer tuple
                rgb = Steganography.__merge_rgb(rgb1, rgb2)

                pixels_new[i, j] = Steganography.__bin_to_int(rgb)

        return new_image

    @staticmethod
    def unmerge(img):
        """memisahkan foto.

        :param img: The input image.
        :return: The unmerged/extracted image.
        """

        # Mendapat pixel map
        pixel_map = img.load()

        # membuat foto baru dan mendapatkan pixel mapnya
        new_image = Image.new(img.mode, img.size)
        pixels_new = new_image.load()

        # Tuple yang digunakan untuk menyimpan ukuran normal foto tersebut
        original_size = img.size

        for i in range(img.size[0]):
            for j in range(img.size[1]):
                # Mendapat nilai  RGB (sebagai string tuple) dari nilai pixel sekarang
                r, g, b = Steganography.__int_to_bin(pixel_map[i, j])

                # ekstraksi  4 bit terakhir (representasi dari foto utama)
                # menggabungkan 4 zero bit kosong di LSB karena total bit ada 24
                rgb = (r[4:] + '0000',
                       g[4:] + '0000',
                       b[4:] + '0000')

                # konversi ke integer tuple
                pixels_new[i, j] = Steganography.__bin_to_int(rgb)

                # Bila posisi benar, simpan posisi tersebut sebagai posisi valid
                if pixels_new[i, j] != (0, 0, 0):
                    original_size = (i + 1, j + 1)

        # potong foto berdasarkan posisi valid
        new_image = new_image.crop((0, 0, original_size[0], original_size[1]))

        return new_image


@click.group()
def cli():
    pass


@cli.command()
@click.option('--img1', required=True, type=str, help='Image that will hide another image')
@click.option('--img2', required=True, type=str, help='Image that will be hidden')
@click.option('--output', required=True, type=str, help='Output image')
def merge(img1, img2, output):
    merged_image = Steganography.merge(Image.open(img1), Image.open(img2))
    merged_image.save(output)


@cli.command()
@click.option('--img', required=True, type=str, help='Image that will be hidden')
@click.option('--output', required=True, type=str, help='Output image')
def unmerge(img, output):
    unmerged_image = Steganography.unmerge(Image.open(img))
    unmerged_image.save(output)


if __name__ == '__main__':
    cli()
