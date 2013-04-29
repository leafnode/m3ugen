#!/usr/bin/python -W ignore:.*
# -*- encoding: iso-8859-2 -*-

import eyeD3
import ogg.vorbis
import sys
import os
import os.path

properexts = ['ogg', 'mp3', 'mpc']

def usage():
    print "Usage: %s <dir1> <dir2> ... <dirn>" % sys.argv[0]
    sys.exit(1)

def mp3info(filename):
    try:
	af = eyeD3.Mp3AudioFile(filename)
	tag = af.getTag()
	if tag is None:
	    out = { 'artist' : os.path.basename(filename), 'title' : '', 'len' : af.getPlayTime() }
	else:
	    out = { 'artist': tag.getArtist(), 'title' : tag.getTitle(), 'len' : af.getPlayTime() }
    except eyeD3.tag.InvalidAudioFormatException:
	out = { 'artist' : os.path.basename(filename), 'title' : '', 'len' : 0 }
    except eyeD3.tag.TagException, e:
	sys.stderr.write("Tag error: "+filename+"\n")
	sys.stderr.write(str(e)+"\n")
	sys.exit(1)
	
    return out

def ogginfo(filename):
    vf = ogg.vorbis.VorbisFile(filename)
    vc = vf.comment()
    vi = vf.info()
    out = {'artist' : vc['ARTIST'][0], 'title' : vc['TITLE'][0], 'len' : int(vf.time_total(-1))}
    return out

def info(filename):
    ext = filename[-3:]
    if ext == "mp3":
	return mp3info(filename)
    if ext == "ogg":
	return ogginfo(filename)
    return None

def main():
    if len(sys.argv) < 2:
	usage()

    dirs = sys.argv[1:]
    data = []
    fulldata = []
    basedirs = []

    # sprawdzenie czy katalog istnieje
    
    for dir in dirs:
	if not os.path.isdir(dir):
	    print "%s does not exist or is not a directory" % (dir, )
	    sys.exit(2)
	if not os.path.isabs(dir):
	    dir = os.path.abspath(dir)
	dir = os.path.expanduser(dir)
	basedirs.append(dir)

    # przechodzenie po katalogach i zbieranie nazw plików
    for basedir in basedirs:
	for root, dirs, files in os.walk(basedir):
	    for name in files:
		ext = name[-3:]
		if ext in properexts:
		    fullname = os.path.join(root, name)
		    data.append(fullname)
    
    # sortowanie
    data.sort()

    # zbieranie danych
    for name in data:
	fulldata.append([name, info(name)])

    # zapis/wyświetlenie

    out = sys.stdout

    out.write("#EXTM3U\n")
    
    for name, fileinfo in fulldata:
	if fileinfo:
	    try:
		out.write("#EXTINF:%(len)d,%(artist)s - %(title)s\n" % fileinfo)
	    except UnicodeEncodeError:
		sys.stderr.write("File '%s' has incorrect characters in tag. Fix it.\n" % name)
		sys.exit(3)
	out.write("%s\n" % (name, ) )


if __name__ == "__main__":
    main()
