import logging
from src.InstrumentDrivers.InstrumentDiscovery import InstrumentDiscovery
from src.InstrumentDrivers.Instrument import Instrument
from src.InstrumentDrivers.DMM6500 import DMM6500
import ipywidgets as widgets
from IPython.display import display

class GUIController:

    @staticmethod
    def view_inst_select():
        ID = InstrumentDiscovery()
        ID.get_handshakes()
        rcvd = ID.handshakes
        
        gc = GUIContent("inst_select_view")

        select_params = dict(
            options=dict(zip(rcvd.values(), rcvd.keys())),
            value=[list(rcvd.keys())[0]] if len(rcvd) > 0 else [],
            #rows=10,
            description='Available Instruments',
            disabled=False,
            style={'description_width': 'initial'},
            layout={'width': 'initial'}
        )
        
        btn_params = dict(
            description='Click me',
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Click me',
            icon='check' # (FontAwesome names without the `fa-` prefix)
        )

        select = widgets.SelectMultiple(**select_params)
        btn = widgets.Button(**btn_params)
        btn.on_click(gc.display_elements)

        gc.elements = [select, btn]

        gc.display_view()

    @staticmethod
    def measure_va_char(blanking_time):
        pass

class GUIContent(dict):
    __VIEWS = dict()

    def __init__(self, view_name):
        self.__elements: list = GUIContent.new_view(view_name)

    @classmethod
    def new_view(cls, view_name):
        if view_name in cls.__VIEWS:
            logging.info("View with the same name exists, returning existing view.\n")
            return cls.__VIEWS[view_name]
        else:
            cls.__VIEWS[view_name] = list()
            return cls.__VIEWS[view_name]
        
    @property
    def elements(self):
        return self.__elements
    
    @elements.setter
    def elements(self, elements: list[widgets.Widget]):
        self.__elements = elements

    def __setitem__(self, key, value):
        self.__elements[key] = value

    def __getitem__(self, key):
        return self.__elements[key]
    
    def __add__(self, widget: widgets.Widget):
        self.__elements.append(widget)

    def display_view(self):
        
        for element in self.elements:
            display(element)

    def display_viewbox(self):
        display(widgets.Box(self.__elements))

    def display_elements(self, _):
        display(self.__elements)

class GUIHook(type):
    def __new__(cls, name, bases, clsdict):
        for attr_name, attr_value in clsdict.items():
            if callable(attr_value) and attr_name != '__init__':
                clsdict[attr_name] = cls.add_hooks(attr_value)
        return super(GUIHook, cls).__new__(cls, name, bases, clsdict)
    
    @staticmethod
    def add_hooks(func):
        def wrapper(*args, **kwargs):
            # Execute the Before Hook
            if hasattr(func, 'before_hook'):
                func.before_hook(*args, **kwargs)
            
            result = func(*args, **kwargs)
            
            # Execute the After Hook
            if hasattr(func, 'after_hook'):
                func.after_hook(*args, **kwargs)
            return result
        return wrapper
    
    def before(hook_func):
        def decorator(func):
            func.before_hook = hook_func
            return func
        return decorator

    def after(hook_func):
        def decorator(func):
            func.after_hook = hook_func
            return func
        return decorator