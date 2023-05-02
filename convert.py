# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 12:00:02 2023

@author: 22856
"""


import os, sys
import io
import csv
import numpy as np
import argparse



def get_header_and_data_position(path: str) -> (list, io.TextIOWrapper):
    with open(path, mode='r') as f:
        header = []
        for i in range(100):
            line = f.readline()
            if(not line):
                return None
            
            if(line.strip()):
                header.append(line.rstrip())
            else:
                j = 1
                while(1):
                    line = f.readline()
                    if(not line):
                        return None
                    
                    if(not line.strip()):
                        j += 1
                    else:
                        if(j>=2):
                            f.seek(f.tell()-len(line)-1)
                            return header, f.tell()
                        else:
                            header.append(line.rstrip())
                            break
                    
        return None


def find_data_wavelength(strings: list[str]) -> np.array:
    delta_sub = "Wavelength Delta (nm): "
    start_sub = "Wavelength Start (nm): "
    num_of_points_sub = "Number of Points: "
    
    start_value = None
    delta_value = None
    num_of_points_value = None
    
    for string in strings:
        index_delta = string.find(delta_sub)
        index_start = string.find(start_sub)
        index_num_of_points = string.find(num_of_points_sub)
        
        if(index_delta!=-1 and len(delta_sub)<len(string)):
            next_index = len(delta_sub)
            delta_value = string[next_index:]
            
        if(index_start!=-1 and len(start_sub)<len(string)):
            next_index = len(start_sub)
            start_value = string[next_index:]
    
        if(index_num_of_points!=-1 and len(num_of_points_sub)<len(string)):
            next_index = len(num_of_points_sub)
            num_of_points_value = string[next_index:]
            
    if(not start_value or not delta_value or not num_of_points_value):
        return None
    
    try:
        start_value = float(start_value.strip())
        delta_value = float(delta_value.strip())
        num_of_points_value = float(num_of_points_value.strip())
        
    except Exception:
        return None
    
    if(delta_value<=0 or num_of_points_value<=0 or start_value<=0):
        return None
        
    stop_value = start_value + delta_value*num_of_points_value
    
    return np.arange(start_value, stop_value, delta_value)


def read_file_and_write(path_r: str, path_w: str, fn: str, wavelength_arr: int,
                        start_position: int, use_channels: set[int]) -> int:
    
    def find_num_of_channels(fr) -> set[int]:
        old_position = fr.tell()
        line = 1
        channels = 0
        
        while(line):
            line = fr.readline().strip()
            channels += 1
        
        fr.seek(old_position)
        
        if(channels<3):
            return {}
            
        return set(range(channels - 2))
    
    def read_one_line(fr):
        line = fr.readline()
        
        # End of file
        if(not line):
            return EOFError
        
        # Empty string (\n)
        line = line.strip()
        if(not line):
            return None
        
        # Power on i-channel
        if(line.count('\t')>10):
            lst = line.split("\t")
            arr = np.array([float(x) for x in lst])
            return arr
        
        # Time
        else:
            return float(line)
        
    
    def write_in_file(y_arr: np.ndarray, file_name: str):
        with open(file_name, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            
            # имена столбцов
            writer.writerow(['Wavelength', 'Channel 1'])
            for a, b in zip(wavelength_arr, y_arr):
                writer.writerow([a, b])
                
            print(f"\t\tФайл {counter}: {file_name} записан.")
    
    counter = 0
    cur_time = 0
    
    try:
        length_of_spectr = wavelength_arr.shape[0]
        
        with open(os.path.join(path_r, fn)) as fr:
            fr.seek(start_position)
            
            channels = find_num_of_channels(fr)
            
            if(len(channels) < len(use_channels)):
                raise Exception("Неправильный список каналов.")
                
            if(not use_channels.issubset(channels)):
                raise Exception("Неправильный список каналов.")
            
            while(1):
                out = read_one_line(fr)
                
                # End of file
                if(isinstance(out, type(EOFError))):
                    break
                
                # Empty string (\n)
                elif(isinstance(out, type(None))):
                    pass
                
                # Time
                elif(isinstance(out, float)):
                    cur_channel = 0
                    if(out>=0 and cur_time<out):
                        cur_time = out
                    else:
                        raise Exception("Неверное время")
                        
                # Power on i-channel
                elif(isinstance(out, np.ndarray)):
                    if('cur_channel' not in locals()):
                        raise Exception("В одном из блоков с каналами нет"
                                        "информации о времени.")
                    if(cur_channel>max(channels)):
                        raise Exception("В одном из блоков с каналами неверное"
                                        "количество каналов.")
                    if(out.shape[0]!=length_of_spectr):
                        raise Exception("Размеры записываемых массивов не "
                                        "совпадают.")
        
                    if(cur_channel in use_channels):    
                        new_fn = "_".join([fn, f"{cur_time}",
                                           f"{cur_channel}"]) + ".csv"
                        name = os.path.join(path_w, new_fn)
                        
                        # write data on i-channel
                        write_in_file(out, name)
                        counter += 1
                        
                    cur_channel += 1
                
                
    except Exception as e:
        print(f"\t\t{e}")
    
    finally:
        return counter


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Описание программы')
    parser.add_argument('path1', help='Путь к папке с txt файлами', type=str)
    parser.add_argument('path2', help='Путь к папке, в которую запишутся '\
                        'csv файлы.', type=str)
    parser.add_argument('-f', '--flag', dest='flag', help='Список с номерам'\
                        'и используемымых каналаов.\n Записать через запятую,'\
                        ' Нумерация начинается с 0.', type=str)
        
    args = parser.parse_args()
    
    input_path = args.path1
    output_path = args.path2
    
    if(not os.path.isdir(input_path)):
        print(f"Директории {input_path} не существует")
        sys.exit(-2)
        
    if(not os.access(input_path, os.R_OK)):
        print(f"К Директории {input_path} нет доступа.")
        sys.exit(-3)
        
    if(not os.path.isdir(output_path)):
        print(f"Директории {input_path} не существует")
        sys.exit(-2)
        
    if(not os.access(output_path, os.W_OK)):
        print(f"К Директории {output_path} нет доступа.")
        sys.exit(-3)
        
    if(args.flag):
        try:
            channels = {int(x.strip()) for x in args.flag.split(',') if x.strip()}
            
            if(len(channels)==0):
                raise Exception
                
        except Exception:
            print("Список каналов передан неправильно.")
            sys.exit(-1)
        
    else:
        channels = {0}
        
    print("\nПрограмма начала работу\n")
    print("\tВыбранные каналы: ", *channels, sep=" ", end='\n\n\n')
    
    total = 0
    
    for f in os.listdir(input_path):
        if not f.endswith('.txt'):
            continue
        else:
            print(f"Текущий файл: {f}.\n")
            
        full_in_dir = os.path.join(input_path, f)
        
        if(not os.access(full_in_dir, os.R_OK)):
            print(f"\nК файлу {f} нет доступа.")
            continue
            
        print(f"\nФайл {f} обрабатывается.")
        
        result = get_header_and_data_position(full_in_dir)
        if(result):
            header, position = result
        else:
            print(f"\tФайл {f} не подходит\n")
            continue
            
        wavelength = find_data_wavelength(header)
        
        if(wavelength is None):
            print(f"\tФайл {f} не подходит\n")
            continue
            
        output = read_file_and_write(input_path, output_path, f,
                                     wavelength, position, channels)
        if(output):
            total += output
            print(f"\n\tФайл {f} прочитан, {output} файлов записано в " \
                  f"папку {output_path}\n")
        else:
            print(f"\tФайл {f} прочитан, но значения не записаны\n")
            
    print(f"\nВсего записано {total} файлов.\n"
          "\nПрограмма закончила работу")
    sys.exit(0)