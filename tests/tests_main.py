import pytest
import time
from unittest import mock

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import main
from main import Game, GameState


@pytest.fixture
def game():
    with mock.patch("pygame.font.Font"):
        with mock.patch("pygame.image.load"):
            with mock.patch("pygame.transform.scale"):
                with mock.patch("pygame.mixer.Sound"):
                    return Game()


def test_initial_state(game):
    assert game.state == GameState.ENTRY
    assert game.level == 1
    assert game.score == 0
    assert isinstance(game.best_scores, dict)


@pytest.mark.parametrize("level,score,shots,new_score,new_shots,expected_score,expected_shots", [
    (1, 10, 5, 15, 6, 15, 6),
    (2, 20, 10, 20, 9, 20, 9),
    (3, 30, 15, 25, 20, 30, 15),
])
def test_update_best_score(game, level, score, shots, new_score, new_shots, expected_score, expected_shots):
    game.level = level
    game.best_scores[level] = {"score": score, "shots": shots}
    game.score = new_score
    game.total_shots = new_shots

    with mock.patch("builtins.open", mock.mock_open()):
        game.update_best_score()

    assert game.best_scores[level]["score"] == expected_score
    assert game.best_scores[level]["shots"] == expected_shots


def test_spawn_targets(game):
    game.level = 2
    game.spawn_targets()
    assert len(game.target_position) == 1
    x, y = game.target_position[0]
    assert 100 <= x <= 1266
    assert 100 <= y <= 468
    assert isinstance(game.target_spawn_time, float)
    assert game.next_spawn_time == 1.0


def test_load_scores_file_not_found(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "RESULTS_FILE", tmp_path / "fake.txt")
    with mock.patch("pygame.font.Font"):
        with mock.patch("pygame.image.load"):
            with mock.patch("pygame.transform.scale"):
                with mock.patch("pygame.mixer.Sound"):
                    g = Game()
    assert g.best_scores == {1: {"score": 0, "shots": 0},
                             2: {"score": 0, "shots": 0},
                             3: {"score": 0, "shots": 0}}


@pytest.mark.slow
def test_draw_timer(game):
    game.start_time = time.time() - 10
    game.paused_duration = 0
    remaining = game.draw_timer(mock.Mock())
    assert remaining in range(49, 51)
