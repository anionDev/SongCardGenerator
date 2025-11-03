import argparse
import os
import random
import hashlib
from PIL import Image, ImageDraw, ImageFont
from mutagen.easyid3 import EasyID3 
from ScriptCollection.GeneralUtilities import GeneralUtilities

class Song:
    year:int
    artists:str
    title:str

    def __init__(self,year:str,artists:str,title:str):
        self.year=year
        self.artists=artists
        self.title=title
        
    def __eq__(self, other):
        if isinstance(other, Song):
            return self.get_key() == other.get_key()
        else:
            return False
    
    def get_key(self)->str:
        return f"{self.year}_{self.artists}_{self.title}"
    
class SongCardGenerator:

    songsfolder:str
    targetfolder:str
    prefixforlinks:str
    fontregular:str
    fontbold:str
    fontitalic:str
    verbose:bool
    number:bool
    background_colors:list[list[int]]=[#rgb-values
        [70, 52, 235], #blue
        [250, 98, 22], #orange
        [250, 49, 35], #red
        [111, 50, 168], #purple
    ]

    def __init__(self,songsfolder:str,targetfolder:str,fontregular:str,fontbold:str,fontitalic:str,verbose:bool,number:bool):
         self.songsfolder=GeneralUtilities.resolve_relative_path_from_current_working_directory( songsfolder)
         self.targetfolder=GeneralUtilities.resolve_relative_path_from_current_working_directory( targetfolder)
         self.fontregular=GeneralUtilities.resolve_relative_path_from_current_working_directory(fontregular)
         self.fontbold=GeneralUtilities.resolve_relative_path_from_current_working_directory(fontbold)
         self.fontitalic=GeneralUtilities.resolve_relative_path_from_current_working_directory(fontitalic)
         self.verbose=verbose
         self.number=number

    @GeneralUtilities.check_arguments
    def __get_properties_from_audio(self,audio:EasyID3,property,file:str)->list[str]:
        results=audio.get(property, [])
        GeneralUtilities.assert_condition(0<len(results),f"Expected property-values \"{property}\" in file \"{file}\".")
        return results

    @GeneralUtilities.check_arguments
    def __get_property_from_audio(self,audio:EasyID3,property,file:str)->str:
        results=self.__get_properties_from_audio(audio,property,file)
        GeneralUtilities.assert_condition(1==len(results),f"Exactly 1 result expected for property-value \"{property}\" in file \"{file}\".")
        return results[0]

    @GeneralUtilities.check_arguments
    def __generate_properties_file(self,target_file:str,title:str,interpret:str,year:int,number:int)->None:
        GeneralUtilities.assert_file_does_not_exist(target_file)
        color:list[int]=random.choice(self.background_colors)
        size=400
        text_top=interpret
        text_middle=str(year)
        text_bottom=title
        text_bottom_left=str(number)
        img = Image.new("RGB", (size, size), (color[0],color[1],color[2]))
        draw:ImageDraw.ImageDraw = ImageDraw.Draw(img)

        font_artist:ImageFont.ImageFont = ImageFont.truetype(self.fontbold,30)
        font_year :ImageFont.ImageFont= ImageFont.truetype(self.fontbold,150)
        font_title :ImageFont.ImageFont= ImageFont.truetype(self.fontitalic,30)
        font_number :ImageFont.ImageFont= ImageFont.truetype(self.fontregular,20)

        font_color=(0,0,0)

        self.__draw_text(draw,size,font_color,0, 50, text_top, font_artist,True)
        self.__draw_text(draw,size,font_color,0, size/2-font_year.size/2 , text_middle, font_year, True)
        self.__draw_text(draw,size,font_color,0, size-70, text_bottom, font_title, True)

        if self.number:
            self.__draw_text(draw,size,font_color,10, size -30,text_bottom_left, font_number, False)

        img.save(target_file)

    @GeneralUtilities.check_arguments
    def __draw_text(self,draw:ImageDraw.ImageDraw,size,font_color,x, y, text,font, center:bool):
        """Zeichnet Text an Position (x, y), optional zentriert horizontal."""
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0] 
        h = bbox[3] - bbox[1]

        if center:
            x = (size - w) / 2
        draw.text((x, y), text, font=font, fill=font_color)

    @GeneralUtilities.check_arguments
    def __print_bar_chart(self,data:dict[int,int], max_width=30):
        min_key = min(data.keys())
        max_key = max(data.keys())
        for year in range(min_key, max_key + 1):
            if not year in data:
                data[year]=0
        max_value = max(data.values())
        for label, value in sorted(data.items()):
            bar_length = int(value / max_value * max_width)
            bar = "█" * bar_length
            print(f"{label:10} | {bar} ({value})")

    @GeneralUtilities.check_arguments
    def __hash(self,input_str:str)->str:
        hash_object = hashlib.sha256(input_str.encode("utf-8"))
        hash_hex = hash_object.hexdigest()
        result= hash_hex[0:12]
        return result

    @GeneralUtilities.check_arguments
    def generate(self)->None:
        GeneralUtilities.assert_folder_exists(self.songsfolder)
        GeneralUtilities.ensure_folder_exists_and_is_empty(self.targetfolder)
        generated_years:dict[int,int]=dict[int,int]()
        
        for set_folder in GeneralUtilities.get_direct_folders_of_folder(self.songsfolder):
            setname:str=os.path.basename(set_folder)
            GeneralUtilities.write_message_to_stdout(f"Generate set \"{setname}\"...")
            song_files=GeneralUtilities.get_direct_files_of_folder(set_folder)
            GeneralUtilities.assert_condition(0<len(song_files),"No songs found")
            amount_of_digits=len(str(len(song_files)))

            songs_all:list[Song]=[]
            for song in song_files:
                GeneralUtilities.assert_condition(song.endswith(".mp3"),"Only mp3 songs are supported.")
                audio = EasyID3(song) 
                title = self.__get_property_from_audio(audio,"title",song)
                artists=", ".join(sorted(self.__get_properties_from_audio(audio,"artist",song)))
                year_str = self.__get_property_from_audio(audio,"date",song)
                year=int(year_str)
                songs_all.append(Song(year,artists,title))

            songs_set:list[Song]=[]
            for song in songs_all:#remove duplicated items
                if not song in songs_set:
                    songs_set.append(song)
            songs_set.sort(key=lambda obj: obj.get_key())

            number=0
            for song in songs_all:
                number=number+1
                set_target_folder=os.path.join(self.targetfolder,setname)
                GeneralUtilities.ensure_directory_exists(set_target_folder)
                hash:str=self.__hash(song.get_key())
                filename:str=f"{hash}.png"
                if self.number:
                    filename=f"{str(number).zfill(amount_of_digits)}_{filename}"
                self.__generate_properties_file(os.path.join(set_target_folder,filename),song.title,song.artists,song.year,number)
                if not song.year in generated_years:
                    generated_years[song.year]=0
                generated_years[song.year]=generated_years[song.year]+1
            GeneralUtilities.write_message_to_stdout(f"Dispersion:")
            self.__print_bar_chart(generated_years)


def run_cli():
    parser = argparse.ArgumentParser(description="Song-Card-Generator")

    # Add arguments
    parser.add_argument("-s","--songsfolder",required=True,help="Source-folder for the songs. Remark: The content will be taken from each subfolder of this folder.")
    parser.add_argument("-t","--targetfolder" ,required=True, help="Target-folder. Remark: The entire content of this folder will be removed.")
    parser.add_argument("-r","--fontregular",required=True)
    parser.add_argument("-b","--fontbold",required=True)
    parser.add_argument("-i","--fontitalic",required=True)
    parser.add_argument("-v", "--verbose", action="store_true",default=False,required=False)
    parser.add_argument("-n", "--number", action="store_true",default=False,required=False)

    # Parse arguments
    scg:SongCardGenerator=None
    args = parser.parse_args()
    scg=SongCardGenerator(args.songsfolder,args.targetfolder,args.fontregular,args.fontbold,args.fontitalic,args.verbose,args.number)
    #scg=HitsterGenerator("songsfolder","targetfolder","arial.ttf","arialbd.ttf","ariali.ttf",False,False)
    scg.generate()

if __name__ == "__main__":
    run_cli()
