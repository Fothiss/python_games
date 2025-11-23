from pathlib import Path

def simple_tree(directory='.', max_depth=4):
    """Простая генерация дерева проекта"""
    ignore = {
        '__pycache__', '.git', '.idea', 'venv', '.venv', 
        'node_modules', '.vscode', 'build', 'dist'
    }
    
    directory = Path(directory)
    
    def print_tree(path, prefix="", is_last=True, depth=0):
        if depth > max_depth:
            return
            
        # Текущий элемент
        connector = "└── " if is_last else "├── "
        print(prefix + connector + path.name)
        
        if path.is_dir():
            # Получаем содержимое
            try:
                items = sorted(path.iterdir())
                # Фильтруем
                items = [item for item in items 
                        if item.name not in ignore 
                        and not item.name.startswith('.')]
                
                # Разделяем папки и файлы
                dirs = [item for item in items if item.is_dir()]
                files = [item for item in items if item.is_file() and 
                        (item.suffix == '.py' or item.name in 
                        ['requirements.txt', 'Dockerfile', 'README.md'])]
                
                all_items = dirs + files
                
            except PermissionError:
                all_items = []
            
            # Рекурсивно обрабатываем
            for i, item in enumerate(all_items):
                is_last_item = i == len(all_items) - 1
                new_prefix = prefix + ("    " if is_last else "│   ")
                print_tree(item, new_prefix, is_last_item, depth + 1)
    
    print_tree(directory, "", True, 0)

if __name__ == "__main__":
    simple_tree('.', 5)