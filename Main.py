from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.storage.jsonstore import JsonStore
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle, RoundedRectangle

Window.clearcolor = (0, 0, 0, 1)

GOLD = (0.831, 0.686, 0.216, 1)
GOLD_HEX = '#D4AF37'
WHITE = (1, 1, 1, 1)
DARK_CARD = (0.067, 0.067, 0.067, 1)
DARK_BTN = (0.1, 0.1, 0.1, 1)
RED_DARK = (0.545, 0, 0, 1)
MUTED = (0.533, 0.533, 0.533, 1)
BLACK = (0, 0, 0, 1)

# Separamos os serviços em par do grid e o adicional que fica inteiro embaixo
SERVICOS_GRID = [
    ('cabelo',       'CABELO',        35.0),
    ('barba',        'BARBA',         25.0),
    ('combo',        'CABELO + BARBA', 55.0),
    ('sobrancelha',  'SOBRANCELHA',   10.0),
]

STORAGE_KEY = 'financeiro'
DEFAULT_DATA = {
    'diario': 0.0,
    'mensal': 0.0,
    'cortes': 0,
    'barbas': 0,
    'sobrs':  0,
    'u_valor': 0.0,
    'u_tipo': '',
}

def format_brl(value: float) -> str:
    return f'R$ {value:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

class RoundedButton(Button):
    def __init__(self, bg_color=GOLD, text_color=(0, 0, 0, 1), radius=8, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self._bg_color = bg_color
        self.color = text_color
        self._radius = radius
        self.bind(pos=self._update, size=self._update)

    def _update(self, *args):  
        self.canvas.before.clear()  
        with self.canvas.before:  
            Color(*self._bg_color)  
            RoundedRectangle(pos=self.pos, size=self.size,  
                             radius=[dp(self._radius)])

class SomavillaLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', spacing=dp(14),
                         padding=[dp(18), dp(24), dp(18), dp(18)], **kwargs)
        self.store = JsonStore('gestao_somavilla_v2.json')
        self.data = self._load()
        self._build()

    def _load(self):  
        if self.store.exists(STORAGE_KEY):  
            stored = dict(DEFAULT_DATA)  
            stored.update(self.store.get(STORAGE_KEY))  
            return stored  
        return dict(DEFAULT_DATA)  

    def _save(self):  
        self.store.put(STORAGE_KEY, **self.data)  

    def _build(self):  
        # --- Cabeçalho ---  
        header = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80),  
                           spacing=dp(2))  
        title = Label(text='SOMAVILLA BARBEARIA', font_size=dp(22),  
                      bold=True, color=GOLD, size_hint_y=None, height=dp(36),  
                      halign='center', valign='middle')  
        title.bind(size=title.setter('text_size'))  
        header.add_widget(title)  
        self.add_widget(header)  

        # --- Painel de faturamento ---  
        billing_card = BoxLayout(orientation='vertical', size_hint_y=None,  
                                 height=dp(120), spacing=dp(8),  
                                 padding=[dp(16), dp(12), dp(16), dp(12)])  
        with billing_card.canvas.before:  
            Color(*DARK_CARD)  
            self._billing_rect = RoundedRectangle(radius=[dp(12)])  
        billing_card.bind(pos=self._upd_billing, size=self._upd_billing)  

        self.lbl_hoje = Label(text=f'HOJE: {format_brl(self.data["diario"])}',  
                              font_size=dp(30), bold=True, color=GOLD,  
                              size_hint_y=None, height=dp(48),  
                              halign='center', valign='middle')  
        self.lbl_hoje.bind(size=self.lbl_hoje.setter('text_size'))  

        self.lbl_mes = Label(text=f'NO MÊS: {format_brl(self.data["mensal"])}',  
                             font_size=dp(16), color=WHITE,  
                             size_hint_y=None, height=dp(28),  
                             halign='center', valign='middle')  
        self.lbl_mes.bind(size=self.lbl_mes.setter('text_size'))  

        billing_card.add_widget(self.lbl_hoje)  
        billing_card.add_widget(self.lbl_mes)  
        self.add_widget(billing_card)  

        # --- Estatísticas ---  
        stats = GridLayout(cols=3, size_hint_y=None, height=dp(80), spacing=dp(10))  
        self.lbl_cortes = self._stat_card('CORTES', self.data['cortes'], stats)  
        self.lbl_barbas = self._stat_card('BARBAS', self.data['barbas'], stats)  
        self.lbl_sobrs  = self._stat_card('SOBRANCELHAS', self.data['sobrs'], stats)  
        self.add_widget(stats)  

        # --- Botões de serviços (Grid de 4 itens em 2 colunas) ---  
        services = GridLayout(cols=2, size_hint_y=None, height=dp(170), spacing=dp(12))  
        for tipo, label, valor in SERVICOS_GRID:  
            btn = RoundedButton(  
                text=f'{label}\n{format_brl(valor)}',  
                bg_color=GOLD,  
                text_color=BLACK,  
                radius=10,  
                font_size=dp(15),  
                bold=True,  
                halign='center',  
            )  
            btn.bind(on_release=lambda b, t=tipo, v=valor: self.registrar(t, v))  
            services.add_widget(btn)  
        self.add_widget(services)  

        # --- Botão Adicional inteiro embaixo do grid ---
        btn_adicional = RoundedButton(
            text=f'ADICIONAL\n{format_brl(5.0)}',
            bg_color=GOLD,
            text_color=BLACK,
            radius=10,
            font_size=dp(15),
            bold=True,
            halign='center',
            size_hint_y=None,
            height=dp(65)
        )
        btn_adicional.bind(on_release=lambda b: self.registrar('adicional', 5.0))
        self.add_widget(btn_adicional)

        # --- Botão Valor Personalizado ---
        self.btn_custom = RoundedButton(
            text='VALOR PERSONALIZADO',
            bg_color=DARK_BTN,
            text_color=GOLD,
            radius=10,
            font_size=dp(14),
            bold=True,
            size_hint_y=None,
            height=dp(52)
        )
        self.btn_custom.bind(on_release=lambda b: self._pedir_valor_personalizado())
        self.add_widget(self.btn_custom)

        # --- Apagar último ---  
        self.btn_undo = RoundedButton(  
            text=self._undo_text(),  
            bg_color=RED_DARK,  
            text_color=WHITE,  
            radius=10,  
            font_size=dp(13),  
            bold=True,  
            size_hint_y=None,  
            height=dp(52),  
        )  
        self.btn_undo.bind(on_release=lambda b: self.apagar_ultimo())  
        self.add_widget(self.btn_undo)  

        # --- Zerar dia / mês ---  
        resets = GridLayout(cols=2, size_hint_y=None, height=dp(52), spacing=dp(12))  

        btn_dia = RoundedButton(text='ZERAR DIA', bg_color=DARK_BTN,  
                                text_color=MUTED, radius=10,  
                                font_size=dp(13), bold=True)  
        btn_dia.bind(on_release=lambda b: self._confirmar(  
            'Zerar o faturamento do dia?', self.zerar_dia))  
        resets.add_widget(btn_dia)  

        btn_mes = RoundedButton(text='ZERAR MÊS', bg_color=DARK_BTN,  
                                text_color=MUTED, radius=10,  
                                font_size=dp(13), bold=True)  
        btn_mes.bind(on_release=lambda b: self._confirmar(  
            'Zerar TUDO?\nDados diários, mensais e contadores serão apagados.',  
            self.zerar_mes))  
        resets.add_widget(btn_mes)  

        self.add_widget(resets)  

    def _upd_billing(self, instance, *args):  
        self._billing_rect.pos  = instance.pos  
        self._billing_rect.size = instance.size  

    def _stat_card(self, label_text, value, parent):  
        card = BoxLayout(orientation='vertical', spacing=dp(2),  
                         padding=[dp(6), dp(8), dp(6), dp(8)])  
        with card.canvas.before:  
            Color(*DARK_CARD)  
            rect = RoundedRectangle(radius=[dp(10)])  
        card.bind(pos=lambda i, *a: setattr(rect, 'pos', i.pos),  
                  size=lambda i, *a: setattr(rect, 'size', i.size))  

        num = Label(text=str(value), font_size=dp(22), bold=True, color=GOLD,  
                    halign='center', valign='middle')  
        num.bind(size=num.setter('text_size'))  

        lbl = Label(text=label_text, font_size=dp(9), color=MUTED,  
                    halign='center', valign='middle')  
        lbl.bind(size=lbl.setter('text_size'))  

        card.add_widget(num)  
        card.add_widget(lbl)  
        parent.add_widget(card)  
        return num  

    def _undo_text(self):  
        if self.data['u_tipo'] and self.data['u_valor'] > 0:  
            tipo = self.data['u_tipo'].upper()  
            val  = format_brl(self.data['u_valor'])  
            return f'APAGAR ÚLTIMO  ({tipo} – {val})'  
        return 'APAGAR ÚLTIMO'  

    def _update_ui(self):  
        self.lbl_hoje.text   = f'HOJE: {format_brl(self.data["diario"])}'  
        self.lbl_mes.text    = f'NO MÊS: {format_brl(self.data["mensal"])}'  
        self.lbl_cortes.text = str(self.data['cortes'])  
        self.lbl_barbas.text = str(self.data['barbas'])  
        self.lbl_sobrs.text  = str(self.data['sobrs'])  
        self.btn_undo.text   = self._undo_text()  

    def registrar(self, tipo, valor):  
        self.data['diario']  = round(self.data['diario'] + valor, 2)  
        self.data['mensal']  = round(self.data['mensal'] + valor, 2)  
        self.data['u_valor'] = valor  
        self.data['u_tipo']  = tipo  
        if tipo == 'cabelo':      self.data['cortes'] += 1  
        elif tipo == 'barba':     self.data['barbas'] += 1  
        elif tipo == 'sobrancelha': self.data['sobrs'] += 1  
        elif tipo == 'combo':  
            self.data['cortes'] += 1  
            self.data['barbas'] += 1  
        self._save()  
        self._update_ui()  

    def apagar_ultimo(self):  
        if not self.data['u_tipo'] or self.data['u_valor'] == 0:  
            return  
        v = self.data['u_valor']  
        self.data['diario'] = max(0.0, round(self.data['diario'] - v, 2))  
        self.data['mensal'] = max(0.0, round(self.data['mensal'] - v, 2))  
        t = self.data['u_tipo']  
        if t == 'cabelo':       self.data['cortes'] = max(0, self.data['cortes'] - 1)  
        elif t == 'barba':      self.data['barbas'] = max(0, self.data['barbas'] - 1)  
        elif t == 'sobrancelha': self.data['sobrs']  = max(0, self.data['sobrs'] - 1)  
        elif t == 'combo':  
            self.data['cortes'] = max(0, self.data['cortes'] - 1)  
            self.data['barbas'] = max(0, self.data['barbas'] - 1)  
        self.data['u_valor'] = 0.0  
        self.data['u_tipo']  = ''  
        self._save()  
        self._update_ui()  

    def zerar_dia(self):  
        self.data['diario']  = 0.0  
        self.data['u_valor'] = 0.0  
        self.data['u_tipo']  = ''  
        self._save()  
        self._update_ui()  

    def zerar_mes(self):  
        self.data = dict(DEFAULT_DATA)  
        self._save()  
        self._update_ui()  

    def _pedir_valor_personalizado(self):
        content = BoxLayout(orientation='vertical', spacing=dp(16),  
                            padding=[dp(16), dp(16), dp(16), dp(16)])  
        with content.canvas.before:  
            Color(*DARK_CARD)  
            Rectangle(pos=content.pos, size=content.size)  

        lbl = Label(text='DIGITE O VALOR (EX: 45.50):', color=WHITE, font_size=dp(15),  
                    halign='center', valign='middle', size_hint_y=None, height=dp(30))  
        lbl.bind(size=lbl.setter('text_size'))  
        content.add_widget(lbl)  

        txt_input = TextInput(text='', multiline=False, input_type='number',
                              font_size=dp(18), size_hint_y=None, height=dp(40),
                              background_color=(0.15, 0.15, 0.15, 1), foreground_color=WHITE)
        content.add_widget(txt_input)

        btns = GridLayout(cols=2, spacing=dp(12), size_hint_y=None, height=dp(48))  

        popup = Popup(title='VALOR PERSONALIZADO', title_color=GOLD,  
                      title_size=dp(16), title_align='center',  
                      content=content, size_hint=(0.85, None), height=dp(220),  
                      background_color=(0.07, 0.07, 0.07, 1),  
                      separator_color=GOLD)  

        def confirmar(*a):  
            try:
                val_text = txt_input.text.replace(',', '.')
                valor = round(float(val_text), 2)
                if valor > 0:
                    self.registrar('personalizado', valor)
            except ValueError:
                pass
            popup.dismiss()  

        btn_nao = RoundedButton(text='CANCELAR', bg_color=DARK_BTN,  
                                text_color=MUTED, radius=8,  
                                font_size=dp(14), bold=True)  
        btn_nao.bind(on_release=popup.dismiss)  

        btn_sim = RoundedButton(text='OK', bg_color=GOLD,  
                                text_color=BLACK, radius=8,  
                                font_size=dp(14), bold=True)  
        btn_sim.bind(on_release=confirmar)  

        btns.add_widget(btn_nao)  
        btns.add_widget(btn_sim)  
        content.add_widget(btns)  

        popup.open()

    def _confirmar(self, mensagem, callback):  
        content = BoxLayout(orientation='vertical', spacing=dp(16),  
                            padding=[dp(16), dp(16), dp(16), dp(16)])  
        with content.canvas.before:  
            Color(*DARK_CARD)  
            Rectangle(pos=content.pos, size=content.size)  

        lbl = Label(text=mensagem, color=WHITE, font_size=dp(15),  
                    halign='center', valign='middle', size_hint_y=None, height=dp(60))  
        lbl.bind(size=lbl.setter('text_size'))  
        content.add_widget(lbl)  

        btns = GridLayout(cols=2, spacing=dp(12), size_hint_y=None, height=dp(48))  

        popup = Popup(title='CONFIRMAR', title_color=GOLD,  
                      title_size=dp(16), title_align='center',  
                      content=content, size_hint=(0.85, None), height=dp(200),  
                      background_color=(0.07, 0.07, 0.07, 1),  
                      separator_color=GOLD)  

        def sim(*a):  
            popup.dismiss()  
            callback()  

        btn_nao = RoundedButton(text='NÃO', bg_color=DARK_BTN,  
                                text_color=MUTED, radius=8,  
                                font_size=dp(14), bold=True)  
        btn_nao.bind(on_release=popup.dismiss)  

        btn_sim = RoundedButton(text='SIM', bg_color=GOLD,  
                                text_color=BLACK, radius=8,  
                                font_size=dp(14), bold=True)  
        btn_sim.bind(on_release=sim)  

        btns.add_widget(btn_nao)  
        btns.add_widget(btn_sim)  
        content.add_widget(btns)  

        popup.open()

class SomavillaApp(App):
    def build(self):
        self.title = 'Somavilla Barbearia'
        scroll = ScrollView()
        layout = SomavillaLayout(size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        scroll.add_widget(layout)
        return scroll

if __name__ == '__main__':
    SomavillaApp().run()
