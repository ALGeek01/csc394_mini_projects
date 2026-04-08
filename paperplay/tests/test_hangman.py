from paperplay.games.hangman.model import HangmanState


def test_hangman_mask_and_guess() -> None:
    s = HangmanState.new("paper", lives=2)
    assert s.masked() == "_ _ _ _ _"
    assert s.guess("p") is True
    assert s.masked().startswith("p")
    assert s.guess("z") is False
    assert s.lives == 1


def test_hangman_win() -> None:
    s = HangmanState.new("aa", lives=1)
    assert s.guess("a") is True
    assert s.is_won()

