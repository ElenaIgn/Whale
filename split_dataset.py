import os
import random
import shutil

def collect_and_split_dataset(search_dir, output_dir, train_ratio=0.75):
    
    subdirs = [
        'train/images', 'train/labels',
        'val/images', 'val/labels'
    ]
    for subdir in subdirs:
        os.makedirs(os.path.join(output_dir, subdir), exist_ok=True)

    image_extensions = ('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG')
    
    found_images = {}  
    found_labels = {}  

    print(f"Шаг 1: Сканирование папки {search_dir}...")
    
    
    for root, dirs, files in os.walk(search_dir):
        for file in files:
            name_without_ext, ext = os.path.splitext(file)
            
           
            if ext in image_extensions:
                found_images[name_without_ext] = os.path.join(root, file)
            
            elif ext == '.txt' and file not in ['classes.txt', 'train.txt']:
                found_labels[name_without_ext] = os.path.join(root, file)

   
    valid_basenames = list(set(found_images.keys()) & set(found_labels.keys()))
    
    if not valid_basenames:
        print("ОШИБКА: Не найдено ни одной пары (картинка + .txt разметка) с одинаковыми именами!")
        print(f"Всего картинок найдено: {len(found_images)}, всего .txt файлов: {len(found_labels)}")
        return

    
    random.seed(42) 
    random.shuffle(valid_basenames)

    # Рассчитываем пропорцию разделения (75% train, 25% val)
    split_index = int(len(valid_basenames) * train_ratio)
    train_basenames = valid_basenames[:split_index]
    val_basenames = valid_basenames[split_index:]

    print(f"\nУспешно сопоставлено парных файлов: {len(valid_basenames)}")
    print(f"Направлено в TRAIN (обучение): {len(train_basenames)}")
    print(f"Направлено в VAL (валидация): {len(val_basenames)}")

    
    def copy_matched_files(basename_list, subset):
        copied_count = 0
        for name in basename_list:
            img_src = found_images[name]
            txt_src = found_labels[name]
            
            img_file_name = os.path.basename(img_src)
            txt_file_name = os.path.basename(txt_src)
            
            shutil.copy2(img_src, os.path.join(output_dir, subset, 'images', img_file_name))
            shutil.copy2(txt_src, os.path.join(output_dir, subset, 'labels', txt_file_name))
            copied_count += 1
        print(f"Успешно скопировано в '{subset}': {copied_count} пар.")

    
    print("\nШаг 2: Распределение и копирование файлов...")
    copy_matched_files(train_basenames, 'train')
    copy_matched_files(val_basenames, 'val')
    print("\n--- Процесс успешно завершен! Датасет полностью готов в папке 'whale_dataset' ---")

if __name__ == "__main__":
    # Запускаем с учетом вашей папки cvat_donload
    collect_and_split_dataset(search_dir='cvat_donload', output_dir='whale_dataset', train_ratio=0.75)
