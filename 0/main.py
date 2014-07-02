import args
import os
import fs
import log

tmp = args.tempDir
pwd = args.pwd
log.i("Indexing " + pwd)
fs.indexFiles(pwd)

log.i("Getting unprocessed images")
unprocImgNames = fs.getUnprocessedImageNames(pwd)
if not unprocImgNames or len(unprocImgNames) == 0:
    log.i("No unprocessed images.")
    #TODO stop the program?

log.i("Processing " + str(len(unprocImgNames)) + " images")
for img in unprocImgNames:
    log.i("Getting calbration images for " + img)
    darks = []
    biass = []
    flats = []
    log.d("Getting darks")
    darks = fs.getDarks(pwd, img)
    log.d("Getting biass")
    biass = fs.getBiass(pwd, img)
    log.d("Getting flats")
    flats = fs.getFlats(pwd, img)

    #TODO deal with not good darks
    #TODO deal with lack of flats
    #TODO deal with weird timing for calibration (before vs. after)

    log.d("IRAF files")
    imgBaseName = os.path.splitext(os.path.basename(img))[0]
    log.d("Saving lists to: " + pwd + tmp)
    fs.writeListToFile(pwd + tmp + ".darks-" + imgBaseName, darks)
    fs.writeListToFile(pwd + tmp + ".biass-" + imgBaseName, biass)
    fs.writeListToFile(pwd +tmp + ".flats-" + imgBaseName, flats)
