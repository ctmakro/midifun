# batch download from http://www.piano-midi.de/

names = \
'''Albeniz
Bach
Balakirew
Beethoven
Borodin
Brahms
Burgmueller
Chopin
Clementi
Debussy
Godowsky
Granados
Grieg
Haydn
Liszt
Mendelssohn
Moszkowski
Mozart
Mussorgsky
Rachmaninov
Ravel
Schubert
Schumann
Sinding
Tchaikovsky'''.split("\n")
zip_template = "http://www.piano-midi.de/zip/{}.zip"
zip_urls = [zip_template.format(i) for i in names]

zip_urls += \
'''http://www.kuhmann.com/Disklavier/Classical-I%20(001-215)%20MID.zip
http://www.kuhmann.com/Disklavier/Classical-II%20(215)%20MID.zip
http://www.kuhmann.com/Disklavier/Classical-III%20(222)%20MID.zip
http://www.kuhmann.com/Disklavier/Classical-IV%20(136)%20MID.zip
http://www.kuhmann.com/Disklavier/Classical-V%20001-370%20(MIDI).zip
http://www.kuhmann.com/Disklavier/Classical%20VI%20(MIDI).zip
http://www.kuhmann.com/Disklavier/Classical-VII%20(MID).zip'''.split('\n')

from downloader import maybe_download_and_extract

for zip_url in zip_urls:
    try:
        maybe_download_and_extract(zip_url,"./midies/")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("(err)",zip_url)
