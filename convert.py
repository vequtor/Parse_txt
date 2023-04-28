# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 12:00:02 2023

@author: 22856
"""


import os, sys
import pandas as pd
import numpy as np
import argparse
from typing import NamedTuple

class Channels(NamedTuple):
    start_channels: int
    start_time: int
    num_of_channels: int
    space: int
    period: int
    

# function for checking and
# skipping lines
def collect_data_channel(index):
    start = 69 # ?????????????????
    channel_row = 0  # ?????????????????
    
    if(index<start):
        return True
    
    if(index%10==channel_row):
        return False

    return True

# function for checking and
# skipping lines
def collect_data_time(index):
    start = 69 # ?????????????????
    time_row = 9  # ?????????????????
    
    if(index<start):
        return True
    
    if(index%10==time_row):
        return False
    
    return True

def find_data_wavelength(path: str) -> np.array:
    
    delta_sub = "Wavelength Delta (nm): "
    start_sub = "Wavelength Start (nm): "
    num_of_points_sub = "Number of Points: "
    
    
    info_about_channels_value = None
    delta_value = None
    start_value = None
    stop_value = None
    num_of_points_value = None
    
    counter_new_line = 0
    
    i = 0
    
    with open(path, mode='r') as fr:
        while(1):
            if(i>100):
                print("Не найдено данных для построения диапазона длин волн.")
                return
                
            if(delta_value and start_value and num_of_points_value and
               info_about_channels):
                stop_value = start_value + delta_value*num_of_points_value
                print(f"\tДлина волны от {start_value} до {stop_value} " \
                      f"{num_of_points_value} значений\n")
                return np.arange(start_value, stop_value, delta_value)
            
            i += 1
                
            line = fr.readline()
            
            if(line=="\n"):
                counter_new_line += 1
            
            # find first spectr
            else:
                if(num_of_points_value and counter_new_line>=1):
                    print("sfasa")           
                else:   
                    counter_new_line = 0
                
            index_start = line.find(start_sub)
            index_delta = line.find(delta_sub)
            index_num_of_points = line.find(num_of_points_sub)
                        
            
            if(index_delta != -1):
                index_of_point = None
                delta_str = line[index_delta+len(start_sub):-1]
                delta_value = 0
                
                for index, sim in enumerate(delta_str):
                    if(ord(sim)>=48 and ord(sim)<=57):
                        if(index_of_point):
                            delta_value += (ord(sim)-48)*(0.1**(index-index_of_point))
                        else:
                            delta_value = delta_value*10 + ord(sim)-48
                
                    if(ord(sim)==46):
                        index_of_point = index
            
            if(index_start != -1):
                index_of_point = None
                start_str = line[index_start+len(start_sub):-1]
                start_value = 0
                
                for index, sim in enumerate(start_str):
                    if(ord(sim)>=48 and ord(sim)<=57):
                        if(index_of_point):
                            start_value += (ord(sim)-48)*(0.1**(index-index_of_point))
                        else:
                            start_value = start_value*10 + ord(sim)-48
                
                    if(ord(sim)==46):
                        index_of_point = index
                        
            if(index_num_of_points != -1):
                num_of_points_str = line[index_num_of_points+len(num_of_points_sub):-1]
                num_of_points_value = 0
                
                for sim in num_of_points_str:
                    if(ord(sim)>=48 and ord(sim)<=57):
                        num_of_points_value = num_of_points_value*10 + ord(sim)-48
                        


def read_file_and_write(path_r: str, path_w: str, fn: str, wavelength_arr: int) -> None:
    num_of_cols = wavelength_arr.shape[0]
    counter = 0
    
    index_start = fn.find(".") + 1
    index_stop = fn.rfind(".")
    if(index_start==-1):
        index_start = 0
    if(index_stop==-1):
        index_stop = len(fn) - 1
        
    try:
        df_t = pd.read_csv(os.path.join(path_r, fn), encoding = 'cp1251', sep = '\t',
                          skiprows=lambda x: collect_data_time(x), names=("time",),
                          usecols=(0, ), header=None)
        
        df_ch = pd.read_csv(os.path.join(path_r, fn), encoding = 'cp1251', sep = '\t',
                          skiprows=lambda x: collect_data_channel(x), names=range(0, num_of_cols),
                          header=None)
        
        df1_tr = df_ch.transpose()
        
        if(df_ch.shape[0]!=df_t.shape[0]):
            raise Exception
        
        for i in df1_tr.columns:
            try:
                arr1 = df1_tr[i]
                arr2 = wavelength_arr
                if(arr1.shape!=arr2.shape):
                    raise Exception
                
                df2 = pd.DataFrame({'Wavelength': arr2, 'Channel 1': arr1})
                
                new_fn = fn[index_start: index_stop] + "__" + \
                    str(df_t["time"][i]) + ".csv"
                
                df2.to_csv(os.path.join(path_w, new_fn), sep=";",
                           encoding="cp1251", index=False)

                print(f"\t\tФайл {i}: {new_fn} записан.")
                counter += 1
                
            except Exception:
                pass
            
    except Exception as e:
        print(e)
    
    finally:
        return counter
        

def validate(path: str) -> bool:
    if(not os.access(path=path, mode=os.R_OK)):
        return False
    
    return True


sys.argv.append(r"D:\испытания\проверка ФП датчиков\Термоиспытания датчик 1000")
sys.argv.append(r"D:\испытания\проверка ФП датчиков\Термоиспытания датчик 1000\обработка")

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Описание программы')
    parser.add_argument('path1', help='Путь к папке с txt файлами')
    parser.add_argument('path2', help='Путь к папке, в которую запишутся '\
                        'csv файлы.')
    parser.add_argument('-f', '--flag', dest='flag', help='Список с номерам'\
                        'и используемымых каналаов.\n Записать через запятую,'\
                        ' Нумерация начинается с 0.')
        
    args = parser.parse_args()
    
    input_path = args.path1
    output_path = args.path2
    
    if(not os.access(args.path1, mode=os.R_OK)):
        print(f"К файлу {input_path} нет доступа.")
        sys.exit(-2)
    if(not os.access(sys.path2, mode=os.W_OK)):
        print(f"К файлу {output_path} нет доступа.")
        sys.exit(-3)
        
    if(args.flag):
        try:
            channels = np.array((eval(args.flag)), dtype=int)
            channels = np.unique(channels)
            
            if(len(channels)==0):
                raise Exception
                
        except Exception:
            print("Список каналов передан неправильно.")
            sys.exit(-1)
        
    else:
        channels = (0, )
        
    print("\nПрограмма начала работу\n")
    print("\tВыбранные каналы: ", *channels, sep=" ")
    
    for f in os.listdir(input_path):
        if f.endswith('.txt'):
            ful_dir = os.path.join(input_path, f)
            if(validate(ful_dir)):
                print(f"\nФайл {f}")
                wavelength = find_data_wavelength(ful_dir)
                if(wavelength is not None):
                    print(f"\nФайл {f} подходит\n\tОбработка...")
                    output = read_file_and_write(input_path, output_path, f,
                                                 wavelength)
                    if(output):
                        print(f"\n\tФайл {f} прочитан, {output} файлов записано в " \
                              f"папку {output_path}\n")
                    else:
                        print(f"\tФайл {f} прочитан, но значения не записаны\n")
                else:
                    print(f"\tФайл {f} не прочитан\n")
            else:
                print(f"Файл {f} не подходит.\n")

print("\nПрограмма закончила работу\n")
sys.exit(0)