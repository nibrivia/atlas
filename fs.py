import pyfits
import log
import os
import fnmatch

def isFlat(imgType):
    return imgType == 4
def isDark(imgType):
    return imgType == 3
def isBias(imgType):
    return imgType == 2
def isLight(imgType):
    return imgType == 1
def isUnknown(imgType):
    return imgType == 0

def imgTypes():
    return {"Unknown":0, "Light":1, "Bias":2, "Dark":3, "Flat":4}

def getHeader(filename):
    hdu_list = pyfits.open(filename)
    return hdu_list[0].header

def getDarks(root, imgName):
    #hdu_list = pyfits.open(root + imgName)
    #hdr = hdu_list[0].header
    hdr = getHeader(root + imgName)
    #expTime = hdr["EXPTIME"]
    dateObs = hdr["DATE-OBS"].split("T")
    darkList = []

    log.v("Looking for darks from date:" + dateObs[0]) 
    darks = readFileToArray(root + ".darks")
    darkList = []
    for dark in darks:
        darkHdr = getHeader(root + dark)
        match = True
        #if darkHdr["EXPTIME"] != expTime:
            #match = False
        if dateObs[0] not in darkHdr["DATE-OBS"]:
            match = False
        if match:
            log.v("Found dark, matches with  " + dark)
            darkList.append(dark)

    return darkList

def getBiass(root, imgName):
    hdr = getHeader(root + imgName)
    dateObs = hdr["DATE-OBS"].split("T")
    biasList = []

    log.v("Looking for biass from date:" + dateObs[0])
    biass = readFileToArray(root + ".biass")
    biassList = []
    for bias in biass:
        biasHdr = getHeader(root + bias)
        match = True
        if dateObs[0] not in biasHdr["DATE-OBS"]:
            match = False
        if match:
            log.v("Found bias, matches with  " + bias)
            biasList.append(bias)
    return biasList

def getFlats(root, imgName):
    hdr = getHeader(root + imgName)
    dateObs = hdr["DATE-OBS"].split("T")
    flatList = []

    log.v("Looking for flats from date:" + dateObs[0])
    flats = readFileToArray(root + ".flats")
    flatsList = []
    for flat in flats:
        flatHdr = getHeader(root + flat)
        match = True
        if dateObs[0] not in flatHdr["DATE-OBS"]:
            match = False
        if match:
            log.v("Found flat, matches with  " + flat)
            flatsList.append(flat)
    return flatsList

def getUnprocessedImageNames(root):
    fileContents = readFileToArray(root + ".lights")
    filenames = []
    proc = readFileToArray(root + ".proc")
    
    for line in fileContents:
        (fn, date) = line.split(":")
        if fn not in proc:
            filenames.append(fn)
    filenames.sort()
    return filenames

def getUnprocessedFlatFn(root):
    fileContents = readFileToArray(root + ".flats")
    filenames = []
    proc = readFileToArray(root + ".proc")
    
    for fn in fileContents:
        if fn not in proc:
            filenames.append(fn)
    filenames.sort()
    return filenames

def indexFiles(root):
    log.d("Looking for all *.fit* in " + root)
    fitsFiles = [os.path.relpath(os.path.join(dirpath, f), root)
            for dirpath, dirnames, files in os.walk(root)
            for f in fnmatch.filter(files, "*.fit")]
    #print(fitsFiles)
 
    listDarks = readFileToArray(root + ".darks")
    listBiass = readFileToArray(root + ".biass")
    listFlats = readFileToArray(root + ".flats")
    listLights = readFileToArray(root + ".lights")
    listUnknowns = readFileToArray(root + ".unknowns")
    listErrors = readFileToArray(root + ".errors")
    index = readFileToArray(root + ".index")

    for f in fitsFiles:
        if f in index:
            log.v("Skipped " + f)
            continue
        if "atlas_" in f:
            continue
        log.d("Indexing "+f)
        hdr = getHeader(root + f)
        imgType = hdr["PICTTYPE"]
        outFile = "None"
        date = hdr["DATE-OBS"].split("T")[0]
        if isFlat(imgType):
            log.v(f + " is a flat.")
            listFlats.append(f)
        elif isDark(imgType):
            log.v(f + " is a dark")
            listDarks.append(f)
        elif isBias(imgType):
            log.v(f + " is a bias")
            listBiass.append(f)
        elif isLight(imgType):
            log.v(f + " is a light frame!")
            listLights.append(f + ":" + date)
        elif isUnknown(imgType):
            log.w(f + " is of unknown type?")
            listUnknowns.append(f)
        else:
            log.wtf("ImgType not unknown or anything else??")
            listErrors.append(f)
        #TODO only open file once in w+ mode
        index.append(f)
    writeListToFile(root+".flats", listFlats)
    writeListToFile(root+".darks", listDarks)
    writeListToFile(root+".biass", listBiass)
    writeListToFile(root+".lights", listLights)
    writeListToFile(root+".unknowns", listUnknowns)
    writeListToFile(root+".errors", listErrors)
    writeListToFile(root+".index", index)
    return

def writeListToFile(filename, array):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    f = open(filename, 'w+')
    for element in array:
        f.write(element + '\n')

def readFileToArray(filename):
    if not os.path.isfile(filename):
        return []
    f = open(filename, 'r')
    array = []
    for line in f:
        text = line.strip('\n')
        array.append(text)
    return array
