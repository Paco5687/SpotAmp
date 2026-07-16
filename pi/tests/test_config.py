"""Config loading: defaults, toml overrides, derived values."""

from spotamp.config import Config


def test_defaults_are_mock_and_square():
    cfg = Config()
    assert cfg.backend == "mock"
    assert cfg.controls == "mock"
    assert cfg.window_size == (720, 720)
    assert cfg.battery == "none"


def test_redirect_uri_uses_loopback_ip():
    cfg = Config()
    # Spotify banned "localhost"; must be the explicit loopback IP.
    assert cfg.spotify_redirect_uri == "http://127.0.0.1:8888/callback"
    cfg.spotify_redirect_port = 9000
    assert cfg.spotify_redirect_uri.endswith(":9000/callback")


def test_load_missing_file_returns_defaults(tmp_path):
    cfg = Config.load(tmp_path / "nope.toml")
    assert cfg.backend == "mock"


def test_load_overrides_and_ignores_unknown_keys(tmp_path):
    p = tmp_path / "config.toml"
    p.write_text(
        'backend = "librespot"\n'
        "window_size = [500, 800]\n"
        "fps = 60\n"
        'not_a_real_key = "ignored"\n',
        encoding="utf-8",
    )
    cfg = Config.load(p)
    assert cfg.backend == "librespot"
    assert cfg.window_size == (500, 800)  # list from toml becomes a tuple
    assert cfg.fps == 60
    assert not hasattr(cfg, "not_a_real_key")


def test_token_path_override(tmp_path):
    cfg = Config()
    assert cfg.token_path().name == "spotify_token.json"
    cfg.spotify_token_path = str(tmp_path / "tok.json")
    assert cfg.token_path() == tmp_path / "tok.json"
