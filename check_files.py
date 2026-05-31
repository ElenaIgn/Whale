import os

print("--- КОРНЕВАЯ ПАПКА ПРОЕКТА ---")
print("Текущая рабочая директория:", os.getcwd())

print("\n--- СОДЕРЖИМОЕ КОРНЕВОЙ ПАПКИ ---")
try:
    items = os.listdir('.')
    for item in items:
        print(f"  [{'ПАПКА' if os.path.isdir(item) else 'ФАЙЛ'}] {item}")
except Exception as e:
    print("Ошибка чтения корня:", e)

print("\n--- ИЩЕМ КАРТИНКИ И ТЕКСТОВЫЕ ФАЙЛЫ В ПРОЕКТЕ ---")
image_exts = ('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG')
found_any_img = 0
found_any_txt = 0

for root, dirs, files in os.walk('.'):
    
    if 'venv' in root or '.git' in root or '.vscode' in root:
        continue
    
    for f in files:
        if f.endswith(image_exts):
            found_any_img += 1
            if found_any_img <= 3:
                print(f"  Найдена картинка: {os.path.join(root, f)}")
        elif f.endswith('.txt') and f != 'requirements.txt' and f != 'classes.txt':
            found_any_txt += 1
            if found_any_txt <= 3:
                print(f"  Найден .txt файл: {os.path.join(root, f)}")

print(f"\nВсего в проекте (исключая venv) обнаружено:")
print(f"  Картинок: {found_any_img}")
print(f"  Текстовых файлов разметки: {found_any_txt}")
