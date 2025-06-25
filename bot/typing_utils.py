import asyncio
import random
import string
import time

class TypingUtils:
    def __init__(self, wpm=80, accuracy=95):
        """
        wpm: target words per minute (integer)
        accuracy: target accuracy in percent (integer 0-100)
        """
        self.wpm = wpm
        self.accuracy = accuracy
        self.chars_per_word = 5  # standard estimate

    def get_char_delay(self):
        """
        Calculate delay between each keystroke in seconds based on WPM.
        WPM = words per minute, each word ~5 chars.
        """
        cps = (self.wpm * self.chars_per_word) / 60  # chars per second
        delay = 1 / cps if cps > 0 else 0.1
        # Add some randomness for human feel
        delay += random.uniform(-0.01, 0.03)
        return max(0.005, delay)

    def should_make_typo(self):
        """
        Decide if typo should be made based on accuracy percentage.
        """
        return random.uniform(0, 100) > self.accuracy

    def random_typo_char(self, correct_char):
        """
        Generate a random typo character close to the correct one,
        or just a random lowercase letter.
        """
        letters = string.ascii_lowercase
        if correct_char.lower() in letters:
            # Slightly biased to adjacent keyboard chars could be added here
            return random.choice(letters.replace(correct_char.lower(), ''))
        return random.choice(letters)

    async def type_text(self, element, text, send_key_func):
        """
        Types given text into element with human-like delays.
        
        Parameters:
        - element: browser element (for example, Playwright or Selenium element)
        - text: the string to type
        - send_key_func: async function to send keys to element, e.g. element.type or element.send_keys
          It should accept a single character and handle sending it.
        """
        i = 0
        while i < len(text):
            c = text[i]
            if self.should_make_typo():
                # make a typo
                typo_char = self.random_typo_char(c)
                await send_key_func(typo_char)
                await asyncio.sleep(self.get_char_delay())

                # Backspace to fix typo
                await send_key_func('\b')  # Assuming '\b' triggers backspace
                await asyncio.sleep(self.get_char_delay())

            # Type the correct character
            await send_key_func(c)
            await asyncio.sleep(self.get_char_delay())
            i += 1

    async def press_enter(self, send_key_func):
        """
        Press Enter key to submit (race done)
        """
        await send_key_func('\n')  # or '\r' depending on platform


