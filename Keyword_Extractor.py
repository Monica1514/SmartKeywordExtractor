#!/usr/bin/env python
# coding: utf-8

# In[11]:


import tkinter as tk
from tkinter import scrolledtext, messagebox, font
import string
import re
from sklearn.feature_extraction.text import TfidfVectorizer

# Basic stopwords list (you can extend this)
stop_words = set("""
a about above after again against all am an and any are aren't as at be because been before being below between both but by
can't cannot could couldn't did didn't do does doesn't doing don't down during each few for from further had hadn't has hasn't
have haven't having he he'd he'll he's her here here's hers herself him himself his how how's i i'd i'll i'm i've if in into
is isn't it it's its itself let's me more most mustn't my myself no nor not of off on once only or other ought our ours
ourselves out over own same shan't she she'd she'll she's should shouldn't so some such than that that's the their theirs
them themselves then there there's these they they'd they'll they're they've this those through to too under until up very was
wasn't we we'd we'll we're we've were weren't what what's when when's where where's which while who who's whom why why's with
won't would wouldn't you you'd you'll you're you've your yours yourself yourselves
""".split())

# Preprocessing function
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'\d+', '', text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    tokens = text.split()
    tokens = [word for word in tokens if word not in stop_words]
    return ' '.join(tokens)

# Keyword extraction function
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

# GUI function for extract button
def on_extract():
    input_text = input_box.get("1.0", tk.END).strip()
    if not input_text:
        messagebox.showwarning("Input Needed", "Please enter product descriptions.")
        return

    descriptions = [desc.strip() for desc in input_text.split('\n') if desc.strip()]
    keywords = extract_keywords(descriptions)

    output_box.config(state='normal')
    output_box.delete("1.0", tk.END)
    for i, kw in enumerate(keywords):
        capitalized = [word.capitalize() for word in kw]
        output_box.insert(tk.END, f"Product {i+1} Keywords: {', '.join(capitalized)}\n", "bold")
    output_box.config(state='disabled')

# Create main window
root = tk.Tk()
root.title("Keyword Extractor")

# Input label and text box
tk.Label(root, text="Enter product descriptions (one per line):").grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky='w')
input_box = scrolledtext.ScrolledText(root, height=10, width=60)
input_box.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

# Start button - styled, larger, centered
start_button = tk.Button(
    root,
    text="Start",
    command=on_extract,
    bg="#add8e6",         # Light blue background
    fg="black",
    font=("Helvetica", 14, "bold"),
    padx=30,
    pady=10
)
start_button.grid(row=2, column=0, columnspan=2, pady=10)

# Output box - read-only with bold text
output_font = font.Font(family="Helvetica", size=12, weight="bold")
output_box = scrolledtext.ScrolledText(root, height=10, width=60, state='disabled')
output_box.tag_configure("bold", font=output_font)
output_box.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

# Run the app
root.mainloop()


# In[ ]:




