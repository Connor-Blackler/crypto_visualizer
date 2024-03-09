from main.wmain import Wmain
from shared_crypto_analysis.custom_indicators.AFR import get_AFR, OptionsAFR

if __name__ == "__main__":
    # main_window = Wmain(1200, 1000)
    # main_window.run()

    assets = "BTC"
    options = OptionsAFR(period=14, atr_factor=2.0)
    result_df = get_AFR(assets, options)
