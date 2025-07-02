# -*- coding: utf-8 -*-
"""
Created on Tue Jun 17 16:05:58 2025

@author: cleit
"""
import os
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import requests

#-------ENDPOINT DA API -----
API_URL = "http://127.0.0.1:8000/almoxarifado"

# ----- FUNÇÃO PARA REGISTRAR UMA PEÇA -
def register_part():
    part_name = entry_part_name.get().strip()
    manufacturer = entry_manufacturer.get().strip()
    sector = entry_sector.get().strip()
    aircraft = entry_aircraft.get().strip()
    quantity = entry_quantity.get().strip()
    value = entry_value.get().strip()

    if not all([part_name, manufacturer, sector, aircraft, quantity, value]):
        messagebox.showerror("Error", "Please fill in all fields.")
        return

    try:
        quantity = int(quantity)
        value = float(value)
    except ValueError:
        messagebox.showerror("Error", "Quantity must be integer and Value must be decimal.")
        return

    response = requests.post(API_URL, json={
        "part_name": part_name,
        "manufacturer": manufacturer,
        "application_sector": sector,
        "aircraft": aircraft,
        "quantity": quantity,
        "value": value
    })

    if response.status_code == 200:
        messagebox.showinfo("Success", "Part registered successfully.")
        for e in entries:
            e.delete(0, tk.END)
        list_parts()
    else:
        messagebox.showerror("Error", response.json().get("detail", "Error registering part."))

# ----- FUNÇÃO PARA LISTAR AS PEÇAS REGISTRADAS -----
def list_parts():
    for item in tree.get_children():
        tree.delete(item)

    response = requests.get(API_URL)
    if response.status_code == 200:
        parts = response.json()
        for part in parts:
            tree.insert("", tk.END, values=(
                part.get("id"),
                part.get("part_name"),
                part.get("manufacturer"),
                part.get("application_sector"),
                part.get("aircraft"),
                part.get("quantity"),
                part.get("value")
            ))

# ----- JANELA PRINCIPAL -----
root = tk.Tk()
root.title("PART REGISTRATION")
root.geometry("800x700")

# ----- CAMINHO RELATIVO DA IMAGEM DE FUNDO -----
current_dir = os.path.dirname(__file__)
image_path = os.path.join(current_dir, "image", "aviao.jpg")

# ----- IMAGEM DE FUNDO -----
bg_image = Image.open(image_path)
bg_image = bg_image.resize((800, 700), Image.Resampling.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_image)

canvas = tk.Canvas(root, width=800, height=600)
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, image=bg_photo, anchor="nw")

# ----- CAMPOS DE ENTRADA -----
labels = ["PART NAME:", "MANUFACTURER:", "APPLICATION SECTOR:", "AIRCRAFT:", "QUANTITY:", "VALUE:"]
entries = []

for i, label in enumerate(labels):
    canvas.create_text(120, 30 + i*40, text=label, anchor="w", font=("Arial", 10, "bold"), fill="white")
    entry = tk.Entry(root, width=40)
    canvas.create_window(280, 20 + i*40, anchor="nw", window=entry)
    entries.append(entry)

entry_part_name, entry_manufacturer, entry_sector, entry_aircraft, entry_quantity, entry_value = entries

# ----- BOTÃO DE REGISTRO -----
register_button = tk.Button(root, text="REGISTER", command=register_part)
canvas.create_window(370, 270, anchor="nw", window=register_button)

# ----- TABELA DE PEÇAS (TREEVIEW) -----
columns = ("ID", "PART NAME", "MANUFACTURER", "SECTOR", "AIRCRAFT", "QUANTITY", "VALUE")
tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=100)

canvas.create_window(50, 320, anchor="nw", window=tree)

# ----- CARREGAR DADOS INICIAIS -----
list_parts()

# ----- EVITA ERRO DE IMAGEM AO VIVO -----
root.bg_photo = bg_photo

# ----- EXECUTAR A INTERFACE -----
root.mainloop()

