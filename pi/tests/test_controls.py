"""Serial protocol: parsing inbound events, formatting outbound commands."""

from winamp_player.controls import (
    ControlEvent,
    ControlEventType,
    FADER_MAX,
    FaderId,
    cmd_fader_release,
    cmd_fader_target,
    cmd_led,
    parse_event,
)


def test_parse_button_event():
    ev = parse_event("EV BTN 4 1")
    assert ev == ControlEvent(ControlEventType.BUTTON, 4, 1)


def test_parse_fader_touch_enc_pot():
    assert parse_event("EV FADER 8 742").type is ControlEventType.FADER
    assert parse_event("EV TOUCH 9 0").value == 0
    assert parse_event("EV ENC 1 -3").value == -3
    assert parse_event("EV POT 0 1023").value == 1023


def test_parse_tolerates_whitespace():
    assert parse_event("  EV BTN 0 1 \r\n") == ControlEvent(ControlEventType.BUTTON, 0, 1)


def test_parse_rejects_junk():
    for junk in ("", "EV", "EV BTN 1", "EV WAT 1 2", "EV BTN x y",
                 "LOG something happened", "PONG"):
        assert parse_event(junk) is None, junk


def test_cmd_fader_target_format_and_clamp():
    assert cmd_fader_target(FaderId.VOLUME, 512) == "FADER 8 512\n"
    assert cmd_fader_target(FaderId.EQ0, -50) == "FADER 0 0\n"
    assert cmd_fader_target(FaderId.SEEK, 99999) == f"FADER 9 {FADER_MAX}\n"


def test_cmd_fader_release_and_led():
    assert cmd_fader_release(FaderId.PREAMP) == "FADER_RELEASE 7\n"
    assert cmd_led(0, 255, 128, 0) == "LED 0 255 128 0\n"
