import json
import os
import shutil
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from pnadcontinua.utils import (
    wrap_string, get_vars_from_bin_dict, get_var_desc, has_duplicates,
    is_numeric
)
from pnadcontinua.core import (
    get_quarter_data_urls, download_data, load_data, filter_cat_column,
    filter_num_column, calculate_totals, get_deflator
)
from pnadcontinua.constants import (
    DATA_FOLDER, TEMP_FOLDER, DOWNLOADED_DATA_FILE, TUTORIAL_URL
)
from pnadcontinua.metadata import (
    VARIABLES_MAPPING, VARIABLES_DESCRIPTION, ALL_GROUP, MAIN_GROUP,
    WORK_GROUP, EDUCATION_GROUP, NUMERICAL_GROUP, DEFLATOR_GROUP
)


CURRENT_DIR = os.path.dirname(__file__)
DATA_FOLDER_PATH = os.path.join(CURRENT_DIR, "..", DATA_FOLDER)
TEMP_FOLDER_PATH = os.path.join(CURRENT_DIR, "..", TEMP_FOLDER)
DOWNLOADED_DATA_PATH = os.path.join(CURRENT_DIR, "..", DOWNLOADED_DATA_FILE)


class HomeFrame(ttk.Frame):
    def __init__(self, root):
        super().__init__(root)

        self.btns_width = 25
        self.btns_height = 45

        self.grid_columnconfigure(0, weight=1)
        for row in range(1, 6):
            self.grid_rowconfigure(row, minsize=self.btns_height)

        self.title = ttk.Label(self, text="PNAD Contínua", font=("", 30), anchor="center")
        self.title.grid(row=0, column=0, pady=60, sticky="ew")

        self.microdados_btn = ttk.Button(
            self,
            text="MICRODADOS",
            command=lambda: root.show_frame(root.microdata_frame),
            width=self.btns_width
        )
        self.microdados_btn.grid(row=1, column=0, pady=(5, 0), sticky="ns")

        self.aggregations_btn = ttk.Button(
            self,
            text="BAIXAR AGREGAÇÕES",
            command=lambda: root.show_frame(root.aggregations_frame),
            width=self.btns_width
        )
        self.aggregations_btn.grid(row=2, column=0, pady=(5, 0), sticky="ns")

        self.variables_btn = ttk.Button(
            self,
            text="DESCRIÇÃO DE VARIÁVEIS",
            command=lambda: root.show_frame(root.variables_frame),
            width=self.btns_width
        )
        self.variables_btn.grid(row=3, column=0, pady=(5, 0), sticky="ns")

        self.tutorial_btn = ttk.Button(
            self,
            text="TUTORIAL",
            command=lambda: root.show_frame(root.tutorial_frame),
            width=self.btns_width
        )
        self.tutorial_btn.grid(row=4, column=0, pady=(5, 0), sticky="ns")


class BaseFrame(ttk.Frame):
    def __init__(self, root, title):
        super().__init__(root)

        self.root = root

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(1, weight=1)

        # Header
        self.header_frame = ttk.Frame(self)
        self.header_frame.grid(row=0, column=0, sticky="nsew")
        self.header_frame.grid_columnconfigure(0, weight=1)
        self.title = ttk.Label(self.header_frame, text=title, font=("", 16), anchor="center")
        self.title.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.back_btn = ttk.Button(
            self.header_frame,
            command=lambda: root.show_frame(root.home_frame),
            text="Voltar"
        )
        self.back_btn.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Main content
        self.main_frame = ttk.Frame(self)
        self.main_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
    
    def checkboxes_box(
            self, selections, vars=None, vars_desc=None, sel_label=None,
            sel_all_btn=True, sel_all=False, fixed_selections=[], show_codes=True
        ):
        box = ttk.Frame(self)
        box.place(relwidth=1, relheight=1)

        window_width = self.winfo_width()
        window_height = self.winfo_height()

        selection_height = window_height - 50

        selection_area = ttk.Frame(box, height=selection_height)
        selection_area.pack(side=tk.TOP, fill=tk.X)
        canvas = tk.Canvas(selection_area, highlightthickness=0, height=selection_height)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(selection_area, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        canvas.configure(yscrollcommand=scrollbar.set)

        second_frame = ttk.Frame(canvas, width=window_width)
        second_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=second_frame, anchor="nw")

        checkboxes = []

        btns_area = ttk.Frame(box)
        btns_area.pack(side=tk.BOTTOM, padx=10, pady=(0, 15))
        save_btn = ttk.Button(btns_area, text="Cancelar", command=lambda: box.destroy())
        save_btn.pack(side=tk.LEFT, padx=2)
        cancel_btn = ttk.Button(btns_area, text="Salvar", command=lambda: self.box_save_btn(box, selections, checkboxes, sel_label))
        cancel_btn.pack(side=tk.LEFT, padx=2)

        if sel_all_btn:
            # Select All Checkbox
            sel_all_cb = ttk.Checkbutton(second_frame, text="Selecionar Tudo")
            sel_all_cb.pack(side=tk.TOP, padx=5, pady=(5, 0), anchor="nw")
            sel_all_cb.configure(command=lambda: self.box_select_all(sel_all_cb, checkboxes, fixed_selections))
            sel_all_cb.state(["!alternate"])

        # Variable Checkboxes
        vars_selection = selections if not vars else {
            k: v for k, v in selections.items() if k in vars
        }
        for var, checked in vars_selection.items():
            text = wrap_string(get_var_desc(vars_desc, var, show_var=show_codes) if vars_desc else var, 50)
            cb = ttk.Checkbutton(second_frame, text=text)
            cb.variable = var
            cb.pack(side=tk.TOP, padx=5, pady=(5, 0), anchor="nw")
            checkboxes.append(cb)
            cb.invoke() if checked == 1 else cb.state(["!alternate"])
            if var in fixed_selections:
                cb.config(state="disabled")
            self.root.update_idletasks()

        if sel_all_btn and sel_all:
            sel_all_cb.invoke()

    def box_save_btn(self, box, selections, checkboxes, sel_label=None):
        for cb in checkboxes:
            selections[cb.variable] = 1 if "selected" in cb.state() else 0
        if sel_label:
            checked = [k for k, v in selections.items() if v == 1]
            text = f"Seleção: {len(checked)}"
            sel_label.configure(text=text)
        box.destroy()
    
    def box_select_all(self, select_all_checkbox, checkboxes, fixed_selections):
        if "selected" in select_all_checkbox.state():
            for cb in checkboxes:
                if cb.variable in fixed_selections:
                    continue
                if "selected" not in cb.state():
                    cb.invoke()
        else:
            for cb in checkboxes:
                if cb.variable in fixed_selections:
                    continue
                if "selected" in cb.state():
                    cb.invoke()
    
    def box_create_sel_dict(self, vars):
        return {v: 0 for v in vars}
        
    def items_box(self, items, items_desc=None, show_var=True):
        box = ttk.Frame(self)
        box.place(relwidth=1, relheight=1)
        window_width = self.winfo_width()
        window_height = self.winfo_height()
        selection_height = window_height - 50
        items_area = ttk.Frame(box, height=selection_height)
        items_area.pack(side=tk.TOP, fill=tk.X)
        canvas = tk.Canvas(items_area, highlightthickness=0, height=selection_height)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(items_area, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=scrollbar.set)
        second_frame = ttk.Frame(canvas, width=window_width)
        second_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=second_frame, anchor="nw")
        btn_area = ttk.Frame(box)
        btn_area.pack(side=tk.BOTTOM, padx=10, pady=(0, 15))
        back_btn = ttk.Button(btn_area, text="Voltar", command=lambda: box.destroy())
        back_btn.pack(side=tk.TOP, padx=2)
        for item in items:
            text = wrap_string(get_var_desc(items_desc, item, show_var) if items_desc else item, 50)
            item_label = ttk.Label(second_frame, text=text)
            item_label.pack(side=tk.TOP, anchor="nw", padx=5, pady=(5, 0))
            self.root.update_idletasks()
    
    def get_downloaded_data(self):
        downloaded_data = None
        with open(DOWNLOADED_DATA_PATH) as f:
            downloaded_data = json.load(f)
        return downloaded_data


class MicrodataFrame(BaseFrame):
    def __init__(self, root):
        super().__init__(root, "MICRODADOS")

        self.btns_height = 40

        self.vars_selection = self.box_create_sel_dict(ALL_GROUP)
        self.fixed_vars = ["Ano", "Trimestre", "UF", "V1028"]
        for v in self.fixed_vars:
            self.vars_selection[v] = 1

        self.quarters_selection = {}

        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=0)
        self.main_frame.grid_rowconfigure(1, weight=1)

        # Download Section
        self.download_frame = ttk.Frame(self.main_frame, relief="solid")
        self.download_frame.grid(row=0, column=0, sticky='nsew')
        self.download_frame.grid_columnconfigure(0, weight=1)
        self.download_frame.grid_rowconfigure(0, weight=0)

        # Select Variables
        self.sel_vars_label = ttk.Label(self.download_frame, text="Selecionar Variáveis")        
        self.sel_vars_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.sel_vars_btns_container = ttk.Frame(self.download_frame)
        self.sel_vars_btns_container.grid(row=1, column=0, padx=5, sticky="nsew")
        self.sel_vars_btns_container.grid_rowconfigure(0, weight=1)
        self.sel_vars_btns_container.grid_columnconfigure(0, weight=1)
        self.sel_vars_btns_container.grid_columnconfigure(1, weight=1)
        self.sel_vars_btns_container.grid_columnconfigure(2, weight=1)
        self.sel_vars_btns_container.grid_columnconfigure(3, weight=1)
        self.sel_vars_custom_btn = ttk.Button(
            self.sel_vars_btns_container,
            text="Tudo",
            command=lambda: self.checkboxes_box(
                self.vars_selection, vars_desc=VARIABLES_DESCRIPTION,
                sel_label=self.selected_vars_label, fixed_selections=self.fixed_vars
            )
        )
        self.sel_vars_custom_btn.grid(row=0, column=0, sticky="nsew")
        self.sel_vars_main_btn = ttk.Button(
            self.sel_vars_btns_container,
            text="Principais",
            command=lambda: self.checkboxes_box(
                self.vars_selection, MAIN_GROUP, VARIABLES_DESCRIPTION,
                sel_label=self.selected_vars_label,  fixed_selections=self.fixed_vars
            )
        )
        self.sel_vars_main_btn.grid(row=0, column=1, padx=5, sticky="nsew")
        self.sel_vars_work_btn = ttk.Button(
            self.sel_vars_btns_container,
            text="Trabalho",
            command=lambda: self.checkboxes_box(
                self.vars_selection, WORK_GROUP, VARIABLES_DESCRIPTION,
                sel_label=self.selected_vars_label, fixed_selections=self.fixed_vars
            )
        )
        self.sel_vars_work_btn.grid(row=0, column=2, sticky="nsew")
        self.sel_vars_education_btn = ttk.Button(
            self.sel_vars_btns_container,
            text="Educação",
            command=lambda: self.checkboxes_box(
                self.vars_selection, EDUCATION_GROUP, VARIABLES_DESCRIPTION,
                sel_label=self.selected_vars_label, fixed_selections=self.fixed_vars
            )
        )
        self.sel_vars_education_btn.grid(row=0, column=3, padx=(5, 0), sticky="nsew")
        
        self.selected_vars_label = ttk.Label(self.download_frame, text="Seleção: 4", wraplength=root.window_size-30)
        self.selected_vars_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.sel_quarters_label = ttk.Label(self.download_frame, text="Selecionar Trimestres")
        self.sel_quarters_label.grid(row=3, column=0, padx=5, pady=(20, 5), sticky="w")
        self.sel_quarters_custom_btn = ttk.Button(self.download_frame, text="Tudo", command=self.select_quarters)
        self.sel_quarters_custom_btn.grid(row=4, column=0, padx=5, sticky="nsew")
        self.selected_quarters_label = ttk.Label(self.download_frame, text="Seleção: 0", wraplength=root.window_size-30)
        self.selected_quarters_label.grid(row=5, column=0, padx=5, pady=5, sticky="w")

        self.progress_frame = ttk.Frame(self.download_frame)
        self.progress_frame.grid(row=6, column=0, padx=5, pady=(20, 0))
        self.progress_bar = None
        self.progress_complete_label = ttk.Label(self.progress_frame, text="", anchor="center")
        self.progress_complete_label.grid(row=0, column=0)

        self.download_btn = ttk.Button(self.download_frame, text="Baixar", command=self.start_download)
        self.download_btn.grid(row=7, column=0, padx=5, pady=5, sticky="s")

        ## Downloaded Section
        self.downloaded_frame = ttk.Frame(self.main_frame, relief="solid")
        self.downloaded_frame.grid(row=1, column=0, pady=(10, 0), sticky='nsew')
        self.downloaded_frame.grid_columnconfigure(0, weight=1)
        self.downloaded_frame.grid_rowconfigure(0, weight=0)
        self.downloaded_frame.grid_rowconfigure(1, weight=0)
        self.downloaded_frame.grid_rowconfigure(2, weight=1)

        self.downloaded_vars_label = ttk.Label(self.downloaded_frame, text="Dados Baixados")
        self.downloaded_vars_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.downloaded_btns_container = ttk.Frame(self.downloaded_frame)
        self.downloaded_btns_container.grid(row=1, column=0, padx=5, sticky="nsew")
        self.downloaded_btns_container.grid_rowconfigure(0, weight=1)
        self.downloaded_btns_container.grid_columnconfigure(0, weight=1)
        self.downloaded_btns_container.grid_columnconfigure(1, weight=1)

        self.downloaded_vars_btn = ttk.Button(
            self.downloaded_btns_container,
            text="Variáveis",
            command=lambda: self.items_box(
                self.get_downloaded_data()["variables"],
                items_desc=VARIABLES_DESCRIPTION
            )
        )
        self.downloaded_vars_btn.grid(row=0, column=0, sticky="nsew")
        self.downloaded_quarters_btn = ttk.Button(
            self.downloaded_btns_container,
            text="Trimestres",
            command=lambda: self.items_box(self.get_downloaded_data()["quarters"])
        )
        self.downloaded_quarters_btn.grid(row=0, column=1, padx=(5, 0), sticky="nsew")

        self.memory_use = ttk.Label(self.downloaded_frame, text="Uso de Armazenamento: 0 MB", anchor="w")
        self.memory_use.grid(row=2, column=0, padx=5, pady=(5, 0), sticky="w")
        self.update_memory_use()

        self.del_data_btn = ttk.Button(self.downloaded_frame, text="Apagar", command=lambda: self.del_data(confirm_message=True))
        self.del_data_btn.grid(row=4, column=0, padx=5, pady=5)
    
    def start_download(self):
        try:
            threading.Thread(target=self.download, daemon=True).start()
        except:
            messagebox.showwarning("Erro", "Erro ao baixar microdados")

    def download(self):
        selected_vars = [k for k, v in self.vars_selection.items() if v == 1]
        selected_quarters = [k for k, v in self.quarters_selection.items() if v == 1]

        text = ""
        if len(selected_vars) == 0:
            text += "Selecione variáveis\n"
        if len(selected_quarters) == 0:
            text += "Selecione trimestres"
        if text:
            messagebox.showwarning("Campos obrigatórios", text)
            return

        downloaded_data = self.get_downloaded_data()
        downloaded_vars = downloaded_data["variables"]
        if len(downloaded_vars) > 0 and set(downloaded_vars) != set(selected_vars):
            response = messagebox.askyesno(
                "Confirmar Seleção",
                "As variáveis selecionadas diferem dos dados já baixados. Deseja confirmar a nova seleção?"
            )
            if response:
                self.del_data()
            else:
                return

        buttons = [
            self.back_btn,
            self.sel_vars_custom_btn, self.sel_vars_main_btn,
            self.sel_vars_work_btn, self.sel_vars_education_btn,
            self.sel_quarters_custom_btn, self.download_btn,
            self.downloaded_vars_btn, self.downloaded_quarters_btn,
            self.del_data_btn
        ]
        for btn in buttons:
            btn.config(state="disabled")

        self.progress_complete_label.config(text="")

        progress_bar = ttk.Progressbar(self.progress_frame, orient="horizontal", length=200, mode="determinate")
        progress_bar.grid(row=0, column=0)

        quarter_data_urls = get_quarter_data_urls()
        filtered_urls = [url for url in quarter_data_urls if f"{url[134:138]}/{url[132:134]}" in selected_quarters]
        progress_bar["maximum"] = len(filtered_urls)

        self.update_idletasks()

        for i, url in enumerate(filtered_urls):
            download_data(url, variables=selected_vars)
            downloaded_data = self.get_downloaded_data()
            quarter = f"{url[134:138]}/{url[132:134]}"  # YYYY/QQ
            if quarter not in downloaded_data["quarters"]:
                downloaded_data["quarters"].append(quarter)
                downloaded_data["quarters"].sort()
            downloaded_data["variables"] = selected_vars
            self.save_downloaded_data(downloaded_data)
            progress_bar["value"] = i + 1
            self.update_memory_use()
            self.update_idletasks()
    
        progress_bar.destroy()
        self.progress_complete_label.config(text="Dados Baixados!")

        for btn in buttons:
            btn.update_idletasks()
            btn.config(state="normal")

    def select_quarters(self):
        try:
            quarter_data_urls = get_quarter_data_urls()
        except:
            messagebox.showwarning("Erro", "Erro ao carregar lista de trimestres (verifique sua conexão com a internet)")
            return
        updated_quarters = [f"{url[134:138]}/{url[132:134]}" for url in quarter_data_urls]
        updated_quarters = self.box_create_sel_dict(updated_quarters)
        if not self.quarters_selection:
            self.quarters_selection = updated_quarters
        else:
            self.quarters_selection = updated_quarters | self.quarters_selection
        self.checkboxes_box(self.quarters_selection, sel_label=self.selected_quarters_label)
    
    def save_downloaded_data(self, data):
        downloaded_data_path_temp = DOWNLOADED_DATA_PATH + ".temp"
        with open(downloaded_data_path_temp, "w") as f:
            json.dump(data, f)   
        os.replace(downloaded_data_path_temp, DOWNLOADED_DATA_PATH)  

    def del_data(self, confirm_message=False):
        if confirm_message:
            response = messagebox.askyesno(
                "Apagar dados",
                "Tem certeza de que deseja apagar todos os dados baixados?"
            )
            if not response:
                return
        if os.path.exists(DATA_FOLDER_PATH):
            shutil.rmtree(DATA_FOLDER_PATH)
        if os.path.exists(TEMP_FOLDER_PATH):
            shutil.rmtree(TEMP_FOLDER_PATH)
        self.save_downloaded_data({"variables": [], "quarters": []})
        self.update_memory_use()
        self.update_idletasks()

    def update_memory_use(self):
        total_size = 0
        for dirpath, _, filenames in os.walk(DATA_FOLDER_PATH):
            for file in filenames:
                file_path = os.path.join(dirpath, file)
                if os.path.isfile(file_path):
                    total_size += os.path.getsize(file_path)
        size_in_mb = total_size / (1024 ** 2)
        memory_use = None
        if size_in_mb >= 1024:
            size_in_gb = size_in_mb / 1024
            memory_use = f"{size_in_gb:.2f} GB"
        else:
            memory_use = f"{size_in_mb:.2f} MB"
        self.memory_use.configure(text=f"Uso de Armazenamento: {memory_use}")


class AggregationsFrame(BaseFrame):
    def __init__(self, root):
        super().__init__(root, "BAIXAR AGREGAÇÕES")
        self.cat_filters = []
        self.cat_filter_elements = []
        self.num_filters = []
        self.num_filter_elements = []

        self.groups_selection = {}

        self.include_count = True
        self.include_count_element = None
        self.total_ops = []
        self.total_ops_elements = []

        self.main_frame.configure(relief='solid')
        self.main_frame.grid_rowconfigure(9, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.filter_label = ttk.Label(self.main_frame, text="Filtros")
        self.filter_label.grid(row=0, column=0, padx=50, pady=(40, 5), sticky="w")
        self.filter_btn = ttk.Button(self.main_frame, text="Selecionar", command=self.filters_box)
        self.filter_btn.grid(row=1, column=0, padx=50, sticky="nsew")
        self.filter_btn.config(padding=(10, 5))
        self.sel_filters_label = ttk.Label(self.main_frame, text="Seleção: 0")
        self.sel_filters_label.grid(row=2, column=0, padx=50, pady=5, sticky="w")

        self.group_by_label = ttk.Label(self.main_frame, text="Agrupar Por")
        self.group_by_label.grid(row=3, column=0, padx=50, pady=(25, 5), sticky="w")
        self.group_by_btn = ttk.Button(
            self.main_frame,
            text="Selecionar",
            command=lambda: self.checkboxes_box(
                self.groups_selection, vars_desc=VARIABLES_DESCRIPTION,
                sel_label=self.sel_groups_label, sel_all_btn=False
            )
        )
        self.group_by_btn.config(padding=(10, 5))
        self.group_by_btn.grid(row=4, column=0, padx=50, sticky="nsew")
        self.sel_groups_label = ttk.Label(self.main_frame)
        self.sel_groups_label.grid(row=5, column=0, padx=50, pady=5, sticky="w")

        self.totals_label = ttk.Label(self.main_frame, text="Totais")
        self.totals_label.grid(row=6, column=0, padx=50, pady=(25, 5), sticky="w")
        self.totals_btn = ttk.Button(self.main_frame, text="Selecionar", command=self.totals_box)
        self.totals_btn.grid(row=7, column=0, padx=50, sticky="nsew")
        self.totals_btn.config(padding=(10, 5))
        self.sel_totals_label = ttk.Label(self.main_frame, text="Seleção: 1")
        self.sel_totals_label.grid(row=8, column=0, padx=50, pady=5, sticky="w")

        self.download_btn = ttk.Button(self.main_frame, text="Baixar", command=self.download_csv)
        self.download_btn.grid(row=10, padx=10, pady=(0, 5), column=0, sticky="s")

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        downloaded_data = self.get_downloaded_data()
        self.downloaded_cat = [v for v in downloaded_data["variables"] if v not in NUMERICAL_GROUP and v != "V1028"]
        self.downloaded_num = [v for v in downloaded_data["variables"] if v in NUMERICAL_GROUP]
        if "Ano" in self.downloaded_num and "Trimestre" in self.downloaded_num:
            self.groups_selection = self.box_create_sel_dict(["Ano", "Trimestre"] + self.downloaded_cat)
            self.groups_selection["Ano"] = 1
            self.groups_selection["Trimestre"] = 1
            self.sel_groups_label.configure(text="Seleção: 2")
        else:
            self.groups_selection = {}
            self.sel_groups_label.configure(text="Seleção: 0")

    def filters_box(self):
        def create_filter():
            tab_index = tabs_area.index("current")
            if tab_index == 0:
                create_cat_filter()
            else:
                create_num_filter()

        def create_cat_filter(var=None, values=None):
            filter = ttk.Frame(canvas_frame_cat)
            filter.values = values
            filter.pack(pady=10)
            labels_container = ttk.Frame(filter)
            labels_container.pack(side=tk.LEFT, padx=2)
            var_label = ttk.Label(labels_container, text="Variável")
            var_label.pack(anchor="w")
            val_label = ttk.Label(labels_container, text="Valores")
            val_label.pack(pady=(4, 0), anchor="w")
            sel_container = ttk.Frame(filter)
            sel_container.pack(side=tk.LEFT)
            var_sel = ttk.Combobox(sel_container, values=self.downloaded_cat, state="readonly")
            var_sel.bind("<<ComboboxSelected>>", lambda e: change_cat_sel(filter))
            var_sel.set(var or "Selecionar")
            filter.variable = var_sel
            var_sel.pack()
            val_sel = ttk.Button(sel_container, text="Selecionar", command=lambda: sel_cat_filter_values(filter))
            val_sel.pack(pady=(4, 0), fill=tk.X, expand=True)
            delete_filter_btn = ttk.Button(filter, text="X", width=1, command=lambda: delete_cat_filter(filter))
            delete_filter_btn.pack(side=tk.LEFT, padx=5, fill=tk.Y, expand=True)

            self.cat_filter_elements.append(filter)

        def change_cat_sel(filter):
            filter.values = None

        def sel_cat_filter_values(filter):
            sel_all = not bool(filter.values)
            variable = filter.variable.get()
            if variable == "Selecionar":
                return
            mapping = VARIABLES_MAPPING[variable]
            filter.values = filter.values or self.box_create_sel_dict(mapping.keys())
            self.checkboxes_box(filter.values, vars_desc=mapping, sel_all=sel_all, show_codes=False)
            
        def delete_num_filter(filter):
            self.num_filter_elements = [f for f in self.num_filter_elements if f != filter]
            filter.destroy()

        def delete_cat_filter(filter):
            self.cat_filter_elements = [f for f in self.cat_filter_elements if f != filter]
            filter.destroy()

        def save_filters():
            cat_filters = []
            for cat_filter in self.cat_filter_elements:
                variable = cat_filter.variable.get()
                if variable == "Selecionar":
                    messagebox.showwarning("Erro", "Filtro inválido (Variáveis categóricas)")
                    return
                cat_filters.append({
                    "variable": variable,
                    "values": cat_filter.values
                })
            if has_duplicates(cat_filters):
                messagebox.showwarning("Erro", "Filtro repetido (Variáveis categóricas)")
                return

            num_filters = []
            for num_filter in self.num_filter_elements:
                variable = num_filter.variable.get()
                operation = num_filter.operation.get()
                value = num_filter.value.get()
                if variable == "Selecionar" or operation == "Selecionar" or not is_numeric(value):
                    messagebox.showwarning("Erro", "Filtro inválido (Variáveis numéricas)")
                    return
                num_filters.append({
                    "variable": variable,
                    "operation": operation,
                    "value": value
                })
            if has_duplicates(num_filters):
                messagebox.showwarning("Erro", "Filtro repetido (Variáveis numéricas)")
                return

            self.cat_filters = cat_filters
            self.cat_filter_elements = []
            self.num_filters = num_filters
            self.num_filter_elements = []
            label_text = f"Seleção: {len(cat_filters)+len(num_filters)}"
            self.sel_filters_label.configure(text=label_text)
            box.destroy()

        def create_num_filter(var=None, op=None, val=None):
            filter = ttk.Frame(canvas_frame_num)
            filter.pack(pady=10)
            labels_container = ttk.Frame(filter)
            labels_container.pack(side=tk.LEFT, padx=2)
            var_label = ttk.Label(labels_container, text="Variável")
            var_label.pack(anchor="w")
            op_label = ttk.Label(labels_container, text="Operação")
            op_label.pack(pady=(2, 0), anchor="w")
            val_label = ttk.Label(labels_container, text="Valor")
            val_label.pack(pady=(2, 0), anchor="w")
            sel_container = ttk.Frame(filter)
            sel_container.pack(side=tk.LEFT)
            var_sel = ttk.Combobox(sel_container, values=self.downloaded_num, state="readonly")
            filter.variable = var_sel
            var_sel.set(var or "Selecionar")
            var_sel.pack()
            op_sel = ttk.Combobox(sel_container, values=["Igual a", "Maior que", "Menor que", "Maior ou igual a", "Menor ou igual a"], state="readonly")
            filter.operation = op_sel
            op_sel.set(op or "Selecionar")
            op_sel.pack(pady=(2, 0))
            val_sel = ttk.Entry(sel_container)
            filter.value = val_sel
            val_sel.insert(0, val or 0.0)
            val_sel.pack(pady=(2, 0), anchor="w")
            delete_filter_btn = ttk.Button(filter, text="X", width=1, command=lambda: delete_num_filter(filter))
            delete_filter_btn.pack(side=tk.LEFT, padx=5, fill=tk.Y, expand=True)
            self.num_filter_elements.append(filter)

        box = ttk.Frame(self)
        box.place(relwidth=1, relheight=1)
        ## Buttons
        btns_area = ttk.Frame(box)
        btns_area.pack(side=tk.BOTTOM, padx=10, pady=(5, 15))
        back_btn = ttk.Button(btns_area, text="Voltar", command=save_filters)
        back_btn.pack(side=tk.LEFT, padx=2)
        add_btn = ttk.Button(btns_area, text="Adicionar", command=create_filter)
        add_btn.pack(side=tk.LEFT, padx=2)
        ## Tabs
        tabs_area = ttk.Notebook(box)
        tabs_area.pack(expand=True, fill=tk.BOTH)
        cat_tab = ttk.Frame(tabs_area)
        tabs_area.add(cat_tab, text="Variáveis categóricas")
        canvas_cat = tk.Canvas(cat_tab, highlightthickness=0)
        canvas_cat.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_cat = ttk.Scrollbar(cat_tab, orient=tk.VERTICAL, command=canvas_cat.yview)
        scrollbar_cat.pack(side=tk.RIGHT, fill=tk.Y)
        canvas_cat.configure(yscrollcommand=scrollbar_cat.set)
        canvas_frame_cat = ttk.Frame(canvas_cat)
        canvas_frame_cat.bind('<Configure>', lambda e: canvas_cat.configure(scrollregion=canvas_cat.bbox("all")))
        canvas_cat.create_window((self.winfo_width()//2,0), window=canvas_frame_cat, anchor="n")
        num_tab = ttk.Frame(tabs_area)
        tabs_area.add(num_tab, text="Variáveis numéricas")
        canvas_num = tk.Canvas(num_tab, highlightthickness=0)
        canvas_num.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_num = ttk.Scrollbar(num_tab, orient=tk.VERTICAL, command=canvas_num.yview)
        scrollbar_num.pack(side=tk.RIGHT, fill=tk.Y)
        canvas_num.configure(yscrollcommand=scrollbar_num.set)
        canvas_frame_num = ttk.Frame(canvas_num)
        canvas_frame_num.bind('<Configure>', lambda e: canvas_num.configure(scrollregion=canvas_num.bbox("all")))
        canvas_num.create_window((self.winfo_width()//2,0), window=canvas_frame_num, anchor="n")
        for num_filter in self.num_filters:
            create_num_filter(
                num_filter["variable"],
                num_filter["operation"],
                num_filter["value"]
            )
        for cat_filter in self.cat_filters:
            create_cat_filter(
                cat_filter["variable"],
                cat_filter["values"]
            )

    def totals_box(self):
        def create_cnt_total(include_count):
            cnt_total = ttk.Frame(canvas_frame_cnt)
            cnt_total.pack()
            cnt_labels_container = ttk.Frame(cnt_total)
            cnt_labels_container.pack(pady=(10, 0), side=tk.LEFT, anchor="n")
            cnt_label = ttk.Label(cnt_labels_container, text="Quantidade de Pessoas")
            cnt_label.pack(anchor="w")
            sel_container = ttk.Frame(cnt_total)
            sel_container.pack(padx=(4, 0), pady=(10, 0), side=tk.LEFT, anchor="n")
            cnt_total_sel = ttk.Combobox(sel_container, values=["Incluir", "Não incluir"], state="readonly")
            cnt_total_sel.set("Incluir" if include_count else "Não incluir")
            cnt_total.include = cnt_total_sel
            cnt_total_sel.pack()
            self.include_count_element = cnt_total

        def create_op_total(variable=None, operation=None, deflator=None):
            op_total = ttk.Frame(canvas_frame_ops)
            op_total.pack(side=tk.TOP, pady=10)
            op_container = ttk.Frame(op_total)
            op_container.pack(side=tk.TOP)
            op_labels_container = ttk.Frame(op_container)
            op_labels_container.pack(side=tk.LEFT, anchor="n")
            op_var_label = ttk.Label(op_labels_container, text="Variável")
            op_var_label.pack(anchor="w")
            op_label = ttk.Label(op_labels_container, text="Operação")
            op_label.pack(pady=(4, 0), anchor="w")
            sel_container = ttk.Frame(op_container)
            sel_container.pack(padx=(4, 0), side=tk.LEFT, anchor="n")
            op_var_sel = ttk.Combobox(sel_container, values=[v for v in self.downloaded_num if v not in ["Ano", "Trimestre"]], state="readonly")
            op_total.variable = op_var_sel
            op_var_sel.set(variable or "Selecionar")
            op_var_sel.pack()
            op_operation_sel = ttk.Combobox(sel_container, values=["Soma", "Média"], state="readonly")
            op_total.operation = op_operation_sel
            op_operation_sel.set(operation or "Selecionar")
            op_operation_sel.pack(pady=(2, 0))
            delete_op_total_btn = ttk.Button(op_container, text="X", width=1, command=lambda: delete_op_total(op_total))
            delete_op_total_btn.pack(side=tk.LEFT, padx=5, fill=tk.Y, expand=True)
            def_cb = ttk.Checkbutton(op_total, text="Deflacionar valores")
            op_total.deflator = def_cb
            def_cb.invoke() if deflator else def_cb.state(["!alternate"])
            if variable in DEFLATOR_GROUP:
                op_total.deflator.pack(side=tk.TOP, pady=(4, 0), anchor="w")
            op_var_sel.bind("<<ComboboxSelected>>", lambda e: def_cb_manager(op_total))
            self.total_ops_elements.append(op_total)

        def delete_op_total(op_total):
            self.total_ops_elements = [t for t in self.total_ops_elements if t != op_total]
            op_total.destroy()
    
        def def_cb_manager(ops_total):
            if ops_total.variable.get() in DEFLATOR_GROUP:
                ops_total.deflator.pack(side=tk.TOP, pady=(4, 0), anchor="w")
            else:
                ops_total.deflator.pack_forget()
                if "selected" in ops_total.deflator.state():
                    ops_total.deflator.invoke()

        def add_btn_manager():
            if tabs_area.index("current") == 0:
                add_btn.pack_forget()
            else:
                add_btn.pack()

        def save_totals():
            self.include_count = self.include_count_element.include.get() == "Incluir"
            total_ops = []
            for total_op in self.total_ops_elements:
                variable = total_op.variable.get()
                operation = total_op.operation.get()
                if variable == "Selecionar" or operation == "Selecionar":
                    messagebox.showwarning("Erro", "Total inválido (Soma e Média)")
                    return
                total_ops.append({
                    "variable": total_op.variable.get(),
                    "operation": total_op.operation.get(),
                    "deflator": "selected" in total_op.deflator.state()
                })
            if not self.include_count and len(total_ops) == 0:
                messagebox.showwarning("Erro", "Necessário selecionar pelo menos um total")
                return
            if has_duplicates(total_ops):
                messagebox.showwarning("Erro", "Total repetido (Soma e Média)")
                return
            self.include_count_element = None
            self.total_ops_elements = []
            self.total_ops = total_ops
            
            label_text = f"Seleção: {len(total_ops) + (1 if self.include_count else 0)}"
            self.sel_totals_label.configure(text=label_text)
            box.destroy()

        box = ttk.Frame(self)
        box.place(relwidth=1, relheight=1)

        # Buttons
        btns_area = ttk.Frame(box)
        btns_area.pack(side=tk.BOTTOM, padx=10, pady=(5, 15))
        back_btn = ttk.Button(btns_area, text="Voltar", command=save_totals)
        back_btn.pack(side=tk.LEFT, padx=2)
        add_btn = ttk.Button(btns_area, text="Adicionar", command=create_op_total)

        ## Tabs
        tabs_area = ttk.Notebook(box)
        tabs_area.pack(expand=True, fill=tk.BOTH)
        tabs_area.bind("<<NotebookTabChanged>>", lambda e: add_btn_manager())

        cnt_tab = ttk.Frame(tabs_area)
        tabs_area.add(cnt_tab, text="Contagem")
        canvas_cnt = tk.Canvas(cnt_tab, highlightthickness=0)
        canvas_cnt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_cnt = ttk.Scrollbar(cnt_tab, orient=tk.VERTICAL, command=canvas_cnt.yview)
        scrollbar_cnt.pack(side=tk.RIGHT, fill=tk.Y)
        canvas_cnt.configure(yscrollcommand=scrollbar_cnt.set)
        canvas_frame_cnt = ttk.Frame(canvas_cnt)
        canvas_frame_cnt.bind('<Configure>', lambda e: canvas_cnt.configure(scrollregion=canvas_cnt.bbox("all")))
        canvas_cnt.create_window((self.winfo_width()//2,0), window=canvas_frame_cnt, anchor="n")
        create_cnt_total(self.include_count)

        ops_tab = ttk.Frame(tabs_area)
        tabs_area.add(ops_tab, text="Soma e Média")
        canvas_ops = tk.Canvas(ops_tab, highlightthickness=0)
        canvas_ops.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_ops = ttk.Scrollbar(ops_tab, orient=tk.VERTICAL, command=canvas_ops.yview)
        scrollbar_ops.pack(side=tk.RIGHT, fill=tk.Y)
        canvas_ops.configure(yscrollcommand=scrollbar_ops.set)
        canvas_frame_ops = ttk.Frame(canvas_ops)
        canvas_frame_ops.bind('<Configure>', lambda e: canvas_ops.configure(scrollregion=canvas_ops.bbox("all")))
        canvas_ops.create_window((self.winfo_width()//2,0), window=canvas_frame_ops, anchor="n")
        
        for total_op in self.total_ops:
            create_op_total(total_op["variable"], total_op["operation"], total_op["deflator"])

    def download_csv(self):
        group_cols = get_vars_from_bin_dict(self.groups_selection)
        if len(group_cols) == 0:
            messagebox.showwarning("Erro", "Necessário agrupar por pelo menos uma variável")
            return

        data = load_data()
        for cat_filter in self.cat_filters:
            data = filter_cat_column(
                data,
                cat_filter["variable"],
                get_vars_from_bin_dict(cat_filter["values"])
            )
        for num_filter in self.num_filters:
            data = filter_num_column(
                data,
                num_filter["variable"],
                num_filter["operation"],
                float(num_filter["value"])
            )

        agg_list = []
        deflator_data = None
        for total in self.total_ops:
            if total["deflator"] and deflator_data is None:
                try:
                    deflator_data = get_deflator()
                except:
                    messagebox.showwarning("Erro", "Erro ao baixar deflator (verifique sua conexão com a internet)")
                    return
            agg_list.append(
                [total["variable"], total["operation"], total["deflator"]]
            )
        result = calculate_totals(data, group_cols, agg_list, self.include_count, deflator_data)
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            result.write_csv(file_path)


class VariablesFrame(BaseFrame):
    def __init__(self, root):
        super().__init__(root, "DESCRIÇÃO DE VARIÁVEIS")
        self.box = ttk.Frame(self.main_frame)
        self.box.place(relwidth=1, relheight=1)
        self.box.configure(relief="solid")
        self.back_btn.configure(command=self.close)

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        self.start_render()

    def start_render(self):
        threading.Thread(target=self.render, daemon=True).start()

    def render(self):
        items_area = ttk.Frame(self.box)
        items_area.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=1, pady=1)
        canvas = tk.Canvas(items_area, highlightthickness=0)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(items_area, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=scrollbar.set)
        second_frame = ttk.Frame(canvas)
        second_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=second_frame, anchor="nw")
        for item in ALL_GROUP:
            text = wrap_string(get_var_desc(VARIABLES_DESCRIPTION, item), 50)
            item_label = ttk.Label(second_frame, text=text)
            item_label.pack(side=tk.TOP, anchor="nw", padx=5, pady=(5, 0))
            self.root.update_idletasks()

    def close(self):
        for child in self.box.winfo_children():
            child.destroy()
        self.root.show_frame(self.root.home_frame)


class TutorialFrame(BaseFrame):
    def __init__(self, root):
        super().__init__(root, "TUTORIAL")

        self.main_frame.configure(relief='solid')
        self.tutorial_url = TUTORIAL_URL

        self.label = ttk.Label(self.main_frame, text="Tutorial disponível no endereço:")
        self.label.pack(padx=5, pady=5, anchor="w")

        self.url = tk.Text(self.main_frame, height=1, width=54)
        self.url.insert(tk.END, self.tutorial_url)
        self.url.tag_configure("center", justify="center")
        self.url.tag_add("center", "1.0", "end")
        self.url.config(state=tk.DISABLED)
        self.url.pack(pady=(20, 0))

        self.copy_btn = ttk.Button(self.main_frame, text="Copiar", command=self.copy_text)
        self.copy_btn.pack(pady=10)
    
    def copy_text(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.tutorial_url)

