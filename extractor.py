import re, os, logging, pprint, json
from datetime import datetime
from bs4 import BeautifulSoup
import urllib.request

class Song:
    def __init__(self, pack, title, bpm, composer, vocalist, genre, fb, fvb, sb, eb):
        self.pack = pack;
        self.title = title;
        self.bpm = bpm;
        self.composer = composer;
        self.vocalist = vocalist;
        self.genre = genre;
        self.fb = fb;
        self.fvb = fvb;
        self.sb = sb;
        self.eb = eb;

    def get_difficulties(self):
        difficulties = []
        diff_sets = {
                "4B":self.fb,
                "5B":self.fvb,
                "6B":self.sb,
                "8B":self.eb
                }
        diff_names = ["NM", "HD", "MX", "SC"]
        diff_list = {k:dict(zip(diff_names,v)) for (k,v) in diff_sets.items()}
        for beats, diffs in diff_list.items():
            for diff, stars in diffs.items():
                difficulties.append({
                    "diffName":f"{beats} {diff}",
                    "diffNumber":stars,
                    "players":1,
                    "double":False
                    })
        return difficulties

    def json_conv(self):
        artist_string = "";
        if self.vocalist != "":
            artist_string = f"{self.composer} ft {self.vocalist}"
        else:
            artist_string = self.composer

        return {
                "pack": self.pack,
                "songName":self.title,
                "songArtist":artist_string,
                "bpm":self.bpm,
                "hasDifficulties":True,
                "hasDiffNumbers":True,
                "difficulties": self.get_difficulties()
                }

def main():
    pp = pprint.PrettyPrinter(depth=6)
    content = ""
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0')]
    with opener.open('http://cyphergate.net/index.php?title=DJMAX_RESPECT:Tracklist#RESPECT_Tracks') as f:
        content = f.read().decode("utf-8")
    soup = BeautifulSoup(content, "html.parser")
    dict_table = {}
    songs = {}
    for tbnum, table in enumerate(soup.select(".mw-parser-output table")):
        if tbnum not in dict_table:
            dict_table[tbnum] = {}
        for num, ele in enumerate(table.find_all("tr")):
            for elex in ele.find_all("td"):
                if num not in dict_table[tbnum]:
                    if (table.th is not None) and (table.th.string.replace("\n", "").strip() == "DOK2 - ONLY ON" or table.th.string.replace("\n", "").strip() == "TAP SONIC"):
                        pass
                    elif table.th is not None:
                        dict_table[tbnum][num] = [table.th.string.replace("\n", "").strip(), elex.get_text().replace("\n", "").strip()]
                    else:
                        dict_table[tbnum][num] = [elex.get_text().replace("\n", "").strip()]
                else:
                    dict_table[tbnum][num].append(elex.get_text().replace("\n", "").strip())
    els = list(dict_table.values())
    print(len(els))
    del els[-1]
    del els[0:2]
    print(len(els))
    print(els)
    for table in els:
        for row in table.values():
            th = row.pop(0)
            print(row)
            fb = row[5:9]
            fvb = row[9:13]
            sb = row[13:17]
            eb = row[17:21]
            if th in songs:
                songs[th].append(Song(th, row[0], row[1], row[2], row[3], row[4], fb, fvb, sb, eb))
            else:
                songs[th] = [Song(th, row[0], row[1], row[2], row[3], row[4], fb, fvb, sb, eb)]
    for pack, song_list in songs.items():
        print(pack, len(song_list))
        songs_encodable = [x.json_conv() for x in song_list]
        f = open(f"djmaxrespectv-{pack.lower().replace(' ', '-')}.json", "w")
        f.write(json.dumps(songs_encodable, indent=4, sort_keys=True))
        f.close()

main()
