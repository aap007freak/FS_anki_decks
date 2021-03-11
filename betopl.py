import fitz
import discord
from discord.ext import commands
from discord.ext import tasks

class Oplossing(commands.Cog):
    """
    All variables that you need to change are in the __init__ method.

    The PyMuPDF library is very powerful but also poorly documented and fairly low-level; which makes for a not so
    enjoyable coding experience.

    """

    def __init__(self):
        self.doc = fitz.open("ankistuff/solution_manual.pdf")

        # we have these hardcoded instead of locating them manually because of performance, for later chapters it
        # takes +- 10 seconds to look up page numbers
        self.chapters = {1: (0, 14), 2: (14, 47), 3: (47, 83), 4: (83, 117), 5: (117, 163), 6: (163, 193), 7: (193, 217),
                8: (217, 261), 9: (261, 303), 10: (303, 338), 11: (338, 371), 12: (371, 413), 13: (413, 442),
                14: (442, 474), 15: (474, 502), 16: (502, 531), 17: (531, 554), 18: (554, 578), 19: (578, 607),
                20: (607, 639), 21: (639, 675), 22: (675, 704), 23: (704, 738), 24: (738, 771), 25: (771, 794),
                26: (794, 835), 27: (835, 858), 28: (858, 886), 29: (886, 908), 30: (908, 941), 31: (941, 958),
                32: (958, 987), 33: (987, 1018), 34: (1018, 1040), 35: (1040, 1065), 36: (1065, 1094), 37: (1094, 1122),
                38: (1122, 1146), 39: (1146, 1171), 40: (1171, 1199), 41: (1199, 1224), 42: (1224, 1249), 43: (1249, 1269)}

        #again, decreases performance if set too high, dont't go higher than 10 for optimum performance
        self.scale_factor = fitz.matrix=fitz.Matrix(2, 2)
        self.croptop = 50
        self.cropbottom = 65

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


    def search_for_exercise(self, input):
        """

        :return: -Page number of the beginnning of the exercise
                 -fitz.Rect containing
        """
        doc = self.doc
        oplG = False

        splits = input.split('.')
        for p in doc.pages(int(self.chapters[int(splits[0])][0]), int(self.chapters[int(splits[0])][1])):
            if "Solutions to Problems" in p.getText():
                oplG = True
            if oplG:
                oefnr = str(splits[1] + ". ")
                if oefnr in p.getText():
                    b_rect = p.searchFor(oefnr)[0]  # first (normally only) occurrence
                    # find end
                    for nr2, p2 in enumerate(doc.pages(start=p.number, stop=int(self.chapters[int(splits[0])][1]))):
                        if str(int(oefnr.rstrip(". ")) + 1) in p2.getText():
                            e_rect = p2.searchFor(str(int(oefnr.rstrip(". ")) + 1))[0]  # first (normally only) occurrence
                            print(b_rect)
                            print(e_rect)
                            return p.number, b_rect, p2.number, e_rect

                    # if the for loop terminates without having found a partner, just return None as the end rect
                    # todo this doesnt work if a member wants the last exercise of a chapter, wich also happens to be a
                    #  multiple page question. Ideally it should return the page nr of one before the next chapter and a
                    #  rect of the entire page
                    return p.number, b_rect, p.number, "none"

    def convert_to_png(self, bpnr, beginrect, eindnr, eindrect):
        naam = "SPOILER-finished"

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
                displayrect = fitz.Rect(page.rect.tl.x, beginrect.tl.y + self.croptop, page.rect.br.x, page.rect.br.y - self.cropbottom)
                pixes.append(p.getPixmap(clip=displayrect, matrix=self.scale_factor))
            epage = self.doc.loadPage(eindnr)  # end page
            displayrect = fitz.Rect(page.rect.tl.x, page.rect.tl.y + self.croptop, page.rect.br.x, eindrect.tr.y)
            pixes.append(epage.getPixmap(clip=displayrect, matrix=self.scale_factor))
            self.pixmaps_to_png(naam, pixes)

    @commands.command("opl")
    async def opl(self, ctx,  *, argv):
        try:
            a, b, c, d = self.search_for_exercise(argv)
            self.convert_to_png(a, b, c, d)
            await ctx.send(file=discord.File("ankistuff/SPOILER_finished.png"))
        except:
            await ctx.send("Er is iets foutgegaan chief, sorry!")

