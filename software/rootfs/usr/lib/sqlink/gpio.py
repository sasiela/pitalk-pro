from pathlib import Path


PTT_SQL_GPIO = 536
GPIO_PATH = Path(
    f"/sys/class/gpio/gpio{PTT_SQL_GPIO}"
)


def available():
    return GPIO_PATH.exists()


def get_value():
    return int(
        (GPIO_PATH / "value")
        .read_text()
        .strip()
    )


def set_value(value):
    value = 1 if value else 0

    (GPIO_PATH / "value").write_text(
        str(value)
    )


def ptt_on():
    # SQLink architecture:
    # LOW = SQL open / TX path active
    set_value(0)


def ptt_off():
    # HIGH = idle / SQL closed
    set_value(1)


def is_ptt_active():
    return get_value() == 0
