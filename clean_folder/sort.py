from pathlib import Path
import shutil
import sys
import re

IMAGES = []
AUDIO = []
VIDEO = []
DOCUMENT = []
MY_OTHER = []
ARCHIVES = []

CYRILLIC_SYMBOLS = 'абвгґдеєжзиіїйклмнопрстуфхцчшщьюя'
TRANSLATION = ("a", "b", "v", "g","g", "d", "e", "je", "j", "z","u", "i","ji", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch",  "",  "yu", "u", "ja")
TRANS = {}

REGISTER_EXTENSION = {'JPEG': IMAGES,'JPG': IMAGES,'PNG': IMAGES,'SVG': IMAGES,
                      'AVI': VIDEO, 'MP4': VIDEO, 'MOV': VIDEO, 'MKV': VIDEO,
                      'DOC': DOCUMENT, 'DOCX': DOCUMENT, 'TXT': DOCUMENT, 'PDF': DOCUMENT, 'XLSX': DOCUMENT, 'PPTX': DOCUMENT,
                      'MP3': AUDIO, 'OGG': AUDIO, 'WAV': AUDIO, 'AMR': AUDIO,
                      'ZIP': ARCHIVES, 'GZ': ARCHIVES, 'TAR' : ARCHIVES}

FOLDERS = []
EXTENSION = set()
UNKNOWN = set()

def get_extension(filename: str) -> str:
    return Path(filename).suffix[1:].upper() 


def scan(folder: Path) -> None:
    for item in folder.iterdir():
        if item.is_dir():
            if item.name not in ('archives', 'video', 'audio', 'documents', 'images', 'uknown'):
                FOLDERS.append(item)
                scan(item) 
            continue 
        
        ext = get_extension(item.name) 
        fullname = folder / item.name  
        if not ext:
            MY_OTHER.append(fullname)
        else:
            try:
                container = REGISTER_EXTENSION[ext]
                EXTENSION.add(ext)
                container.append(fullname)
            except KeyError:
                UNKNOWN.add(ext)
                MY_OTHER.append(fullname)


for c, l in zip(CYRILLIC_SYMBOLS, TRANSLATION):
    TRANS[ord(c)] = l
    TRANS[ord(c.upper())] = l.upper()

def normalize(name: str) -> str:
    t_name = name.translate(TRANS)
    t_name = re.sub(r'\W(?<!\.)', '_', t_name)
    print(t_name)
    return t_name


def handle_all(filename: Path, target_folder: Path) -> None:
    target_folder.mkdir(exist_ok=True, parents=True)
    filename.replace(target_folder / normalize(filename.name))

def handle_other(filename: Path, target_folder: Path) -> None:
    target_folder.mkdir(exist_ok=True, parents=True)
    filename.replace(target_folder / normalize(filename.name))

def handle_archive(filename: Path, target_folder: Path) -> None:
    target_folder.mkdir(exist_ok=True, parents=True)
    folder_for_file = target_folder / normalize(filename.name.replace(filename.suffix, ''))
    folder_for_file.mkdir(exist_ok=True, parents=True)
    try:
        shutil.unpack_archive(filename, folder_for_file)
    except shutil.ReadError:
        print('It is not archive')
        folder_for_file.rmdir()
    filename.unlink()

def handle_folder(folder: Path):
    try:
        folder.rmdir()
    except OSError:
        print(f"Can't delete folder: {folder}")

def main(folder: Path):
    scan(folder)
    for file in IMAGES:
        handle_all(file, folder / 'images' )
    for file in AUDIO:
        handle_all(file, folder / 'audio' )
    for file in VIDEO:
        handle_all(file, folder / 'video')
    for file in DOCUMENT:
        handle_all(file, folder / 'documents')
    for file in MY_OTHER:
        handle_all(file, folder / 'uknown')
    for file in ARCHIVES:
        handle_archive(file, folder / 'archives')
    for folder in FOLDERS[::-1]:
        handle_folder(folder)
    print(f'Types of files in folder: {EXTENSION}')
    print(f'Unknown files of types: {UNKNOWN}')

def start():
     if sys.argv[1]:
        folder_for_scan = Path(sys.argv[1])
        print(f'Start in folder: {folder_for_scan.resolve()}')
        main(folder_for_scan.resolve())

if __name__ == "__main__":
    if sys.argv[1]:
        folder_for_scan = Path(sys.argv[1])
        print(f'Start in folder: {folder_for_scan.resolve()}')
        main(folder_for_scan.resolve())