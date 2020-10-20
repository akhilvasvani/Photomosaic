#!/usr/bin/env python

import sys 
import os 
import subprocess 
import json 
import re 
import functools 
import validation_util 
from BaseImage import BaseImage 
from PIL import Image 

class SourceImageProcessor:

    def __init__(self, img_dir, size=(50,50)):
        self.img_dir = img_dir 
        self.size = size 

    def read_source_avg_colors(self): 
        loc1 = self.img_dir + ".txt" 
        loc2 = f"img_sets/img_jsons/" + self.img_dir + ".txt" 
        if os.path.isfile(loc1) or os.path.isfile(loc2): 
            return self.read_JSON_contents()
        print(f"JSON file provided does not exist. Running program to save avg_color results to JSON file as '{self.img_dir}.json' and re-trying to read JSON contents.") 
        if not os.path.exists(f"img_sets/{self.img_dir}"):
            p = subprocess.Popen(f"mkdir img_sets/{self.img_dir}", shell = True) 
        if not os.path.exists(f"img_sets/{self.img_dir}/thumbnails"):
            p = subprocess.Popen(f"mkdir img_sets/{self.img_dir}/thumbnails/", shell = True) 
        self.save_avg_colors_to_JSON() 
        return self.read_JSON_contents()

    def read_JSON_contents(self):
        try: 
            with open("img_sets/img_jsons/" + self.img_dir + ".txt", 'r') as json_file:
                return json.load(json_file) 
        except FileNotFoundError:
            try:
                with open(self.img_dir + ".txt", 'r') as json_file:
                    return json.load(json_file) 
            except FileNotFoundError:
                print("JSON file is not found. Exiting...") 
                sys.exit(1) 

    def save_avg_colors_to_JSON(self):
        source_img_dict = [self.collect_avg_colors_for_source_imgs()]
        with open(f"img_sets/img_jsons/{self.img_dir}" + ".txt", "w") as out:
            json.dump(source_img_dict, out) 

    def collect_avg_colors_for_source_imgs(self):
        trimmed_thumbnails = self.standardize_source_images()
        source_img_dict = {} 
        for img_class, img in trimmed_thumbnails.items():
            if img_class.name not in source_img_dict: 
                try: 
                    source_img_dict[img_class.name] = img_class.get_avg_color(img) ## .getcolors() might not return a 4-color tuple 
                except TypeError:
                    pass 
        return source_img_dict

    def standardize_source_images(self): 
        output = {}
        for img_class in self.get_images_from_img_dir(): 
            replacements = [(self.img_dir, ""), ("/", "")] 
            new_name = img_class.name
            for old, new in replacements:
                new_name = re.sub(old, new, new_name) 
            thumbnail_name = f"img_sets/{self.img_dir}/thumbnails/" + new_name + "_thumbnail.jpg"
            width, height = img_class.img.size 
            trimmed_img = img_class.img 
            if width > height:
                trimmed_img = trim_width(img_class.img, width, height)  
            elif width < height: 
                trimmed_img = trim_height(img_class.img, width, height)  
            thumbnail = trimmed_img.thumbnail(self.size)  
            if not os.path.exists(f"{thumbnail_name}.png"):
                trimmed_img.save(thumbnail_name, "png")   ## the trimmed thumbnail will be used for our img
            output[BaseImage(thumbnail_name)] = trimmed_img 
        return output 

    def get_images_from_img_dir(self):
        for fn in os.listdir(self.img_dir):
            if fn.endswith(".jpg") or fn.endswith(".png"): 
                yield BaseImage(self.img_dir + "/" + fn) 

def trim_width(img, width, height):
    if width <= height: return img
    diff = width - height 
    left = top = 0 
    right = width - diff 
    return img.crop((left, top, right, height))  

def trim_height(img, width, height):
    if height <= width: return img
    diff = height - width 
    left = top = 0 
    bottom = height - diff 
    return img.crop((left, top, width, bottom)) 

if __name__ == "__main__":
    print(read_source_avg_colors())
