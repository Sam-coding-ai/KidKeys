# Copyright (c) 2026 Github: Sam-coding-ai and @kidkeysofficial. All Rights Reserved.
# Unauthorized copying, commercial distribution, or removal of attribution is strictly prohibited.

from pynput import mouse, keyboard
from pynput.keyboard import Controller, Key, KeyCode
from PIL import Image, ImageDraw
import pystray
import winsound
import time
import winreg
import ctypes
import subprocess
import sys
import os
import threading
import webbrowser
import tkinter as tk

# Try importing plyer for native Windows Toast Notifications
try:
    from plyer import notification
except ImportError:
    notification = None

is_locked = False
trigger_tap_count = 0
last_tap_time = 0

current_keyboard_listener = None
current_mouse_listener = None
tray_icon = None

# Controller to inject the hidden Touchpad toggle hotkey
kbd_controller = Controller()

def play_beep_async(freq, duration):
    """Plays audio cues asynchronously to avoid blocking low-level OS hooks."""
    def beep():
        try:
            winsound.Beep(freq, duration)
        except Exception:
            pass
    threading.Thread(target=beep, daemon=True).start()

def get_resource_path(filename):
    """Resolves resource paths for PyInstaller bundles and dev mode."""
    if getattr(sys, 'frozen', False):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, filename)

def create_fallback_icon():
    """Generates an in-memory gold padlock icon if padlock.ico is missing."""
    img = Image.new('RGBA', (64, 64), (255, 255, 255, 0))
    d = ImageDraw.Draw(img)
    d.arc([16, 8, 48, 40], 180, 0, fill='silver', width=6)
    d.line([16, 24, 16, 32], fill='silver', width=6)
    d.line([48, 24, 48, 32], fill='silver', width=6)
    d.rounded_rectangle([12, 28, 52, 56], radius=4, fill='gold', outline='darkgoldenrod', width=2)
    d.ellipse([28, 36, 36, 44], fill='black')
    d.polygon([30, 42, 34, 42, 35, 50, 29, 50], fill='black')
    return img

def show_toast_notification():
    """Slides a 5-second auto-dismiss Toast Notification on launch."""
    # Give Windows time to fully load the system tray icon first
    time.sleep(2)
    
    title = "KidKeys — Toddler Locker Active"
    message = "Running in background!\n• LOCK: Tap CAPS LOCK 3x\n• UNLOCK: Tap CAPS LOCK 5x"

    if notification:
        try:
            notification.notify(
                title=title,
                message=message,
                app_name="KidKeys",
                timeout=5
            )
            return
        except Exception:
            pass

    global tray_icon
    if tray_icon:
        try:
            tray_icon.notify(message, title)
        except Exception:
            pass

def subscribe_action(icon, item):
    """Opens the official Telegram community in the default web browser."""
    webbrowser.open("https://t.me/kidkeysofficial")

def support_action(icon, item):
    """Opens a Tkinter popup window with copyable crypto addresses."""
    def show_popup():
        root = tk.Tk()
        root.title("Support KidKeys 💖")
        root.geometry("450x260")
        
        # Center the window on the screen
        root.eval('tk::PlaceWindow . center')
        
        lbl = tk.Label(root, text="KidKeys is 100% free! Support the developer:", font=("Helvetica", 10, "bold"), fg="navy")
        lbl.pack(pady=10)
        
        # Use a Text widget so users can easily highlight and copy the addresses
        txt = tk.Text(root, height=7, width=50, font=("Consolas", 10))
        txt.insert(tk.END, "Bitcoin Address:\n16DYQP8LwdVGzcmNoWq6haUcsVUuUXMKY1\n\nEVM Address (USDT, USDC, ETH, BNB):\n0x0163613124b4e5027e4c2122e9e0cbd7fc773458")
        txt.config(state=tk.DISABLED) # Read-only but still copyable
        txt.pack(padx=10, pady=5)
        
        btn = tk.Button(root, text="Awesome, Thanks!", command=root.destroy, font=("Helvetica", 9, "bold"))
        btn.pack(pady=10)
        
        # Bring to front
        root.attributes('-topmost', True)
        root.mainloop()
        
    # Run in a separate thread to prevent freezing the system tray icon
    threading.Thread(target=show_popup, daemon=True).start()

def exit_action(icon, item):
    """Safely stop listeners, re-enable touchpad if locked, and terminate."""
    global is_locked
    if is_locked:
        set_touchpad_state(enable=True)
    if current_keyboard_listener:
        current_keyboard_listener.stop()
    if current_mouse_listener:
        current_mouse_listener.stop()
    icon.stop()
    os._exit(0)

def setup_tray():
    """Initializes the background System Tray icon with Support/Subscribe links."""
    global tray_icon
    ico_path = get_resource_path("padlock.ico")
    if os.path.exists(ico_path):
        try:
            image = Image.open(ico_path)
        except Exception:
            image = create_fallback_icon()
    else:
        image = create_fallback_icon()

    menu = pystray.Menu(
        pystray.MenuItem("KidKeys Active", lambda: None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("⭐ Subscribe (@kidkeysofficial)", subscribe_action),
        pystray.MenuItem("💖 Support Developer", support_action),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Exit KidKeys", exit_action)
    )
    tray_icon = pystray.Icon("KidKeys", image, "KidKeys Toddler Locker", menu)
    tray_icon.run_detached()

def add_to_startup():
    """Adds the executable to the Windows Registry to run on startup."""
    try:
        if getattr(sys, 'frozen', False):
            app_path = sys.executable
        else:
            app_path = os.path.abspath(__file__)

        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "KidKeysToddlerLocker"

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, f'"{app_path}"')
    except Exception as e:
        print(f"Failed to add to startup registry: {e}")

def set_touchpad_state(enable=True):
    """
    3-Tier Touchpad & Gesture Lock:
    1. Injects Win + Ctrl + F24 OS hotkey.
    2. Overrides PrecisionTouchPad Registry status + Shell notification.
    3. Executes silent PnP Device hardware enable/disable.
    """
    # 1. Hotkey Toggle
    try:
        f24_key = KeyCode.from_vk(0x87)
        with kbd_controller.pressed(Key.cmd, Key.ctrl):
            kbd_controller.press(f24_key)
            kbd_controller.release(f24_key)
    except Exception:
        pass

    # 2. Windows Precision Touchpad Registry & Shell Broadcast
    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\PrecisionTouchPad\Status"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "Enabled", 0, winreg.REG_DWORD, 1 if enable else 0)
        
        ctypes.windll.user32.SendMessageTimeoutW(
            0xFFFF, 0x001A, 0, "PrecisionTouchPad", 0x0002, 1000, None
        )
    except Exception:
        pass

    # 3. Direct Hardware Device Command (PowerShell PnP)
    try:
        cmd = "Enable-PnpDevice" if enable else "Disable-PnpDevice"
        ps_script = f"Get-PnpDevice -Class Touchpad -ErrorAction SilentlyContinue | {cmd} -Confirm:$false"
        subprocess.run(["powershell", "-Command", ps_script], creationflags=0x08000000)
    except Exception:
        pass

def handle_press(key):
    global is_locked, trigger_tap_count, last_tap_time
    
    try:
        if key == keyboard.Key.caps_lock:
            current_time = time.time()
            
            if current_time - last_tap_time < 0.8:
                trigger_tap_count += 1
            else:
                trigger_tap_count = 1
                
            last_tap_time = current_time
            
            if not is_locked:
                if trigger_tap_count >= 3:
                    is_locked = True
                    trigger_tap_count = 0
                    
                    play_beep_async(1200, 150)
                    play_beep_async(1200, 150)

                    # Fully kill Touchpad hardware & gestures
                    set_touchpad_state(enable=False)
                    
                    # Clamp down physical input listeners
                    switch_listeners()
            else:
                if trigger_tap_count >= 5:
                    is_locked = False
                    trigger_tap_count = 0
                    
                    play_beep_async(600, 300)

                    # Lift input suppression first
                    switch_listeners()
                    
                    # Restore Touchpad hardware & gestures
                    set_touchpad_state(enable=True)
    except Exception:
        pass

def switch_listeners():
    global current_keyboard_listener, current_mouse_listener
    
    if current_keyboard_listener:
        current_keyboard_listener.stop()
    if current_mouse_listener:
        current_mouse_listener.stop()
        
    if is_locked:
        current_keyboard_listener = keyboard.Listener(on_press=handle_press, suppress=True)
        current_mouse_listener = mouse.Listener(suppress=True)
    else:
        current_keyboard_listener = keyboard.Listener(on_press=handle_press, suppress=False)
        current_mouse_listener = None
        
    current_keyboard_listener.start()
    if current_mouse_listener:
        current_mouse_listener.start()

# --- Main Execution ---

add_to_startup()
setup_tray()
show_toast_notification()
switch_listeners()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    if is_locked:
        set_touchpad_state(enable=True)
        
    if current_keyboard_listener:
        current_keyboard_listener.stop()
    if current_mouse_listener:
        current_mouse_listener.stop()