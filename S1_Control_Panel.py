import tkinter as tk
from tkinter import messagebox
import subprocess
import threading
import urllib.request
import webbrowser
import socket
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
HOST_SCRIPT = BASE / "iptv_host.py"
PORT = 8000
process = None

def local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "YOUR-PC-IP"

def service_running():
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/api/current", timeout=1.5) as r:
            return r.status == 200
    except Exception:
        return False

def set_status(text, color="#333333"):
    status_var.set(text)
    status_label.config(fg=color)

def start_service():
    global process
    if service_running():
        set_status("Service is already running.", "#167a36")
        return
    if not HOST_SCRIPT.exists():
        messagebox.showerror("Missing file", "iptv_host.py must be in the same folder as this GUI.")
        return
    try:
        # Run host with the same Python interpreter that launched this GUI.
        process = subprocess.Popen(
            [sys.executable, str(HOST_SCRIPT)],
            cwd=str(BASE),
            creationflags=(subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        set_status("Starting S1 service…", "#b36b00")
        root.after(1200, refresh_status)
    except Exception as e:
        messagebox.showerror("Could not start", str(e))
        set_status("Service stopped.", "#a32626")

def stop_service():
    global process
    stopped_own = False
    if process is not None and process.poll() is None:
        try:
            process.terminate()
            process.wait(timeout=4)
            stopped_own = True
        except Exception:
            try:
                process.kill()
                stopped_own = True
            except Exception:
                pass
        process = None
    if stopped_own:
        set_status("Service stopped.", "#a32626")
    elif service_running():
        messagebox.showinfo(
            "Service running elsewhere",
            "The S1 server is running, but it was not started by this control panel. "
            "Close the other Python host window or stop that process first."
        )
    else:
        set_status("Service is already stopped.", "#a32626")

def open_center():
    url = f"http://127.0.0.1:{PORT}/"
    if not service_running():
        if not messagebox.askyesno("Service is stopped", "Start the service now and open Center?"):
            return
        start_service()
        root.after(1800, lambda: webbrowser.open(url))
    else:
        webbrowser.open(url)

def open_tv():
    url = f"http://127.0.0.1:{PORT}/s1"
    if not service_running():
        if not messagebox.askyesno("Service is stopped", "Start the service now and open TV?"):
            return
        start_service()
        root.after(1800, lambda: webbrowser.open(url))
    else:
        webbrowser.open(url)

def refresh_status():
    if service_running():
        set_status(f"Service running  •  Center: http://{local_ip()}:{PORT}/  •  TV: http://{local_ip()}:{PORT}/s1", "#167a36")
    else:
        set_status("Service stopped.", "#a32626")
    root.after(4000, refresh_status)

def on_close():
    # Do not kill the server automatically on GUI close; use Stop Service intentionally.
    root.destroy()

root = tk.Tk()
root.title("S1 IPTV Control Panel")
root.geometry("570x350")
root.resizable(False, False)
root.configure(bg="#f3f5f9")

tk.Label(root, text="S1 IPTV CONTROL PANEL", font=("Segoe UI", 17, "bold"),
         bg="#f3f5f9", fg="#17243d").pack(pady=(22, 5))
tk.Label(root, text="Manage the IPTV host and open either web page",
         font=("Segoe UI", 10), bg="#f3f5f9", fg="#596579").pack(pady=(0, 18))

buttons = tk.Frame(root, bg="#f3f5f9")
buttons.pack(pady=3)

def make_button(parent, text, command, bg, width=17):
    return tk.Button(parent, text=text, command=command, width=width, height=2,
                     font=("Segoe UI", 11, "bold"), bg=bg, fg="white",
                     activebackground=bg, activeforeground="white",
                     relief="flat", cursor="hand2", bd=0)

make_button(buttons, "▶  Start Service", start_service, "#16803c").grid(row=0, column=0, padx=7, pady=7)
make_button(buttons, "■  Stop Service", stop_service, "#b42318").grid(row=0, column=1, padx=7, pady=7)
make_button(buttons, "TV", open_tv, "#1769ff", 17).grid(row=1, column=0, padx=7, pady=7)
make_button(buttons, "Center", open_center, "#5b45b5", 17).grid(row=1, column=1, padx=7, pady=7)

status_var = tk.StringVar(value="Checking service…")
status_label = tk.Label(root, textvariable=status_var, font=("Segoe UI", 9),
                        bg="#f3f5f9", fg="#333333", wraplength=525, justify="center")
status_label.pack(pady=(16, 5))

tk.Label(root, text="Keep iptv_host.py, iptv_sender.html and iptv_client.html in this folder.",
         font=("Segoe UI", 8), bg="#f3f5f9", fg="#6b7280").pack(side="bottom", pady=12)

root.protocol("WM_DELETE_WINDOW", on_close)
refresh_status()
root.mainloop()
