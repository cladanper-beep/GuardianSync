import sqlite3
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle

class GuardianSyncApp(App):
    def build(self):
        self.title = "GuardianSync - Pro"
        self.guardia_activo = None
        self.init_db()

        self.layout_principal = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        with self.layout_principal.canvas.before:
            Color(0.06, 0.09, 0.15, 1)
            self.rect = Rectangle(size=self.layout_principal.size, pos=self.layout_principal.pos)
        self.layout_principal.bind(size=self._update_rect, pos=self._update_rect)

        self.mostrar_pantalla_login()
        return self.layout_principal

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def init_db(self):
        conn = sqlite3.connect('guardiansync_local.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rondas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guardia_nombre TEXT,
                punto_control TEXT,
                timestamp DATETIME
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS guardias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE,
                pin TEXT
            )
        ''')
        cursor.execute("INSERT OR IGNORE INTO guardias (nombre, pin) VALUES ('C. Perales', '1234')")
        cursor.execute("INSERT OR IGNORE INTO guardias (nombre, pin) VALUES ('J. Gomez', '5678')")
        conn.commit()
        conn.close()

    def mostrar_pantalla_login(self):
        self.layout_principal.clear_widgets()
        self.layout_principal.add_widget(Label(text="[b]GuardianSync - Acceso Seguro[/b]", markup=True, font_size=20, size_hint_y=None, height=40, color=(1, 1, 1, 1)))
        self.layout_principal.add_widget(Label(text="Nombre del Guardia:", size_hint_y=None, height=25, color=(0.8, 0.8, 0.8, 1)))
        self.input_login_nombre = TextInput(text="C. Perales", multiline=False, size_hint_y=None, height=45)
        self.layout_principal.add_widget(self.input_login_nombre)
        self.layout_principal.add_widget(Label(text="PIN Personal de Seguridad:", size_hint_y=None, height=25, color=(0.8, 0.8, 0.8, 1)))
        self.input_login_pin = TextInput(text="", password=True, multiline=False, size_hint_y=None, height=45)
        self.layout_principal.add_widget(self.input_login_pin)

        btn_login = Button(text="Iniciar Turno (PIN)", background_color=(0.13, 0.59, 0.95, 1), size_hint_y=None, height=50)
        btn_login.bind(on_press=self.validar_login_accion)
        self.layout_principal.add_widget(btn_login)
        self.label_estado_login = Label(text="Ingrese credenciales para comenzar.", color=(0.7, 0.8, 0.9, 1))
        self.layout_principal.add_widget(self.label_estado_login)

    def validar_login_accion(self, instance):
        nombre = self.input_login_nombre.text.strip()
        pin = self.input_login_pin.text.strip()
        conn = sqlite3.connect('guardiansync_local.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM guardias WHERE nombre = ? AND pin = ?", (nombre, pin))
        resultado = cursor.fetchone()
        conn.close()

        if resultado:
            self.guardia_activo = nombre
            self.mostrar_pantalla_operativa()
        else:
            self.label_estado_login.text = "[Error] PIN incorrecto o guardia no autorizado."

    def mostrar_pantalla_operativa(self):
        self.layout_principal.clear_widgets()
        self.layout_principal.add_widget(Label(text=f"[b]Turno Activo:[/b] {self.guardia_activo}", markup=True, font_size=18, size_hint_y=None, height=35, color=(0.16, 0.72, 0.53, 1)))
        
        btn_escanear = Button(text="Registrar Punto de Control (QR)", background_color=(0.13, 0.59, 0.95, 1), size_hint_y=None, height=50)
        btn_escanear.bind(on_press=self.registrar_punto_accion)
        self.layout_principal.add_widget(btn_escanear)

        btn_cerrar = Button(text="Cerrar Turno (Cambio de Guardia)", background_color=(0.90, 0.30, 0.30, 1), size_hint_y=None, height=40)
        btn_cerrar.bind(on_press=lambda x: self.mostrar_pantalla_login())
        self.layout_principal.add_widget(btn_cerrar)

        self.label_estado = Label(text="Sistema operativo seguro activo.", color=(0.7, 0.8, 0.9, 1))
        self.layout_principal.add_widget(self.label_estado)

    def registrar_punto_accion(self, instance):
        punto_detectado = "QR-PUNTO-PERIMETRO-NORTE"
        conn = sqlite3.connect('guardiansync_local.db')
        cursor = conn.cursor()
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('INSERT INTO rondas (guardia_nombre, punto_control, timestamp) VALUES (?, ?, ?)', (self.guardia_activo, punto_detectado, ahora))
        conn.commit()
        conn.close()
        self.label_estado.text = f"[Éxito] Marcación registrada por {self.guardia_activo}"

if __name__ == '__main__':
    GuardianSyncApp().run()
