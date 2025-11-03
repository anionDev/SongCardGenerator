# SongsCardsGenerator

SongsCardsGenerator is a simple tool to generate cards for games like Hitster based on your own music-folder.

How does it work?

```sh
git clone https://github.com/anionDev/SongCardGenerator
cd SongCardGenerator
python Generate.py -s /.../songsfolder -t ./targetfolder -r /.../arial.ttf -b /.../arialbd.ttf -i /.../ariali.ttf
```

Remarks:

- Caution: This scripts needs a clean target-folder. So any already existing file in the given targetfolder will be removed.
- For each subfolder in the songs-folder a cards-set in targetfolder is generated. So it is required to have the music-files in a subfolder of the songs-folder.
- Only mp3-files are supported.
- The content (year, artist and songname) will be extracted from the mp3-file-metadata.
- `-n` adds an increasing number to the picture and adds the same number as filename-prefix.
- You must provide font-files (for example ttf-files). There is no default- or fallback-value which could be used instead.
- The filenames of the png-files are random but will be the same for 2 files if the year, the artists and the songname is the same.
