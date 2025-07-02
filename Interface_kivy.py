# -*- coding: utf-8 -*-
"""
Created on Wed Jun 18 15:42:50 2025

@author: cleit
"""

from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
import requests
import sys

API_URL = "http://127.0.0.1:8000/almoxarifado"

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = MDBoxLayout(orientation='vertical', spacing=10, padding=20)
        self.add_widget(self.layout)

        self.build_form()
        self.build_buttons()
        self.build_table()

    def build_form(self):
        self.fields = {}

        field_names = [
            ("part_name", "Part Name"),
            ("manufacturer", "Manufacturer"),
            ("application_sector", "Application Sector"),
            ("aircraft", "Aircraft"),
            ("quantity", "Quantity"),
            ("value", "Value")
        ]

        for key, hint in field_names:
            field = MDTextField(hint_text=hint, mode="rectangle")
            self.fields[key] = field
            self.layout.add_widget(field)

    def build_buttons(self):
        btn_layout = MDBoxLayout(size_hint_y=None, height=dp(50), spacing=10)

        self.register_btn = MDRaisedButton(text="Cadastrar", on_release=self.register_part)
        self.exit_btn = MDRaisedButton(text="Sair", on_release=self.exit_app)

        btn_layout.add_widget(self.register_btn)
        btn_layout.add_widget(self.exit_btn)

        self.layout.add_widget(btn_layout)

    def build_table(self):
        self.scroll = ScrollView()
        self.table = None
        self.layout.add_widget(self.scroll)
        self.load_table()

    def load_table(self):
        response = requests.get(API_URL)
        if response.status_code == 200:
            parts = response.json()
            table_data = [
                (
                    part["id"],
                    part["part_name"],
                    part["manufacturer"],
                    part["application_sector"],
                    part["aircraft"],
                    str(part["quantity"]),
                    f'{part["value"]:.2f}'
                ) for part in parts
            ]

            if self.table:
                self.scroll.remove_widget(self.table)

            self.table = MDDataTable(
                size_hint=(1, 1),
                use_pagination=True,
                rows_num=8,
                column_data=[
                    ("ID", dp(30)),
                    ("PART", dp(60)),
                    ("MANUFACTURER", dp(60)),
                    ("SECTOR", dp(60)),
                    ("AIRCRAFT", dp(60)),
                    ("QTY", dp(30)),
                    ("VALUE", dp(50)),
                ],
                row_data=table_data
            )

            self.scroll.add_widget(self.table)

    def register_part(self, *args):
        try:
            data = {
                "part_name": self.fields["part_name"].text.strip(),
                "manufacturer": self.fields["manufacturer"].text.strip(),
                "application_sector": self.fields["application_sector"].text.strip(),
                "aircraft": self.fields["aircraft"].text.strip(),
                "quantity": int(self.fields["quantity"].text.strip()),
                "value": float(self.fields["value"].text.strip())
            }
        except ValueError:
            print("Erro: quantidade precisa ser número inteiro e valor decimal.")
            return

        response = requests.post(API_URL, json=data)
        if response.status_code == 200:
            print("Peça cadastrada com sucesso.")
            for field in self.fields.values():
                field.text = ""
            self.load_table()
        else:
            print("Erro ao cadastrar:", response.json())

    def exit_app(self, *args):
        MDApp.get_running_app().stop()
        Window.close()
        sys.exit(0)

class KivyPartApp(MDApp):
    def build(self):
        Window.bind(on_request_close=self.on_request_close)
        self.theme_cls.theme_style = "Dark"
        return MainScreen()
    
    def on_request_close(self, *args):
        sys.exit(0)

if __name__ == "__main__":
    KivyPartApp().run()
