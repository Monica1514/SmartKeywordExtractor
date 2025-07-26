import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import string
import re
import threading
import time
from sklearn.feature_extraction.text import TfidfVectorizer

# ---------------- User Database (Username → {password, email}) ---------------- #
users = {"admin": {"password": "1234", "email": "admin@example.com"}}

# ---------------- Registration Page ---------------- #
def show_register():
    register_window = tk.Toplevel()
    register_window.title("📝 Register")
    register_window.geometry("400x350")
    register_window.configure(bg="#1f1f2e")

    def register_user():
        new_username = new_user_entry.get().strip()
        new_password = new_pass_entry.get().strip()
        new_email = new_email_entry.get().strip()

        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

        if not new_username or not new_password or not new_email:
            messagebox.showwarning("Error", "All fields are required.")
            return
        if not re.match(email_pattern, new_email):
            messagebox.showerror("Invalid Email", "Please enter a valid email address (e.g., example@example.com).")
            return
        if new_username in users:
            messagebox.showerror("Error", "Username already exists.")
            return

        users[new_username] = {"password": new_password, "email": new_email}
        messagebox.showinfo("Success", "Registration successful!")
        register_window.destroy()

    tk.Label(register_window, text="Create a New Account", font=("Verdana", 16, "bold"), fg="#00d9ff", bg="#1f1f2e").pack(pady=15)
    tk.Label(register_window, text="Username:", font=("Verdana", 12), bg="#1f1f2e", fg="white").pack()
    new_user_entry = tk.Entry(register_window, font=("Verdana", 12))
    new_user_entry.pack(pady=5)

    tk.Label(register_window, text="Password:", font=("Verdana", 12), bg="#1f1f2e", fg="white").pack()
    new_pass_entry = tk.Entry(register_window, font=("Verdana", 12), show="*")
    new_pass_entry.pack(pady=5)

    tk.Label(register_window, text="Email:", font=("Verdana", 12), bg="#1f1f2e", fg="white").pack()
    new_email_entry = tk.Entry(register_window, font=("Verdana", 12))
    new_email_entry.pack(pady=5)

    tk.Button(register_window, text="Register", command=register_user, font=("Verdana", 12, "bold"), bg="#007bff", fg="white", width=15).pack(pady=20)

# ---------------- Login Page ---------------- #
def show_login():
    login_window = tk.Tk()
    login_window.title("🔐 Login")
    login_window.geometry("400x350")
    login_window.configure(bg="#1f1f2e")

    def authenticate():
        username = user_entry.get().strip()
        password = pass_entry.get().strip()
        email = email_entry.get().strip()

        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

        if not re.match(email_pattern, email):
            messagebox.showerror("Invalid Email", "Please enter a valid email address (e.g., example@example.com).")
            return

        if username in users:
            user_data = users[username]
            if user_data["password"] == password and user_data["email"] == email:
                login_window.destroy()
                show_main_app()
            else:
                messagebox.showerror("Login Failed", "Invalid password or email.")
        else:
            messagebox.showerror("Login Failed", "Username does not exist.")

    tk.Label(login_window, text="Login to Keyword Extractor", font=("Verdana", 16, "bold"), fg="#00d9ff", bg="#1f1f2e").pack(pady=15)

    tk.Label(login_window, text="Username:", font=("Verdana", 12), bg="#1f1f2e", fg="white").pack()
    user_entry = tk.Entry(login_window, font=("Verdana", 12))
    user_entry.pack(pady=5)

    tk.Label(login_window, text="Password:", font=("Verdana", 12), bg="#1f1f2e", fg="white").pack()
    pass_entry = tk.Entry(login_window, font=("Verdana", 12), show="*")
    pass_entry.pack(pady=5)

    tk.Label(login_window, text="Email:", font=("Verdana", 12), bg="#1f1f2e", fg="white").pack()
    email_entry = tk.Entry(login_window, font=("Verdana", 12))
    email_entry.pack(pady=5)

    tk.Button(login_window, text="Login", command=authenticate, font=("Verdana", 12, "bold"), bg="#28a745", fg="white", width=15).pack(pady=10)
    tk.Button(login_window, text="Register", command=show_register, font=("Verdana", 11), bg="#6c757d", fg="white").pack()

    login_window.mainloop()

# ---------------- Main Application (Keyword Extractor) ---------------- #
def show_main_app():
    def preprocess_text(text):
        text = text.lower()
        text = re.sub(r'\d+', '', text)
        text = text.translate(str.maketrans('', '', string.punctuation))
        tokens = text.split()
        tokens = [word for word in tokens if word not in stop_words]
        return ' '.join(tokens)

    def extract_keywords(texts, top_n=5):
        preprocessed_texts = [preprocess_text(text) for text in texts]
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(preprocessed_texts)
        feature_names = vectorizer.get_feature_names_out()
        keywords = []
        for i in range(tfidf_matrix.shape[0]):
            scores = zip(feature_names, tfidf_matrix[i].toarray().flatten())
            sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
            keywords.append([word for word, score in sorted_scores[:top_n]])
        return keywords

    def start_extraction():
        start_button.config(state='disabled')
        threading.Thread(target=extract_process).start()

    def clear_all():
        input_box.delete("1.0", tk.END)
        output_box.config(state='normal')
        output_box.delete("1.0", tk.END)
        output_box.config(state='disabled')
        highlight_box.config(state='normal')
        highlight_box.delete("1.0", tk.END)
        highlight_box.config(state='disabled')
        start_button.config(state='normal')

    def save_to_file():
        output_text = output_box.get("1.0", tk.END).strip()
        if not output_text:
            messagebox.showwarning("Warning", "No keywords to save!")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(output_text)
            messagebox.showinfo("Saved", "Keywords saved successfully!")

    def extract_process():
        input_text = input_box.get("1.0", tk.END).strip()
        if not input_text:
            messagebox.showwarning("Warning", "Please enter product descriptions.")
            start_button.config(state='normal')
            return
        descriptions = [desc.strip() for desc in input_text.split('\n') if desc.strip()]
        top_n = int(keyword_num.get()) if keyword_num.get().isdigit() else 5
        keywords = extract_keywords(descriptions, top_n)

        output_box.config(state='normal')
        output_box.delete("1.0", tk.END)
        highlight_box.config(state='normal')
        highlight_box.delete("1.0", tk.END)

        for i, desc in enumerate(descriptions):
            capitalized = [word.capitalize() for word in keywords[i]]
            output_box.insert(tk.END, f"Product {i+1} Keywords: {', '.join(capitalized)}\n", "bold")
            highlight_box.insert(tk.END, f"Product {i+1}:\n", "section")
            words = desc.split()
            for word in words:
                clean_word = preprocess_text(word)
                if any(clean_word == kw for kw in keywords[i]):
                    highlight_box.insert(tk.END, word + " ", "highlight")
                else:
                    highlight_box.insert(tk.END, word + " ")
                time.sleep(0.001)
            highlight_box.insert(tk.END, "\n\n")

        output_box.config(state='disabled')
        highlight_box.config(state='disabled')
        start_button.config(state='normal')

    stop_words = set("""a about above after again against all am an and any are aren't as at be because been before being below \
        between both but by can't cannot could couldn't did didn't do does doesn't doing don't down during each few for from further had hadn't \
        has hasn't have haven't having he he'd he'll he's her here here's hers herself him himself his how how's i i'd i'll i'm i've if in into is \
        isn't it it's its itself let's me more most mustn't my myself no nor not of off on once only or ought our ours ourselves out over own same \
        shan't she she'd she'll she's should shouldn't so some such than that that's the their theirs them themselves then there there's these they \
        they'd they'll they're they've this those through to too under until up very was wasn't we we'd we'll we're we've were weren't what what's \
        when when's where where's which while who who's whom why why's with won't would wouldn't you you'd you'll you're you've your yours yourself \
        yourselves""".split())

    root = tk.Tk()
    root.title("🔍 Smart Keyword Extractor Tool")
    root.geometry("1000x800")
    root.configure(bg="#1f1f2e")

    title_font = ("Verdana", 20, "bold")
    label_font = ("Verdana", 12)
    button_font = ("Verdana", 11, "bold")

    top_frame = tk.Frame(root, bg="#1f1f2e")
    top_frame.pack(pady=10)
    input_frame = tk.Frame(root, bg="#2a2a3d")
    input_frame.pack(pady=10, padx=10, fill="x")
    button_frame = tk.Frame(root, bg="#1f1f2e")
    button_frame.pack(pady=10)
    output_frame = tk.Frame(root, bg="#2a2a3d")
    output_frame.pack(pady=10, padx=10, fill="both", expand=True)

    tk.Label(top_frame, text="🔍 Smart Keyword Extractor", font=title_font, fg="#00d9ff", bg="#1f1f2e").pack()
    tk.Label(input_frame, text="Enter product descriptions (one per line):", font=label_font, fg="white", bg="#2a2a3d").pack(anchor="w", padx=10, pady=5)
    input_box = scrolledtext.ScrolledText(input_frame, height=8, width=100, font=("Verdana", 11))
    input_box.pack(padx=10, pady=5)

    tk.Label(input_frame, text="Number of keywords to extract:", font=label_font, fg="white", bg="#2a2a3d").pack(anchor="w", padx=10, pady=5)
    keyword_num = tk.Entry(input_frame, width=5, font=("Verdana", 12))
    keyword_num.pack(anchor="w", padx=10, pady=5)

    start_button = tk.Button(button_frame, text="▶ Start", command=start_extraction, bg="#28a745", fg="white", font=button_font, width=16)
    start_button.grid(row=0, column=0, padx=10)

    clear_button = tk.Button(button_frame, text="🪟 Clear", command=clear_all, bg="#dc3545", fg="white", font=button_font, width=16)
    clear_button.grid(row=0, column=1, padx=10)

    save_button = tk.Button(button_frame, text="📀 Save to File", command=save_to_file, bg="#007bff", fg="white", font=button_font, width=16)
    save_button.grid(row=0, column=2, padx=10)

    tk.Label(output_frame, text="Extracted Keywords:", font=label_font, fg="white", bg="#2a2a3d").pack(anchor="w", padx=10, pady=5)
    output_box = scrolledtext.ScrolledText(output_frame, height=8, width=100, state='disabled', font=("Verdana", 11))
    output_box.tag_configure("bold", font=("Verdana", 11, "bold"))
    output_box.pack(padx=10, pady=5)

    tk.Label(output_frame, text="Preview with Highlighted Keywords:", font=label_font, fg="white", bg="#2a2a3d").pack(anchor="w", padx=10, pady=5)
    highlight_box = scrolledtext.ScrolledText(output_frame, height=10, width=100, state='disabled', font=("Verdana", 11))
    highlight_box.tag_configure("highlight", background="yellow", font=("Verdana", 11, "bold"))
    highlight_box.tag_configure("section", foreground="#00d9ff", font=("Verdana", 12, "bold"))
    highlight_box.pack(padx=10, pady=5)

    root.mainloop()

# ---------------- Launch App ---------------- #
show_login()