import psutil  # INFO RISORSE SISTEMA
import tkinter as tk  # INTERFACCIA GRAFICA
from tkinter import ttk  # WIDGET
import threading
import csv  # ESPORTAZIONE DEI DATI IN FORMATO CSV
import json  # ESPORTAZIONE DEI DATI IN FORMATO JSON

# Funzione per ottenere la percentuale di utilizzo della CPU in tempo reale
def get_cpu_usage():
    return psutil.cpu_percent(interval=None)  # Usa interval=None per ottenere un valore immediato

# Funzione update_info: AGGIORNARE OGNI SECONDO LE % DI UTILIZZO CPU, MEMORIA, DISCO + PROCESSI ATTIVI
def update_info():
    cpu_percent.set(f"CPU: {get_cpu_usage()}%")
    mem = psutil.virtual_memory()
    memory_percent.set(f"Memory: {mem.percent}%")
    disk = psutil.disk_usage('/')
    disk_percent.set(f"Disk: {disk.percent}%")

    processes = psutil.pids()
    process_list.delete(*process_list.get_children())
    for pid in processes:
        try:
            p = psutil.Process(pid)
            # Aggiungi le informazioni sulla porta (se disponibili) e sul numero di thread
            connections = p.connections(kind='inet')
            port = None
            if connections:
                port = connections[0].laddr.port  # Porta di ascolto
            num_threads = p.num_threads()  # Numero di thread
            process_list.insert("", "end", values=(p.pid, p.name(), f"{p.cpu_percent():.2f}%", f"{p.memory_percent():.2f}%", p.status(), p.create_time(), port, num_threads))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    root.after(refresh_interval.get() * 1000, update_info)

# Funzione export_to_csv: ESPORTAZIONE DEI PROCESSI IN FILE CSV
def export_to_csv():
    with open("system_monitor.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["PID", "Name", "CPU Usage", "Memory Usage", "Status", "Start Time", "Port", "Threads"])
        for row in process_list.get_children():
            writer.writerow(process_list.item(row, "values"))

# Funzione export_to_json: ESPORTAZIONE DEI PROCESSI IN FILE JSON
def export_to_json():
    data = [process_list.item(row, "values") for row in process_list.get_children()]
    with open("system_monitor.json", "w") as file:
        json.dump(data, file, indent=4)

# Funzione filter_process: FILTRA I PROCESSI IN BASE ALLA QUERY DELL'UTENTE
def filter_process():
    query = search_var.get().lower()
    process_list.delete(*process_list.get_children())
    for pid in psutil.pids():
        try:
            p = psutil.Process(pid)
            # Aggiungi le informazioni sulla porta (se disponibili) e sul numero di thread
            connections = p.connections(kind='inet')
            port = None
            if connections:
                port = connections[0].laddr.port  # Porta di ascolto
            num_threads = p.num_threads()  # Numero di thread
            if query in p.name().lower() or query in str(p.pid):
                process_list.insert("", "end", values=(p.pid, p.name(), f"{p.cpu_percent():.2f}%", f"{p.memory_percent():.2f}%", p.status(), p.create_time(), port, num_threads))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

# INTERFACCIA GRAFICA + Widget
root = tk.Tk()
root.title("System Monitor")

# Impostazione del font globale per tutti i widget
root.option_add("*Font", "JetBrainsMonoNL-Thin 14")

# Creazione di uno stile personalizzato per il Treeview
style = ttk.Style()
style.configure("Treeview",
                font=("JetBrainsMonoNL-Thin", 14))  # Imposta il font per le righe
style.configure("Treeview.Heading",
                font=("JetBrainsMonoNL-Thin", 14))  # Imposta il font per le intestazioni

# VARIABILI
cpu_percent = tk.StringVar()
memory_percent = tk.StringVar()
disk_percent = tk.StringVar()
search_var = tk.StringVar()
refresh_interval = tk.IntVar(value=2)

# ETICHETTE INFORMATIVE
cpu_label = ttk.Label(root, textvariable=cpu_percent)
memory_label = ttk.Label(root, textvariable=memory_percent)
disk_label = ttk.Label(root, textvariable=disk_percent)

cpu_label.pack(pady=5)
memory_label.pack(pady=5)
disk_label.pack(pady=5)

# ELENCO PROCESSI
columns = ("PID", "Name", "CPU Usage", "Memory Usage", "Status", "Start Time", "Port", "Threads")
process_list = ttk.Treeview(root, columns=columns, show='headings')

# Configurazione delle intestazioni della tabella
for col in columns:
    process_list.heading(col, text=col)
    process_list.column(col, minwidth=0, width=150)

process_list.pack(pady=10, fill="x")

# CONTROLLI
control_frame = ttk.Frame(root)
control_frame.pack(pady=10)

ttk.Label(control_frame, text="Refresh Interval (s):").grid(row=0, column=0, padx=5)
refresh_scale = ttk.Scale(control_frame, from_=1, to=10, variable=refresh_interval, orient="horizontal")
refresh_scale.grid(row=0, column=1, padx=5)

ttk.Label(control_frame, text="Search:").grid(row=1, column=0, padx=5)
search_entry = ttk.Entry(control_frame, textvariable=search_var)
search_entry.grid(row=1, column=1, padx=5)

# Usa tk.Button invece di ttk.Button per il pulsante Filter
search_button = tk.Button(control_frame, text="Filter", command=filter_process, font=("JetBrainsMonoNL-Thin", 14))
search_button.grid(row=1, column=2, padx=5)

# Impostato il font per i pulsanti Export CSV e Export JSON
csv_button = tk.Button(control_frame, text="Export CSV", command=export_to_csv, font=("JetBrainsMonoNL-Thin", 14))
csv_button.grid(row=2, column=0, padx=5)

json_button = tk.Button(control_frame, text="Export JSON", command=export_to_json, font=("JetBrainsMonoNL-Thin", 14))
json_button.grid(row=2, column=1, padx=5)

# AVVIO MONITORAGGIO
update_info()
root.mainloop()









