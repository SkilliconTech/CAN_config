
from models.config_model import ConfigurationModel


def test_classic_can_default_settings():

    model = ConfigurationModel()

    assert model.classic_can["bitrate"] == "50.000 kbits/s"
    assert model.classic_can["enabled"] is False


def test_canfd_default_settings():

    model = ConfigurationModel()

    assert model.canfd["arbitration_bitrate"] == "500 kbits/s"
    assert model.canfd["data_bitrate"] == "500 kbits/s"


def test_classic_can_update():

    model = ConfigurationModel()

    settings = model.get_classic_can()
    settings["bitrate"] = "250.000 kbits/s"

    model.set_classic_can(settings)

    assert model.get_classic_can()["bitrate"] == "250.000 kbits/s"


def test_canfd_update():

    model = ConfigurationModel()

    settings = model.get_canfd()
    settings["data_bitrate"] = "2000 kbits/s"

    model.set_canfd(settings)

    assert model.get_canfd()["data_bitrate"] == "2000 kbits/s"


def test_reset_configuration():

    model = ConfigurationModel()

    settings = model.get_classic_can()
    settings["bitrate"] = "250.000 kbits/s"

    model.set_classic_can(settings)

    model.reset()

    assert model.get_classic_can()["bitrate"] == "50.000 kbits/s"


def test_model_returns_independent_copy():

    model = ConfigurationModel()

    settings = model.get_classic_can()
    settings["bitrate"] = "250.000 kbits/s"

    assert model.get_classic_can()["bitrate"] == "50.000 kbits/s"
