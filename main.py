import ctypes
import tkinter as tk
from tkinter import messagebox

# Define the necessary constants and functions from Windows API
kernel32 = ctypes.WinDLL('kernel32')
user32 = ctypes.WinDLL('user32')
EnumProcesses = psapi.EnumProcesses
OpenProcess = kernel32.OpenProcess
VirtualAllocEx = kernel32.VirtualAllocEx
WriteProcessMemory = kernel32.WriteProcessMemory
CreateRemoteThread = kernel32.CreateRemoteThread
CloseHandle = kernel32.CloseHandle
GetWindowTextA = user32.GetWindowTextA
GetWindowThreadProcessId = user32.GetWindowThreadProcessId

# Function to enumerate all processes and retrieve their names
def get_processes():
    process_ids = (ctypes.c_ulong * 1024)()
    cb = ctypes.sizeof(process_ids)
    bytes_returned = ctypes.c_ulong()
    EnumProcesses(ctypes.byref(process_ids), cb, ctypes.byref(bytes_returned))

    count = int(bytes_returned.value / ctypes.sizeof(ctypes.c_ulong()))
    process_list = []
    for i in range(count):
        process_id = process_ids[i]
        process_handle = OpenProcess(0x0400 | 0x0010, False, process_id)
        if process_handle:
            window_text = ctypes.create_string_buffer(255)
            GetWindowTextA(process_handle, window_text, 255)
            process_list.append((process_id, window_text.value))
            CloseHandle(process_handle)

    return process_list

# Function to perform DLL injection
def inject_dll():
    selected_process = process_listbox.get(tk.ACTIVE)
    if selected_process:
        target_process_id = selected_process[0]
        dll_path = dll_entry.get()

        # Open the target process with required permissions
        process_handle = OpenProcess(0x1F0FFF, False, target_process_id)

        # Allocate memory in the target process to store the DLL path
        dll_path_address = VirtualAllocEx(process_handle, 0, len(dll_path), 0x1000, 0x04)

        # Write the DLL path to the allocated memory in the target process
        WriteProcessMemory(process_handle, dll_path_address, dll_path, len(dll_path), 0)

        # Load the DLL into the target process by creating a remote thread
        CreateRemoteThread(process_handle, None, 0, kernel32.LoadLibraryA, dll_path_address, 0, None)

        messagebox.showinfo("DLL Injection", "DLL injected successfully!")
    else:
        messagebox.showwarning("DLL Injection", "No process selected!")

# Create the GUI
root = tk.Tk()
root.title("Evil DLL Injector 😈")

# Processes Listbox
process_listbox = tk.Listbox(root, selectmode=tk.SINGLE)
process_listbox.pack(padx=10, pady=10)

# DLL Entry
dll_frame = tk.Frame(root)
dll_frame.pack(padx=10, pady=(0, 10))

dll_label = tk.Label(dll_frame, text="DLL Path:")
dll_label.pack(side=tk.LEFT)

dll_entry = tk.Entry(dll_frame, width=40)
dll_entry.pack(side=tk.LEFT)

# Inject Button
inject_button = tk.Button(root, text="Inject DLL", command=inject_dll)
inject_button.pack(padx=10, pady=10)

# Refresh process list
process_list = get_processes()
for process in process_list:
    process_listbox.insert(tk.END, process)

root.mainloop()
