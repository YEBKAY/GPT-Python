import random
import tkinter as tk
from tkinter import messagebox
import string

class HangmanGUI:
    def __init__(self, master):
        self.master = master
        master.title("Hangman Game with Hints")

        # Updated word list with hints
        self.words_with_hints = [
            ('python', 'A popular programming language'),
            ('java', 'A programming language known for its portability'),
            ('kotlin', 'A language used for Android development'),
            ('javascript', 'A scripting language for web development'),
            ('hangman', 'The name of this game'),
            ('programming', 'The process of writing computer software'),
            ('computer', 'An electronic device for storing and processing data'),
            ('science', 'The pursuit of knowledge and understanding'),
            ('artificial', 'Opposite of natural'),
            ('intelligence', 'Ability to acquire and apply knowledge and skills'),
        ]
        self.word, self.hint = random.choice(self.words_with_hints)
        self.word_letters = set(self.word)
        self.used_letters = set()
        self.lives = 6

        # Set up the GUI components
        self.label_hint = tk.Label(master, text=f"Hint: {self.hint}", font=('Helvetica', 14))
        self.label_hint.pack(pady=10)

        self.label_word = tk.Label(master, text=self.get_display_word(), font=('Helvetica', 18))
        self.label_word.pack(pady=20)

        self.label_lives = tk.Label(master, text=f"Lives Remaining: {self.lives}", font=('Helvetica', 14))
        self.label_lives.pack(pady=10)

        self.label_used = tk.Label(master, text="Used Letters: ", font=('Helvetica', 14))
        self.label_used.pack(pady=10)

        # Add on-screen keyboard
        self.buttons_frame = tk.Frame(master)
        self.buttons_frame.pack(pady=10)

        self.letter_buttons = {}
        for index, letter in enumerate(string.ascii_lowercase):
            button = tk.Button(
                self.buttons_frame, text=letter.upper(), width=4, font=('Helvetica', 12),
                command=lambda l=letter: self.guess_letter(l)
            )
            button.grid(row=index // 9, column=index % 9)
            self.letter_buttons[letter] = button

    def get_display_word(self):
        return ' '.join([letter if letter in self.used_letters else '_' for letter in self.word])

    def guess_letter(self, user_letter):
        if user_letter in self.used_letters:
            messagebox.showinfo("Already Used", f"You have already guessed '{user_letter.upper()}'.")
            return

        self.used_letters.add(user_letter)
        self.letter_buttons[user_letter]['state'] = 'disabled'  # Disable the button after it's used

        if user_letter in self.word_letters:
            self.word_letters.remove(user_letter)
            self.label_word.config(text=self.get_display_word())
            if not self.word_letters:
                messagebox.showinfo("Congratulations!", f"You guessed the word: {self.word}")
                self.master.after(0, self.master.destroy)
        else:
            self.lives -= 1
            self.label_lives.config(text=f"Lives Remaining: {self.lives}")
            if self.lives == 0:
                messagebox.showinfo("Game Over", f"You ran out of lives. The word was: {self.word}")
                self.master.after(0, self.master.destroy)

        used_letters_formatted = ' '.join(sorted(self.used_letters))
        self.label_used.config(text=f"Used Letters: {used_letters_formatted.upper()}")

if __name__ == "__main__":
    root = tk.Tk()
    game = HangmanGUI(root)
    root.mainloop()
