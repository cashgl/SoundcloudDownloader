#!/usr/bin/env python
# Adapted from Ian Palmgren's DownCloud: http://www.ianpalmgren.com/home/#/downcloud/

import soundcloud
import urllib2
import eyed3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC

def custom_song_info():
    print 'Enter your own information\n'
    artist = raw_input('Artist: ')
    title = raw_input('Title: ')
    filename = title + ' - ' + artist + '.mp3'

    return {'filename':filename, 'artist':artist, 'title': title}

if __name__ == '__main__':
    client = soundcloud.Client(client_id='<ENTER_CLIENT_ID>')
    line = '------------------------------------------------------------'

    print '\nWelcome the Soundcloud Song Downloader.'

    song_url = raw_input('Song Url (must include \'https://soundcloud.com\'): ')
        
    try:
        response = urllib2.urlopen(song_url)
    except urllib2.URLError, e:
        if hasattr(e, 'reason'):
            print 'Bad URL, try again!'
        elif hasattr(e, 'code'):
            print 'The server could not fulfill the request.'
            print 'Error Code: ', e.code
        else:
            print 'got', response.geturl()
    else:
        try:
            track = client.get('/resolve', url=song_url)
        except:
            print '\nSong not found.'
            exit(1)
        str = "/tracks/" + str(track.id)
        # fetch track to stream
        try:
            stream_url = client.get(track.stream_url, allow_redirects=False)
        except:
            print "\nArtist has not allowed downloading for this track."
            exit(1)

           
        track = client.get(str)
        artist = track.user['username']
        title = track.title
        filename = title + '.mp3'
        thumbnail = track.artwork_url
        
        if ' - ' in track.title:
            newTitle = track.title.split('-')
            artist = newTitle[0].rstrip()
            title = newTitle[1][1:]
            
        mp3file = urllib2.urlopen(stream_url.location)

        print '\nIs this the correct information?'
        print line
        print 'Filename: ' + filename
        print 'Artist: ' + artist
        print 'Title: ' + title
        print line

        # maps 'y' to True and 'n' to False
        var = {'y':True, 'n':False}[raw_input('Enter Yes or No: ').strip()[0].lower()]
        print '\n'

        info = None
        while not var:
            info = custom_song_info()

            filename = info['filename']

            print '\nIs this the correct information?'
            print line
            print 'Filename: ' + filename
            print 'Artist: ' + info['artist']
            print 'Title: ' + info['title']
            print line

            var = {'y':True, 'n':False}[raw_input('Enter Yes or No: ').strip()[0].lower()]        

        print '\n'

        output = open(filename,'wb')
        output.write(mp3file.read())
        output.close()

        try:
            f = eyed3.load(filename)
            if f.tag is None:
                f.tag = eyed3.id3.Tag()
                f.tag.file_info = eyed3.id3.FileInfo(track.title)
            f.tag.title = title
            f.tag.artist = artist
            f.tag.genre = track.genre

            f.tag.save(track.title, (2,3,0))

            audio = MP3(filename, ID3=ID3)

            user_agent = ''
            headers = { 'User-Agent' : user_agent }
            imgRequest = urllib2.Request(thumbnail, headers=headers)
            imgData = urllib2.urlopen(imgRequest).read()

            audio.tags.add(
                APIC(
                    encoding=3, # 3 is for utf-8
                    mime='image/jpg', # image/jpeg or image/png
                    type=3, # 3 is for the cover image
                    desc=u'Cover',
                    data=imgData
                )
            )
            audio.save()
        except:
            print "Could not download artwork image."
        
        print 'File downloaded succesfully.'