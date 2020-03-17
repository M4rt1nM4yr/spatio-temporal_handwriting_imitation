import os
from xml.etree import ElementTree

from PIL import Image

from utils.generator_with_length import GeneratorWithLength


class BoundingBox:
    def __init__(self, posX, posY, sizeX, sizeY):
        self.posX = posX
        self.posY = posY
        self.sizeX = sizeX
        self.sizeY = sizeY

    def __str__(self):
        return 'BBox(' + str(self.posX) + ", " + str(self.posY) + ", " + str(self.sizeX) + ", " + str(self.sizeY) + ")"

    def cropArgs(self):
        return self.posX, self.posY, self.posX + self.sizeX, self.posY + self.sizeY


class IamOfflineDataset:

    def __init__(self, baseDir):
        self.baseDir = baseDir

        with open(os.path.join(baseDir, 'blacklist.csv')) as blacklistFile:
            blacklist = blacklistFile.readlines()
        blacklist = [x.strip() for x in blacklist]

        self.boundingBoxes = self.loadBoundingBoxes(os.path.join(baseDir, 'ascii', 'lines.txt'), blacklist)
        self.forms, self.numLines = self.loadForms(os.path.join(baseDir, 'xml'), blacklist)


    @staticmethod
    def loadBoundingBoxes(linesFilename, blacklist=list()):
        bBoxes = dict()

        with open(linesFilename, 'r') as linesFile:
            for line in linesFile:
                for blacklistitem in blacklist:
                    if line.startswith(blacklistitem):
                        continue
                if line.startswith('#'):
                    continue
                lineElems = line.strip().split()
                assert(len(lineElems) > 8)

                name = lineElems[0]
                posX = int(lineElems[4])
                posY = int(lineElems[5])
                sizeX = int(lineElems[6])
                sizeY = int(lineElems[7])

                bBoxes[name] = BoundingBox(posX, posY, sizeX, sizeY)

        return bBoxes

    @staticmethod
    def loadForms(formsDir, blacklist=set()):
        forms = dict()
        numLines = 0

        xmlFiles = [os.path.join(formsDir, f) for f in os.listdir(formsDir)
                    if os.path.isfile(os.path.join(formsDir, f)) and f.endswith('.xml')]

        for xmlFile in xmlFiles:
            tree = ElementTree.parse(xmlFile)
            root = tree.getroot()
            assert(root.tag == 'form')

            formId = root.attrib['id']
            if formId in blacklist:
                continue

            lines = dict()
            for line in root.findall('./handwritten-part/line'):
                lines[line.attrib['id']] = line.attrib['text']
                numLines += 1

            forms[formId] = lines

        return forms, numLines

    def loadFormImage(self, formId):
        return Image.open(os.path.join(self.baseDir, 'forms', formId + '.png'))

    def linesIterator(self, imageLoader=None):
        return GeneratorWithLength(self.linesGen(imageLoader), self.numLines)

    def linesGen(self, imageLoader=None):

        if not imageLoader:
            imageLoader = self.loadFormImage

        for formId, form in self.forms.items():

            formImg = imageLoader(formId)

            for lineId, lineText in form.items():
                boundingBox = self.boundingBoxes[lineId]

                lineImg = formImg.crop(boundingBox.cropArgs())

                yield(lineId, lineImg, lineText)

    def formsIterator(self):
        return GeneratorWithLength(self.formsGen(), len(self.forms))

    def formsGen(self):

        # yield('d04-096', self.loadFormImage('d04-096'))

        for formId in self.forms:

            formImg = self.loadFormImage(formId)
            yield formId, formImg
