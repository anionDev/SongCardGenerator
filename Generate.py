import argparse
import os
import re
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
        [111, 50, 168], #purple
        [250, 49, 35], #red
        [250, 98, 22], #orange
        [252, 205, 76], #yellow
        [81, 155, 252], #bright blue
        [245, 156, 54], #bright orange
        [182, 110, 250], #bright purple
    ]
    __max_len_per_line:int=29
    __max_length_of_text:int=54

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
    def __smart_split(self,text: str, max_len_per_line: int) -> list[str]:
        text = text.strip()
        if len(text) <= max_len_per_line:
            return [text]
        match = re.search(r'[\s\-_,;:.]', text[:max_len_per_line][::-1])
        if match:
            split_index = max_len_per_line - match.start()
            first = text[:split_index].rstrip()
            second = text[split_index:].lstrip()
        else:
            first = text[:max_len_per_line - 1] + "-"
            second = text[max_len_per_line - 1:]
        if len(second) > max_len_per_line:
            match2 = re.search(r'[\s\-_,;:.]', second[:max_len_per_line][::-1])
            if match2:
                split_index2 = max_len_per_line - match2.start()
                first = first.rstrip() + "-"
                second = second[:split_index2].rstrip() + " " + second[split_index2:].lstrip()
            else:
                second = second[:max_len_per_line - 1] + "-\n" + second[max_len_per_line - 1:]
        return [first, second]
    
    @GeneralUtilities.check_arguments
    def __generate_properties_file(self,target_file:str,title:str,interpret:str,year:int,number:int,hash:str)->None:
        GeneralUtilities.assert_file_does_not_exist(target_file)
        GeneralUtilities.assert_condition(len(self.background_colors)==8,"Can not calculate color due to changed color-set")
        color_index=int(hash[2], 16)* 8 // 16
        color:list[int]= self.background_colors[color_index]
        size=400
        text_top=interpret
        text_middle=str(year)
        text_bottom=title
        text_bottom_left=str(number)
        img = Image.new("RGB", (size, size), (color[0],color[1],color[2]))
        draw:ImageDraw.ImageDraw = ImageDraw.Draw(img)

        font_artist:ImageFont.ImageFont = ImageFont.truetype(self.fontbold,26)
        font_year :ImageFont.ImageFont= ImageFont.truetype(self.fontbold,150)
        font_title :ImageFont.ImageFont= ImageFont.truetype(self.fontitalic,26)
        font_number :ImageFont.ImageFont= ImageFont.truetype(self.fontregular,20)

        font_color=(0,0,0)
        self.__draw_text_lines(draw,size,font_color,0, 50,self.__smart_split( text_top,self.__max_len_per_line), font_artist,True,True)
        self.__draw_text(draw,size,font_color,0, size/2-font_year.size/2 , text_middle, font_year, True)
        self.__draw_text_lines(draw,size,font_color,0, size-70, self.__smart_split(text_bottom,self.__max_len_per_line), font_title, True,False)

        if self.number:
            self.__draw_text(draw,size,font_color,10, size -30,text_bottom_left, font_number, False)

        img.save(target_file)

    @GeneralUtilities.check_arguments
    def __draw_text_lines(self,draw:ImageDraw.ImageDraw,size,font_color,x, y, lines:list[str],font:ImageFont.FreeTypeFont, center:bool,direction_up_to_down:bool):
        GeneralUtilities.assert_condition(0<len(lines),"No text lines given.")
        GeneralUtilities.assert_condition(len(lines)<=2,"Too many lines. Maximal 2 lines are supported.")
        
        if len(lines)==1:
            self.__draw_text(draw,size,font_color,x, y, lines[0], font, center)
        else:
            if direction_up_to_down:
                y_line1=y
                y_line2=y+font.size*1.2
            else:
                y_line1=y-font.size*1.2
                y_line2=y
            self.__draw_text(draw,size,font_color,x, y_line1, lines[0], font, center)
            self.__draw_text(draw,size,font_color,x, y_line2, lines[1], font, center)

    @GeneralUtilities.check_arguments
    def __draw_text(self,draw:ImageDraw.ImageDraw,size,font_color,x, y, text:str,font:ImageFont.FreeTypeFont, center:bool):
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
    def __get_year_from_audio(self,audio:EasyID3,input_str:str)->int:
        year_str=self.__get_property_from_audio(audio,"date",input_str)
        match1 = re.match(r"(\d{4})-\d{2}-\d{2}", year_str)
        if match1:
            year = match1.group(1)
            return int(year)
        match2 = re.match(r"(\d{4})", year_str)
        if match2:
            year = match2.group(1)
            return int(year)
        raise Exception(f"Could not extract year from date-value \"{year_str}\" in file \"{input_str}\".")

    @GeneralUtilities.check_arguments
    def __truncate_length(self,input_str:str,maximal_length:int)->str:
        if len(input_str)<=maximal_length:
                return input_str
        else:
            return input_str[0:maximal_length]+"..."
        
    @GeneralUtilities.check_arguments
    def generate(self)->None:
        GeneralUtilities.assert_folder_exists(self.songsfolder)
        GeneralUtilities.ensure_folder_exists_and_is_empty(self.targetfolder)
        setfolders=GeneralUtilities.get_direct_folders_of_folder(self.songsfolder)
        for set_folder in setfolders:
            generated_years:dict[int,int]=dict[int,int]()
            setname:str=os.path.basename(set_folder)
            GeneralUtilities.write_message_to_stdout(f"Generate set \"{setname}\"...")
            song_files=GeneralUtilities.get_direct_files_of_folder(set_folder)
            GeneralUtilities.assert_condition(0<len(song_files),"No songs found")
            amount_of_digits=len(str(len(song_files)))

            songs_all:list[Song]=[]
            for song in song_files:
                GeneralUtilities.assert_condition(song.endswith(".mp3"),"Only mp3 songs are supported.")
                audio = EasyID3(song) 
                title =self.__truncate_length( self.__get_property_from_audio(audio,"title",song),self.__max_length_of_text)
                artists=self.__truncate_length( ", ".join(sorted(self.__get_properties_from_audio(audio,"artist",song))),self.__max_length_of_text)
                year= self.__get_year_from_audio(audio,song)
                songs_all.append(Song(year,artists,title))

            songs_set:list[Song]=[]
            for song in songs_all:#remove duplicated items
                if not song in songs_set:
                    songs_set.append(song)
            songs_set.sort(key=lambda obj: obj.get_key())

            number=0

            set_target_folder=os.path.join(self.targetfolder,setname)
            GeneralUtilities.ensure_directory_exists(set_target_folder) 
            tracklist_file:str=os.path.join(set_target_folder,"Tracklist.txt")
            GeneralUtilities.ensure_file_exists(tracklist_file)
            for song in songs_all:
                number=number+1
                GeneralUtilities.append_line_to_file(tracklist_file,f"{str(number)};\"{song.artists}\";\"{song.title}\";{song.year}")
                set_target_cards_folder=os.path.join(self.targetfolder,setname,"Cards")
                GeneralUtilities.ensure_directory_exists(set_target_cards_folder)
                hash:str=self.__hash(song.get_key())
                filename:str=f"{hash}.png"
                if self.number:
                    filename=f"{str(number).zfill(amount_of_digits)}_{filename}"
                self.__generate_properties_file(os.path.join(set_target_cards_folder,filename),song.title,song.artists,song.year,number,hash)
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
    #args = parser.parse_args()
    #scg=SongCardGenerator(args.songsfolder,args.targetfolder,args.fontregular,args.fontbold,args.fontitalic,args.verbose,args.number)
    scg=SongCardGenerator("songsfolder","targetfolder","arial.ttf","arialbd.ttf","ariali.ttf",False,False)
    scg.generate()

if __name__ == "__main__":
    run_cli()
