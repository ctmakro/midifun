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

from downloader import maybe_download_and_extract
for i in names:
    zip_url = zip_template.format(i)
    try:
        maybe_download_and_extract(zip_url,"./midies/")
    except:
        print("(err)",zip_url)
