from paperplay.games.dotsboxes.model import DotsAndBoxesState


def test_dotsboxes_completes_box_and_keeps_turn() -> None:
    s = DotsAndBoxesState.new(3, 3)  # 2x2 boxes
    # Alternate moves that do not complete boxes yet, then let Player 1 complete.
    assert s.turn == 1
    s.play_edge("h", 0, 0)  # P1
    assert s.turn == 2
    s.play_edge("h", 0, 1)  # P2 elsewhere
    assert s.turn == 1
    s.play_edge("v", 0, 0)  # P1
    assert s.turn == 2
    s.play_edge("v", 0, 2)  # P2 elsewhere
    assert s.turn == 1
    s.play_edge("h", 1, 0)  # P1
    assert s.turn == 2
    s.play_edge("h", 2, 0)  # P2 elsewhere
    assert s.turn == 1
    completed = s.play_edge("v", 0, 1)  # P1 completes top-left box
    assert completed == 1
    assert s.score1 == 1
    assert s.turn == 1  # keeps turn

