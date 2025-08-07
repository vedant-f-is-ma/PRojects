import tkinter as tk
from tkinter import ttk, scrolledtext
import openai
from datetime import datetime

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ChatGPT Interface")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")

        # Configure OpenAI API
        self.api_key = ""  # You'll need to add your API key here
        openai.api_key = self.api_key

        # Create main frame
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Chat display area
        self.chat_display = scrolledtext.ScrolledText(
            self.main_frame,
            wrap=tk.WORD,
            width=70,
            height=20,
            font=("Arial", 12),
            bg="white"
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.chat_display.config(state=tk.DISABLED)

        # Input area
        self.input_frame = ttk.Frame(self.main_frame)
        self.input_frame.pack(fill=tk.X, pady=(0, 10))

        self.message_input = ttk.Entry(
            self.input_frame,
            font=("Arial", 12)
        )
        self.message_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.message_input.bind("<Return>", self.send_message)

        self.send_button = ttk.Button(
            self.input_frame,
            text="Send",
            command=self.send_message
        )
        self.send_button.pack(side=tk.RIGHT)

        # API Key input
        self.api_frame = ttk.Frame(self.main_frame)
        self.api_frame.pack(fill=tk.X)

        ttk.Label(
            self.api_frame,
            text="OpenAI API Key:",
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.api_key_input = ttk.Entry(
            self.api_frame,
            show="*",
            width=50
        )
        self.api_key_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.save_key_button = ttk.Button(
            self.api_frame,
            text="Save Key",
            command=self.save_api_key
        )
        self.save_key_button.pack(side=tk.RIGHT)

        # Welcome message
        self.add_message("System", "Welcome! Please enter your OpenAI API key and start chatting.")

    def save_api_key(self):
        self.api_key = self.api_key_input.get()
        openai.api_key = self.api_key
        self.add_message("System", "API key saved successfully!")

    def add_message(self, sender, message):
        self.chat_display.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M")
        
        if sender == "User":
            self.chat_display.insert(tk.END, f"\nYou ({timestamp}):\n", "user")
            self.chat_display.insert(tk.END, f"{message}\n", "user_msg")
        elif sender == "Assistant":
            self.chat_display.insert(tk.END, f"\nAssistant ({timestamp}):\n", "assistant")
            self.chat_display.insert(tk.END, f"{message}\n", "assistant_msg")
        else:
            self.chat_display.insert(tk.END, f"\n{message}\n", "system")

        self.chat_display.tag_configure("user", foreground="blue")
        self.chat_display.tag_configure("user_msg", foreground="black")
        self.chat_display.tag_configure("assistant", foreground="green")
        self.chat_display.tag_configure("assistant_msg", foreground="black")
        self.chat_display.tag_configure("system", foreground="gray")

        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def send_message(self, event=None):
        message = self.message_input.get().strip()
        if not message:
            return

        if not self.api_key:
            self.add_message("System", "Please enter your OpenAI API key first!")
            return

        self.add_message("User", message)
        self.message_input.delete(0, tk.END)

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": message}
                ]
            )
            assistant_response = response.choices[0].message.content
            self.add_message("Assistant", assistant_response)
        except Exception as e:
            self.add_message("System", f"Error: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
