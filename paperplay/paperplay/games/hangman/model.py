from __future__ import annotations

import random
import string
from dataclasses import dataclass


@dataclass
class HangmanState:
    word: str
    lives: int
    guessed: set[str]

    @staticmethod
    def new(word: str, lives: int = 6) -> "HangmanState":
        w = word.strip().lower()
        if not w or any(ch not in string.ascii_lowercase for ch in w):
            raise ValueError("word must be alphabetic")
        if lives <= 0:
            raise ValueError("lives must be positive")
        return HangmanState(word=w, lives=lives, guessed=set())

    def masked(self) -> str:
        return " ".join(ch if ch in self.guessed else "_" for ch in self.word)

    def is_won(self) -> bool:
        return all(ch in self.guessed for ch in self.word)

    def is_lost(self) -> bool:
        return self.lives <= 0 and not self.is_won()

    def guess(self, ch: str) -> bool:
        if self.is_won() or self.is_lost():
            raise ValueError("game is over")
        s = ch.strip().lower()
        if len(s) != 1 or s not in string.ascii_lowercase:
            raise ValueError("guess must be a single letter")
        if s in self.guessed:
            return s in self.word
        self.guessed.add(s)
        if s not in self.word:
            self.lives -= 1
            return False
        return True


def choose_word(words: list[str], rng: random.Random | None = None) -> str:
    if not words:
        raise ValueError("no words available")
    r = rng or random.Random()
    return r.choice(words)

