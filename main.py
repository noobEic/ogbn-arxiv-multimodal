import os
import argparse
from ogb.nodeproppred import PygNodePropPredDataset
from torch_geometric.data import DataLoader
import pandas as pd
import csv
from arxiv_downloader.downloader import *
import tarfile
import gzip
import shutil

def get_split(nodeid, train_set, valid_set, test_set):
    if nodeid in train_set:
        return 'train'
    elif nodeid in valid_set:
        return 'valid'
    elif nodeid in test_set:
        return 'test'
    else:
        raise ValueError('Invalid node id')
    


def retain_files_with_extensions(root_dir, extensions):
    processed_exts = ['.' + ext.lower().lstrip('.') for ext in extensions]
    print("Processing: ", root_dir)
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext in processed_exts:
                if dirpath != root_dir:
                    dest_path = os.path.join(root_dir, filename)

                    counter = 1
                    while os.path.exists(dest_path):
                        base, ext = os.path.splitext(filename)
                        dest_path = os.path.join(root_dir, f"{base}_{counter}{ext}")
                        counter += 1
                    try:
                        shutil.move(file_path, dest_path)
                    except Exception as e:
                        print(f"移动失败 {file_path} -> {dest_path}: {str(e)}")
            else:
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"删除失败 {file_path}: {str(e)}")

    for dirpath, dirnames, _ in os.walk(root_dir, topdown=False):
        for dirname in dirnames:
            full_dir = os.path.join(dirpath, dirname)
            if full_dir != root_dir:
                try:
                    shutil.rmtree(full_dir)
                except Exception as e:
                    print(f"删除目录失败 {full_dir}: {str(e)}")


def extract_tar_gz(folder: str) -> None:
    archives = [f for f in os.listdir(folder) if f.endswith(".tar.gz")]
    archive_path = os.path.join(folder, archives[0])
    temp_tar = os.path.join(folder, "temp.tar")
    try:
        with gzip.open(archive_path, 'rb') as f_in:
            with open(temp_tar, 'wb') as f_out:
                f_out.write(f_in.read())
                
        with tarfile.open(temp_tar, 'r') as tar:
            tar.extractall(folder)
            print(f"Extracting {archive_path}")
    finally:
        if os.path.exists(temp_tar):
            os.remove(temp_tar)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download ogbn-arxiv-multimodal dataset')
    parser.add_argument('--dir', type=str, default='./ogbn-arxiv-papers', help='Directory to store the dataset')

    args = parser.parse_args()

    dir_name = args.dir
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    os.makedirs(f'{dir_name}/train', exist_ok=True)
    os.makedirs(f'{dir_name}/valid', exist_ok=True)
    os.makedirs(f'{dir_name}/test', exist_ok=True)
    
    train_set = set()
    valid_set = set()
    test_set = set()

    with open("raw/train.csv") as fd:
        rd = csv.reader(fd)
        for row in rd:
            train_set.add(row[0])

    with open("raw/valid.csv") as fd:
        rd = csv.reader(fd)
        for row in rd:
            valid_set.add(row[0])
    
    with open("raw/test.csv") as fd:
        rd = csv.reader(fd)
        for row in rd:
            test_set.add(row[0])


    
    dic = {}




    with open("raw/titleabs.tsv", "r", encoding="utf-8", errors="replace") as fd:
        clean_lines = (line.replace('\x00', '') for line in fd)
        rd = csv.reader(clean_lines, delimiter="\t")
        for row in rd:
            dic[row[0]] = row[1]
    
    extensions = ['pdf','png','jpg','jpeg','eps']

    with open("raw/nodeidx2paperid.csv") as fd2:
        i = 0
        clean_lines = (line.replace('\x00', '') for line in fd2)
        rd2 = csv.reader(clean_lines)
        for row in rd2:
            print(row[0],dic[row[1]])
            split = get_split(row[0], train_set, valid_set, test_set)
            print(split)
            os.makedirs(f'{dir_name}/{split}/{row[0]}', exist_ok=True)
            if download_by_title(dic[row[1]],f'{dir_name}/{split}/{row[0]}'):
                extract_tar_gz(f'{dir_name}/{split}/{row[0]}')
                retain_files_with_extensions(f'{dir_name}/{split}/{row[0]}', extensions)
            i+=1
            if i==10: 
                break
    
    
