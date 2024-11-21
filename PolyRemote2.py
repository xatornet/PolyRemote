import tkinter as tk
from tkinter import filedialog, messagebox
import os
import subprocess

# Archivo donde se almacenarán los ejecutables y sus rutas
DATABASE_FILE = "executables.txt"
STEAM_LIBRARY_PATH_FILE = "steam_library.txt"
POLYGUNNERS_APP_ID = 1853840  # ID del juego Polygunners
POLY_ROOT = ""  # Variable para almacenar la ruta de la librería de Steam

# Función para cargar la ruta de la librería de Steam
def load_steam_library_path():
    global POLY_ROOT
    if os.path.exists(STEAM_LIBRARY_PATH_FILE):
        with open(STEAM_LIBRARY_PATH_FILE, "r") as file:
            POLY_ROOT = file.readline().strip()
    else:
        # Solicitar al usuario la ruta de la librería de Steam
        POLY_ROOT = filedialog.askdirectory(title="Selecciona la carpeta COMMON de tu librería de Steam")
        if POLY_ROOT:
            # Comprobar si Polygunners está instalado
            polygunners_path = os.path.join(POLY_ROOT, "Polygunners")
            if os.path.exists(polygunners_path):
                messagebox.showinfo("Éxito", "Polygunners encontrado.")
            else:
                install_polygunners()
            with open(STEAM_LIBRARY_PATH_FILE, "w") as file:
                file.write(POLY_ROOT)
        else:
            messagebox.showerror("Error", "No se seleccionó ninguna ruta. Cerrando la aplicación.")
            app.quit()

# Función para instalar Polygunners si no está presente
def install_polygunners():
    answer = messagebox.askyesno("Instalar Polygunners", "No se encontró Polygunners. ¿Deseas instalarlo?")
    if answer:
        subprocess.run(["start", f"steam://install/{POLYGUNNERS_APP_ID}"], shell=True)

        # Pausa para esperar la instalación
        messagebox.showinfo("Instalación de Polygunners", 
                            "Cuando se TERMINE la instalación de Polygunners, pulse OK en este mensaje.")
        
        # Renombrar la carpeta una vez que se haya ejecutado el juego
        polygunners_path = os.path.join(POLY_ROOT, "Polygunners")
        if os.path.exists(polygunners_path):
            os.rename(polygunners_path, os.path.join(POLY_ROOT, "Polygunners_bak"))
            messagebox.showinfo("Éxito", "Polygunners ha sido renombrado a Polygunners_bak.")
        else:
            messagebox.showerror("Error", "No se encontró la carpeta de Polygunners después de la instalación.")
    else:
        app.quit()

# Función para cargar los ejecutables almacenados
def load_executables():
    executables = []
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, "r") as file:
            lines = file.readlines()
            for i in range(0, len(lines), 2):
                exe = lines[i].strip().split(": ")[1]
                path = lines[i+1].strip().split(": ")[1]
                executables.append((exe, path))
    return executables

# Función para guardar los ejecutables en el archivo
def save_executables(executables):
    with open(DATABASE_FILE, "w") as file:
        for exe, path in executables:
            file.write(f"EXE SELECCIONADO: {exe}\n")
            file.write(f"RUTA EXE SELECCIONADO: {path}\n")

# Función para agregar un nuevo ejecutable
def add_executable():
    filepath = filedialog.askopenfilename(filetypes=[("EXE Files", "*.exe")])
    if filepath:
        exe_name = os.path.basename(filepath)
        exe_dir = os.path.dirname(filepath)
        executables.append((exe_name, exe_dir))
        save_executables(executables)
        update_listbox()
        
        # Verificar si ya existe un softlink "Polygunners.exe"
        exe_symlink = os.path.join(exe_dir, "Polygunners.exe")
        if not os.path.exists(exe_symlink):
            os.system(f'mklink "{exe_symlink}" "{os.path.join(exe_dir, exe_name)}"')

# Función para quitar un ejecutable
def remove_executable():
    selected = listbox.curselection()
    if selected:
        exe, path = executables[selected[0]]
        exe_symlink = os.path.join(path, "Polygunners.exe")
        
        # Borrar el softlink en la carpeta del EXE
        if os.path.exists(exe_symlink):
            os.remove(exe_symlink)
        
        # Borrar el softlink en POLY_ROOT
        poly_symlink = os.path.join(POLY_ROOT, "Polygunners")
        if os.path.exists(poly_symlink):
            os.remove(poly_symlink)
        
        # Eliminar el ejecutable de la base de datos
        executables.pop(selected[0])
        save_executables(executables)
        update_listbox()

# Función para crear symlink en POLY_ROOT
def create_symlink():
    selected = listbox.curselection()
    if selected:
        exe, path = executables[selected[0]]
        poly_symlink = os.path.join(POLY_ROOT, "Polygunners")
        
        # Borrar el symlink previo si existe
        if os.path.exists(poly_symlink):
            os.remove(poly_symlink)
        
        # Crear nuevo symlink
        os.system(f'mklink /d "{poly_symlink}" "{path}"')
        messagebox.showinfo("Éxito", f"Symlink creado en {POLY_ROOT}")

# Función para actualizar la lista de ejecutables en la GUI
def update_listbox():
    listbox.delete(0, tk.END)
    for exe, path in executables:
        listbox.insert(tk.END, f"{exe} - {path}")

# Configurar la interfaz gráfica
app = tk.Tk()
app.title("PolyRemote Alpha")
app.geometry("500x400")

# Cargar la ruta de la librería de Steam
load_steam_library_path()

# Lista de ejecutables
executables = load_executables()

# Listbox para mostrar los ejecutables
listbox = tk.Listbox(app, height=10)
listbox.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

# Botones
btn_add = tk.Button(app, text="Agregar App", command=add_executable)
btn_add.pack(pady=5)

btn_remove = tk.Button(app, text="Quitar App", command=remove_executable)
btn_remove.pack(pady=5)

btn_symlink = tk.Button(app, text="Hazlo Remote!", command=create_symlink)
btn_symlink.pack(pady=5)

# Inicializar la lista
update_listbox()

# Ejecutar la aplicación
app.mainloop()


# Recuerda, para compilar este script necesitas PyInstaller https://pyinstaller.org/en/stable/installation.html
# Y cuando lo tengas, compila con "pyinstaller --onefile --windowed PolyRemote.py"