import fitz


class Oplossing():
    """
    All variables that you need to change are in the __init__ method.

    The PyMuPDF library is very powerful but also poorly documented and fairly low-level; which makes for a not so
    enjoyable coding experience.

    """

    def __init__(self):
        self.doc = fitz.open("theo.pdf")

        # we have these hardcoded instead of locating them manually because of performance, for later chapters it
        # takes +- 10 seconds to look up page numbers
        self.stellingen = ["1.1.1", "1.1.2", "1.2.1", "1.2.2", "1.2.3", "1.2.4", "1.2.5", "1.2.6", "1.3.1", "1.4.1",
                           "1.4.2", "2.1.1", "2.2.1",
                           "2.2.2", "2.3.1", "2.4.1", "2.4.2", "2.4.3", "2.5.1", "2.5.2", "2.5.3", "3.1.1", "3.2.1",
                           "3.2.2", "3.2.3", "3.2.4",
                           "3.2.5", "3.3.1", "3.4.1", "3.5.1", "3.5.2", "3.5.3", "3.6.1", "4.1.1", "4.1.2", "4.2.1",
                           "4.2.2", "4.3.1", "4.4.1",
                           "4.5.1", "4.6.1", "5.1.1", "5.2.1", "5.3.1", "6.1.1", "6.2.1", "7.1.1", "7.1.2"]

        # again, decreases performance if set too high, dont't go higher than 10 for optimum performance
        self.scale_factor = fitz.matrix = fitz.Matrix(10, 10)
        self.croptop = 69
        self.cropbottom = 30

    def pixmaps_to_png(self, naam, lst):
        """
        Helper function that writes *multiple* pixmaps to png.

        :param naam: name of the output file (has to end in .png)
        :param lst: list of pixmaps to stitch together
        """
        tar_h = sum(x.height for x in lst)
        tar_w = lst[0].width

        accum_height = 0

        tar_pix = fitz.Pixmap(lst[0].colorspace, (0, 0, tar_w, tar_h), lst[0].alpha)
        for i, c in enumerate(lst):
            h = c.height
            c.setOrigin(0, accum_height)
            tar_pix.copyPixmap(c, c.irect)
            accum_height += h

        tar_pix.writePNG(f'{naam}.png')

    def search_for_exercise(self, input, next):
        """

        :return: -Page number of the beginnning of the exercise
                 -fitz.Rect containing
        """
        doc = self.doc

        for p in doc.pages(start = 4):

            if input in p.getText():
                b_rect = p.searchFor(input)[0]  # first (normally only) occurrence
                # find end
                for p2 in doc.pages(start=p.number):
                    if next in p2.getText():
                        e_rect = p2.searchFor(next)[0]  # first (normally only) occurrence
                        return p.number, b_rect, p2.number, e_rect

                # if the for loop terminates without having found a partner, just return None as the end rect
                # todo this doesnt work if a member wants the last exercise of a chapter, wich also happens to be a
                #  multiple page question. Ideally it should return the page nr of one before the next chapter and a
                #  rect of the entire page
                return p.number, b_rect, p.number, "none"

    def convert_to_png(self, naam, bpnr, beginrect, eindnr, eindrect):

        if type(eindrect) == str:
            page = self.doc.loadPage(bpnr)
            displayrect = fitz.Rect(page.rect.tl.x, beginrect.tl.y, page.rect.br.x, page.rect.br.y - self.cropbottom)
            pix = page.getPixmap(clip=displayrect, matrix=self.scale_factor)
            self.pixmaps_to_png(naam, [pix])

        if bpnr == eindnr:
            page = self.doc.loadPage(bpnr)
            displayrect = fitz.Rect(page.rect.tl.x, beginrect.tl.y, page.rect.br.x, eindrect.tr.y)
            pix = page.getPixmap(clip=displayrect, matrix=self.scale_factor)
            self.pixmaps_to_png(naam, [pix])
        else:
            pixes = []
            page = self.doc.loadPage(bpnr)  # begin page
            displayrect = fitz.Rect(page.rect.tl.x, beginrect.tl.y, page.rect.br.x, page.rect.br.y - self.cropbottom)
            pixes.append(page.getPixmap(clip=displayrect, matrix=self.scale_factor))
            for i in range(bpnr + 1, eindnr):  # middle pages
                p = self.doc.loadPage(i)
                displayrect = fitz.Rect(page.rect.tl.x, page.rect.tl.y + self.croptop, page.rect.br.x,
                                        page.rect.br.y - self.cropbottom)
                pixes.append(p.getPixmap(clip=displayrect, matrix=self.scale_factor))
            epage = self.doc.loadPage(eindnr)  # end page
            displayrect = fitz.Rect(page.rect.tl.x, page.rect.tl.y + self.croptop, page.rect.br.x, eindrect.tr.y)
            pixes.append(epage.getPixmap(clip=displayrect, matrix=self.scale_factor))
            self.pixmaps_to_png(naam, pixes)

    # @commands.command("opl")
    def opl(self):
        for i, cum in enumerate(self.stellingen[:len(self.stellingen) - 1]):
            print("doing: " + cum)
            a, b, c, d = self.search_for_exercise(cum, self.stellingen[i + 1])
            print(a)
            print(b)
            print(c)
            print(d)
            self.convert_to_png("result/" + cum , a, b, c, d)




dick = Oplossing()
dick.opl()
