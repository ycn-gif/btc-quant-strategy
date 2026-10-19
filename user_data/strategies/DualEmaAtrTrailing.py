from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta

class DualEmaAtrTrailing(IStrategy):
    """
    BTC/USDT 1h 双 EMA + RSI 过滤 + 原生移动止损
    """
    INTERFACE_VERSION = 3
    timeframe = '1h'
    can_short = False

    # 原生移动止损
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.02
    trailing_only_offset_is_reached = True

    # 兜底止损和止盈
    stoploss = -0.05
    minimal_roi = {"0": 0.15}

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['ema20'] = ta.EMA(dataframe, timeperiod=20)
        dataframe['ema50'] = ta.EMA(dataframe, timeperiod=50)
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        dataframe['atr'] = ta.ATR(dataframe, timeperiod=14)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['ema20'] > dataframe['ema50']) &
                (dataframe['ema20'].shift(1) <= dataframe['ema50'].shift(1)) &
                (dataframe['rsi'] < 70) &
                (dataframe['volume'] > 0)
            ),
            'enter_long'
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['ema20'] < dataframe['ema50']) &
                (dataframe['ema20'].shift(1) >= dataframe['ema50'].shift(1)) &
                (dataframe['volume'] > 0)
            ),
            'exit_long'
        ] = 1
        return dataframe