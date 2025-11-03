# SongsCardsGenerator

SongsCardsGenerator is a simple tool to generate cards for games like Hitster based on your own music-folder.

How does it work?

```sh
git clone https://github.com/anionDev/SongCardGenerator
python Generate.py -s ./songsfolder -t ./targetfolder -r ./arial.ttf -b ./arialbd.ttf -i ./ariali.ttf
```
For each subfolder in the songs-folder a cards-set in targetfolder is generated. So it is required to have the music-files in a subfolder of the songs-folder.
Caution: This scripts needs a clean target-folder. So any already existing file in the given targetfolder will be removed.
