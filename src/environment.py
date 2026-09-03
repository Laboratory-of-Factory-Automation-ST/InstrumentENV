import os

class EnvInit:
    def __init__(self):
        os.add_dll_directory(r"C:\Windows\System32")
        os.environ["PYVISA_LIBRARY"] = r"C:\Windows\System32\visa32.dll"
