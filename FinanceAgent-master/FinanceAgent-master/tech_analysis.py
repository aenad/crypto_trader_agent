import pandas as pd
import numpy as np
from typing import Tuple, List, Dict, Union, Optional
import pandas as pd
import pandas_ta as ta
import numpy as np
from typing import Literal, Dict, Any


def preprocess_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess cryptocurrency data to ensure it has the correct format.
    
    Args:
        data (pd.DataFrame): Raw cryptocurrency data
        
    Returns:
        pd.DataFrame: Preprocessed data
    """
    # Make a copy to avoid modifying the original data
    df = data.copy()
    
    # Ensure datetime is in the correct format
    if 'datetime' in df.columns:
        df['datetime'] = pd.to_datetime(df['datetime'])
        df.set_index('datetime', inplace=True)
    
    # Ensure all required columns exist
    required_columns = ['open', 'high', 'low', 'close']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Required column '{col}' not found in data")
    
    # Check if at least one volume column exists
    volume_columns = ['volume', 'volumefrom', 'volumeto']
    has_volume = any(col in df.columns for col in volume_columns)
    
    if not has_volume:
        # If no volume column exists, create a dummy one (strategies may still use it)
        print("Warning: No volume column found. Creating a dummy volume column.")
        df['volume'] = 1.0
    elif 'volume' not in df.columns:
        # If 'volume' doesn't exist but other volume columns do, use volumefrom as default
        if 'volumefrom' in df.columns:
            df['volume'] = df['volumefrom']
        else:
            df['volume'] = df['volumeto']
    
    # Convert columns to numeric if needed
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Handle any missing values
    df.dropna(inplace=True)
    
    return df

def support_resistance(data: pd.DataFrame, window: int = 10, threshold: float = 0.01) -> Dict[str, List[float]]:
    """
    Identify support and resistance levels in price data.
    
    Args:
        data (pd.DataFrame): Preprocessed price data
        window (int): Window size for identifying highs and lows
        threshold (float): Minimum distance between levels (as percentage)
        
    Returns:
        Dict: Dictionary containing support and resistance levels
    """
    df = preprocess_data(data)
    
    # Find local minima and maxima
    df['min'] = df['low'].rolling(window=window, center=True).min()
    df['max'] = df['high'].rolling(window=window, center=True).max()
    
    # Identify potential support levels (local minima)
    is_support = (df['min'] == df['low']) & (df['min'].shift(1) > df['min']) & (df['min'].shift(-1) > df['min'])
    
    # Identify potential resistance levels (local maxima)
    is_resistance = (df['max'] == df['high']) & (df['max'].shift(1) < df['max']) & (df['max'].shift(-1) < df['max'])
    
    # Extract support and resistance levels
    support_levels = df[is_support]['low'].tolist()
    resistance_levels = df[is_resistance]['high'].tolist()
    
    # Filter levels to remove those that are too close
    support_levels = filter_levels(support_levels, threshold)
    resistance_levels = filter_levels(resistance_levels, threshold)
    
    return {'support': support_levels, 'resistance': resistance_levels}

def filter_levels(levels: List[float], threshold: float) -> List[float]:
    """
    Filter out levels that are too close to each other.
    
    Args:
        levels (List[float]): List of price levels
        threshold (float): Minimum distance between levels (as percentage)
        
    Returns:
        List[float]: Filtered list of price levels
    """
    if not levels:
        return []
    
    levels.sort()
    filtered_levels = [levels[0]]
    
    for level in levels[1:]:
        if (level - filtered_levels[-1]) / filtered_levels[-1] > threshold:
            filtered_levels.append(level)
    
    return filtered_levels

def support_resistance_strategy(data: pd.DataFrame, window: int = 10, threshold: float = 0.01) -> str:
    """
    Strategy based on support and resistance levels.
    
    Args:
        data (pd.DataFrame): Preprocessed price data
        window (int): Window size for identifying highs and lows
        threshold (float): Minimum distance between levels (as percentage)
        
    Returns:
        str: "Bullish", "Bearish", or "Neutral"
    """
    df = preprocess_data(data)
    levels = support_resistance(df, window, threshold)
    
    current_price = df['close'].iloc[-1]
    
    # Find closest support and resistance
    supports = [s for s in levels['support'] if s < current_price]
    resistances = [r for r in levels['resistance'] if r > current_price]
    
    closest_support = max(supports) if supports else None
    closest_resistance = min(resistances) if resistances else None
    
    if closest_support is None or closest_resistance is None:
        return "Neutral"
    
    # Calculate distances to closest support and resistance
    support_distance = (current_price - closest_support) / current_price
    resistance_distance = (closest_resistance - current_price) / current_price
    
    # Decision based on proximity to support or resistance
    if support_distance < resistance_distance * 0.5:
        # Price is closer to support - bullish
        return "Bullish"
    elif resistance_distance < support_distance * 0.5:
        # Price is closer to resistance - bearish
        return "Bearish"
    else:
        # Price is in the middle - neutral
        return "Neutral"

def trend_following_strategy(data: pd.DataFrame, short_period: int = 20, long_period: int = 50) -> str:
    """
    Strategy based on trend following using moving averages.
    
    Args:
        data (pd.DataFrame): Preprocessed price data
        short_period (int): Short-term moving average period
        long_period (int): Long-term moving average period
        
    Returns:
        str: "Bullish", "Bearish", or "Neutral"
    """
    df = preprocess_data(data)
    
    # Calculate moving averages
    df['short_ma'] = df['close'].rolling(window=short_period).mean()
    df['long_ma'] = df['close'].rolling(window=long_period).mean()
    
    # Get current and previous values
    current_short_ma = df['short_ma'].iloc[-1]
    current_long_ma = df['long_ma'].iloc[-1]
    prev_short_ma = df['short_ma'].iloc[-2]
    prev_long_ma = df['long_ma'].iloc[-2]
    
    # Check for crossovers
    if current_short_ma > current_long_ma and prev_short_ma <= prev_long_ma:
        # Bullish crossover (short MA crosses above long MA)
        return "Bullish"
    elif current_short_ma < current_long_ma and prev_short_ma >= prev_long_ma:
        # Bearish crossover (short MA crosses below long MA)
        return "Bearish"
    elif current_short_ma > current_long_ma:
        # Already in an uptrend
        return "Bullish"
    elif current_short_ma < current_long_ma:
        # Already in a downtrend
        return "Bearish"
    else:
        return "Neutral"


def breakout_strategy(data: pd.DataFrame, window: int = 20, threshold: float = 0.01) -> str:
    """
    Strategy based on price breakouts from established ranges.
    
    Args:
        data (pd.DataFrame): Preprocessed price data
        window (int): Lookback window for range identification
        threshold (float): Threshold for breakout confirmation (as percentage)
        
    Returns:
        str: "Bullish", "Bearish", or "Neutral"
    """
    df = preprocess_data(data)
    
    # Calculate recent high and low in the lookback window
    recent_high = df['high'].rolling(window=window).max().iloc[-2]  # Use -2 to avoid including current bar
    recent_low = df['low'].rolling(window=window).min().iloc[-2]
    
    # Get current price
    current_close = df['close'].iloc[-1]
    previous_close = df['close'].iloc[-2]
    
    # Check for breakouts
    if current_close > recent_high * (1 + threshold) and previous_close <= recent_high:
        return "Bullish"  # Bullish breakout
    elif current_close < recent_low * (1 - threshold) and previous_close >= recent_low:
        return "Bearish"  # Bearish breakout
    else:
        return "Neutral"  # No breakout

def range_trading_strategy(data: pd.DataFrame, window: int = 20) -> str:
    """
    Strategy for trading in range-bound markets.
    
    Args:
        data (pd.DataFrame): Preprocessed price data
        window (int): Lookback window for range identification
        
    Returns:
        str: "Bullish", "Bearish", or "Neutral"
    """
    df = preprocess_data(data)
    
    # Determine if the market is range-bound
    recent_high = df['high'].rolling(window=window).max()
    recent_low = df['low'].rolling(window=window).min()
    price_range = (recent_high - recent_low) / recent_low
    
    # A market is considered range-bound if the range is relatively small
    is_range_bound = price_range.iloc[-1] < 0.05  # 5% range
    
    if not is_range_bound:
        return "Neutral"  # Not a range-bound market
    
    # Calculate average of high and low to find the mid-point of the range
    mid_point = (recent_high.iloc[-1] + recent_low.iloc[-1]) / 2
    current_price = df['close'].iloc[-1]
    
    # Determine position within the range
    if current_price < mid_point and current_price - recent_low.iloc[-1] < recent_high.iloc[-1] - current_price:
        return "Bullish"  # Price is in the lower half of the range - bullish
    elif current_price > mid_point and recent_high.iloc[-1] - current_price < current_price - recent_low.iloc[-1]:
        return "Bearish"  # Price is in the upper half of the range - bearish
    else:
        return "Neutral"  # Price is near the middle of the range

def fibonacci_retracement_strategy(data: pd.DataFrame, trend_periods: int = 100) -> str:
    """
    Strategy based on Fibonacci retracement levels.
    
    Args:
        data (pd.DataFrame): Preprocessed price data
        trend_periods (int): Number of periods to use for trend determination
        
    Returns:
        str: "Bullish", "Bearish", or "Neutral"
    """
    df = preprocess_data(data)
    
    # Determine the trend
    short_ma = df['close'].rolling(window=20).mean()
    long_ma = df['close'].rolling(window=50).mean()
    
    is_uptrend = short_ma.iloc[-1] > long_ma.iloc[-1]
    
    # Find significant high and low points based on the trend
    if is_uptrend:
        # In an uptrend, look for pullbacks from recent highs
        high_point = df['high'].iloc[-trend_periods:].max()
        high_point_idx = df['high'].iloc[-trend_periods:].idxmax()
        
        # Find the lowest point after the high
        subset = df.loc[high_point_idx:]
        if len(subset) <= 1:
            return "Neutral"  # Not enough data
            
        low_point = subset['low'].min()
        
        # Calculate Fibonacci levels (retracements of the up-move)
        diff = high_point - low_point
        fib_236 = low_point + 0.236 * diff
        fib_382 = low_point + 0.382 * diff
        fib_500 = low_point + 0.5 * diff
        fib_618 = low_point + 0.618 * diff
        
        current_price = df['close'].iloc[-1]
        
        # Determine if price is near a Fibonacci level
        if 0.99 * fib_618 <= current_price <= 1.01 * fib_618:
            return "Bullish"  # Strong bullish signal at 61.8% retracement
        elif 0.99 * fib_500 <= current_price <= 1.01 * fib_500:
            return "Bullish"  # Moderate bullish signal at 50% retracement
        elif 0.99 * fib_382 <= current_price <= 1.01 * fib_382:
            return "Bullish"  # Weaker bullish signal at 38.2% retracement
        elif 0.99 * fib_236 <= current_price <= 1.01 * fib_236:
            return "Neutral"  # Weakest retracement level
        else:
            return "Neutral"
    else:
        # In a downtrend, look for bounces from recent lows
        low_point = df['low'].iloc[-trend_periods:].min()
        low_point_idx = df['low'].iloc[-trend_periods:].idxmin()
        
        # Find the highest point after the low
        subset = df.loc[low_point_idx:]
        if len(subset) <= 1:
            return "Neutral"  # Not enough data
            
        high_point = subset['high'].max()
        
        # Calculate Fibonacci levels (retracements of the down-move)
        diff = high_point - low_point
        fib_236 = high_point - 0.236 * diff
        fib_382 = high_point - 0.382 * diff
        fib_500 = high_point - 0.5 * diff
        fib_618 = high_point - 0.618 * diff
        
        current_price = df['close'].iloc[-1]
        
        # Determine if price is near a Fibonacci level
        if 0.99 * fib_618 <= current_price <= 1.01 * fib_618:
            return "Bearish"  # Strong bearish signal at 61.8% retracement
        elif 0.99 * fib_500 <= current_price <= 1.01 * fib_500:
            return "Bearish"  # Moderate bearish signal at 50% retracement
        elif 0.99 * fib_382 <= current_price <= 1.01 * fib_382:
            return "Bearish"  # Weaker bearish signal at 38.2% retracement
        elif 0.99 * fib_236 <= current_price <= 1.01 * fib_236:
            return "Neutral"  # Weakest retracement level
        else:
            return "Neutral"

def multi_timeframe_analysis(data: pd.DataFrame, short_window: int = 20, long_window: int = 60) -> str:
    """
    Strategy based on multiple timeframe analysis.
    
    Args:
        data (pd.DataFrame): Preprocessed price data
        short_window (int): Window for short-term analysis
        long_window (int): Window for long-term analysis
        
    Returns:
        str: "Bullish", "Bearish", or "Neutral"
    """
    df = preprocess_data(data)
    
    # Resample to create higher timeframe data
    # Hourly data to 4-hour data
    df_4h = df.resample('4H').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }).dropna()
    
    # Apply trend analysis on both timeframes
    short_term_signal = trend_following_strategy(df, short_window, long_window)
    long_term_signal = trend_following_strategy(df_4h, short_window // 4, long_window // 4)  # Adjusted for 4h timeframe
    
    # Combine signals with higher weight on the longer timeframe
    if long_term_signal == "Bullish":
        if short_term_signal == "Bullish":
            return "Bullish"  # Strong bullish signal
        elif short_term_signal == "Bearish":
            return "Neutral"  # Mixed signals
        else:
            return "Bullish"  # Long-term signal dominates
    elif long_term_signal == "Bearish":
        if short_term_signal == "Bearish":
            return "Bearish"  # Strong bearish signal
        elif short_term_signal == "Bullish":
            return "Neutral"  # Mixed signals
        else:
            return "Bearish"  # Long-term signal dominates
    else:
        return short_term_signal  # If long-term is neutral, use short-term signal

def volume_confirmation_strategy(data: pd.DataFrame, ma_period: int = 20, volume_column: str = 'volume') -> str:
    """
    Strategy based on price action with volume confirmation.
    
    Args:
        data (pd.DataFrame): Preprocessed price data
        ma_period (int): Period for moving average calculation
        volume_column (str): Column to use for volume analysis ('volume', 'volumefrom', or 'volumeto')
        
    Returns:
        str: "Bullish", "Bearish", or "Neutral"
    """
    df = preprocess_data(data)
    
    # Ensure the selected volume column exists
    if volume_column not in df.columns:
        if 'volume' in df.columns:
            volume_column = 'volume'
        elif 'volumefrom' in df.columns:
            volume_column = 'volumefrom'
        elif 'volumeto' in df.columns:
            volume_column = 'volumeto'
        else:
            return "Neutral"  # No volume data available
    
    # Calculate price change and volume moving average
    df['price_change'] = df['close'] - df['open']
    df['volume_ma'] = df[volume_column].rolling(window=ma_period).mean()
    
    # Get recent values
    current_close = df['close'].iloc[-1]
    previous_close = df['close'].iloc[-2]
    current_volume = df[volume_column].iloc[-1]
    avg_volume = df['volume_ma'].iloc[-1]
    
    price_increasing = current_close > previous_close
    high_volume = current_volume > 1.5 * avg_volume  # Volume is 50% above average
    
    if price_increasing and high_volume:
        return "Bullish"  # Strong buying pressure
    elif not price_increasing and high_volume:
        return "Bearish"  # Strong selling pressure
    elif price_increasing and not high_volume:
        return "Neutral"  # Price rising but not confirmed by volume
    else:
        return "Neutral"  # Price falling but not confirmed by volument = 20) -> str:
    """
    Strategy based on price action with volume confirmation.
    
    Args:
        data (pd.DataFrame): Preprocessed price data
        ma_period (int): Period for moving average calculation
        
    Returns:
        str: "Bullish", "Bearish", or "Neutral"
    """
    df = preprocess_data(data)
    
    # Calculate price change and volume moving average
    df['price_change'] = df['close'] - df['open']
    df['volume_ma'] = df['volume'].rolling(window=ma_period).mean()
    
    # Get recent values
    current_close = df['close'].iloc[-1]
    previous_close = df['close'].iloc[-2]
    current_volume = df['volume'].iloc[-1]
    avg_volume = df['volume_ma'].iloc[-1]
    
    price_increasing = current_close > previous_close
    high_volume = current_volume > 1.5 * avg_volume  # Volume is 50% above average
    
    if price_increasing and high_volume:
        return "Bullish"  # Strong buying pressure
    elif not price_increasing and high_volume:
        return "Bearish"  # Strong selling pressure
    elif price_increasing and not high_volume:
        return "Neutral"  # Price rising but not confirmed by volume
    else:
        return "Neutral"  # Price falling but not confirmed by volume

def combined_strategy(data: pd.DataFrame) -> str:
    """
    Combined strategy using multiple price action techniques.
    
    Args:
        data (pd.DataFrame): Preprocessed price data
        
    Returns:
        str: "Bullish", "Bearish", or "Neutral"
    """
    # Apply individual strategies
    trend_signal = trend_following_strategy(data)
    support_resistance_signal = support_resistance_strategy(data)
    breakout_signal = breakout_strategy(data)
    fibonacci_signal = fibonacci_retracement_strategy(data)
    volume_signal = volume_confirmation_strategy(data)
    
    # Count signals
    bullish_count = sum(1 for signal in [trend_signal, support_resistance_signal, 
                                         breakout_signal, fibonacci_signal, volume_signal] 
                       if signal == "Bullish")
    
    bearish_count = sum(1 for signal in [trend_signal, support_resistance_signal, 
                                         breakout_signal, fibonacci_signal, volume_signal] 
                       if signal == "Bearish")
    
    # Determine overall signal
    if bullish_count > bearish_count + 1:  # Need at least 2 more bullish signals
        return "Bullish"
    elif bearish_count > bullish_count + 1:  # Need at least 2 more bearish signals
        return "Bearish"
    else:
        return "Neutral"



def load_currency_data(csv_file_path: str) -> pd.DataFrame:
    """
    Load and prepare currency data from CSV file
    
    Args:
        csv_file_path: Path to the CSV file
        
    Returns:
        DataFrame with datetime index and OHLCV data
    """
    df = pd.read_csv(csv_file_path)
    df['datetime'] = pd.to_datetime(df['datetime'])
    df.set_index('datetime', inplace=True)
    return df

def macd_strategy(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Literal["Bullish", "Bearish", "Neutral"]:
    """
    MACD (Moving Average Convergence Divergence) Strategy
    
    Args:
        df: DataFrame with OHLCV data
        fast: Fast EMA period (default: 12)
        slow: Slow EMA period (default: 26)
        signal: Signal line EMA period (default: 9)
        
    Returns:
        "Bullish", "Bearish", or "Neutral"
    """

    macd_data = ta.macd(df['close'], fast=fast, slow=slow, signal=signal)
    
    if macd_data is None or len(macd_data) < 2:
        return "Neutral"
    
    # Get latest values
    macd_line = macd_data[f'MACD_{fast}_{slow}_{signal}'].iloc[-1]
    signal_line = macd_data[f'MACDs_{fast}_{slow}_{signal}'].iloc[-1]
    histogram = macd_data[f'MACDh_{fast}_{slow}_{signal}'].iloc[-1]
    
    # Previous values for trend analysis
    prev_macd = macd_data[f'MACD_{fast}_{slow}_{signal}'].iloc[-2]
    prev_signal = macd_data[f'MACDs_{fast}_{slow}_{signal}'].iloc[-2]
    
    # Bullish signals
    if (macd_line > signal_line and prev_macd <= prev_signal) or (histogram > 0 and macd_line > 0):
        return "Bullish"
    # Bearish signals
    elif (macd_line < signal_line and prev_macd >= prev_signal) or (histogram < 0 and macd_line < 0):
        return "Bearish"
    else:
        return "Neutral"

def rsi_strategy(df: pd.DataFrame, period: int = 14, overbought: float = 70, oversold: float = 30) -> Literal["Bullish", "Bearish", "Neutral"]:
    """
    RSI (Relative Strength Index) Strategy
    
    Args:
        df: DataFrame with OHLCV data
        period: RSI calculation period (default: 14)
        overbought: Overbought threshold (default: 70)
        oversold: Oversold threshold (default: 30)
        
    Returns:
        "Bullish", "Bearish", or "Neutral"
    """
    rsi = ta.rsi(df['close'], length=period)
    
    if rsi is None or len(rsi) < 2:
        return "Neutral"
    
    current_rsi = rsi.iloc[-1]
    prev_rsi = rsi.iloc[-2]
    
    # Bullish: RSI moving up from oversold or breaking above 50
    if (current_rsi < oversold and current_rsi > prev_rsi) or (prev_rsi <= 50 and current_rsi > 50):
        return "Bullish"
    # Bearish: RSI moving down from overbought or breaking below 50
    elif (current_rsi > overbought and current_rsi < prev_rsi) or (prev_rsi >= 50 and current_rsi < 50):
        return "Bearish"
    else:
        return "Neutral"


def moving_average_crossover_strategy(df: pd.DataFrame, fast_period: int = 10, slow_period: int = 20) -> Literal["Bullish", "Bearish", "Neutral"]:
    """
    Moving Average Crossover Strategy
    
    Args:
        df: DataFrame with OHLCV data
        fast_period: Fast MA period (default: 10)
        slow_period: Slow MA period (default: 20)
        
    Returns:
        "Bullish", "Bearish", or "Neutral"
    """
    fast_ma = ta.sma(df['close'], length=fast_period)
    slow_ma = ta.sma(df['close'], length=slow_period)
    
    if fast_ma is None or slow_ma is None or len(fast_ma) < 2 or len(slow_ma) < 2:
        return "Neutral"
    
    current_fast = fast_ma.iloc[-1]
    current_slow = slow_ma.iloc[-1]
    prev_fast = fast_ma.iloc[-2]
    prev_slow = slow_ma.iloc[-2]
    
    # Bullish crossover: Fast MA crosses above Slow MA
    if prev_fast <= prev_slow and current_fast > current_slow:
        return "Bullish"
    # Bearish crossover: Fast MA crosses below Slow MA
    elif prev_fast >= prev_slow and current_fast < current_slow:
        return "Bearish"
    else:
        return "Neutral"

def stochastic_strategy(df: pd.DataFrame, k_period: int = 14, d_period: int = 3, overbought: float = 80, oversold: float = 20) -> Literal["Bullish", "Bearish", "Neutral"]:
    """
    Stochastic Oscillator Strategy
    
    Args:
        df: DataFrame with OHLCV data
        k_period: %K period (default: 14)
        d_period: %D period (default: 3)
        overbought: Overbought threshold (default: 80)
        oversold: Oversold threshold (default: 20)
        
    Returns:
        "Bullish", "Bearish", or "Neutral"
    """
    stoch = ta.stoch(df['high'], df['low'], df['close'], k=k_period, d=d_period)
    
    if stoch is None or len(stoch) < 2:
        return "Neutral"
    
    k_line = stoch[f'STOCHk_{k_period}_{d_period}_3'].iloc[-1]
    d_line = stoch[f'STOCHd_{k_period}_{d_period}_3'].iloc[-1]
    prev_k = stoch[f'STOCHk_{k_period}_{d_period}_3'].iloc[-2]
    prev_d = stoch[f'STOCHd_{k_period}_{d_period}_3'].iloc[-2]
    
    # Bullish: %K crosses above %D in oversold area or both lines rising from oversold
    if ((prev_k <= prev_d and k_line > d_line) and k_line < oversold * 1.5) or (k_line < oversold and k_line > prev_k):
        return "Bullish"
    # Bearish: %K crosses below %D in overbought area or both lines falling from overbought
    elif ((prev_k >= prev_d and k_line < d_line) and k_line > overbought * 0.8) or (k_line > overbought and k_line < prev_k):
        return "Bearish"
    else:
        return "Neutral"

def williams_r_strategy(df: pd.DataFrame, period: int = 14, overbought: float = -20, oversold: float = -80) -> Literal["Bullish", "Bearish", "Neutral"]:
    """
    Williams %R Strategy
    
    Args:
        df: DataFrame with OHLCV data
        period: Calculation period (default: 14)
        overbought: Overbought threshold (default: -20)
        oversold: Oversold threshold (default: -80)
        
    Returns:
        "Bullish", "Bearish", or "Neutral"
    """
    willr = ta.willr(df['high'], df['low'], df['close'], length=period)
    
    if willr is None or len(willr) < 2:
        return "Neutral"
    
    current_willr = willr.iloc[-1]
    prev_willr = willr.iloc[-2]
    
    # Bullish: Moving up from oversold territory
    if current_willr < oversold and current_willr > prev_willr:
        return "Bullish"
    # Bearish: Moving down from overbought territory
    elif current_willr > overbought and current_willr < prev_willr:
        return "Bearish"
    else:
        return "Neutral"

def cci_strategy(df: pd.DataFrame, period: int = 20, overbought: float = 100, oversold: float = -100) -> Literal["Bullish", "Bearish", "Neutral"]:
    """
    Commodity Channel Index (CCI) Strategy
    
    Args:
        df: DataFrame with OHLCV data
        period: CCI calculation period (default: 20)
        overbought: Overbought threshold (default: 100)
        oversold: Oversold threshold (default: -100)
        
    Returns:
        "Bullish", "Bearish", or "Neutral"
    """
    cci = ta.cci(df['high'], df['low'], df['close'], length=period)
    
    if cci is None or len(cci) < 2:
        return "Neutral"
    
    current_cci = cci.iloc[-1]
    prev_cci = cci.iloc[-2]
    
    # Bullish: CCI moving up from oversold or crossing above 0
    if (current_cci < oversold and current_cci > prev_cci) or (prev_cci <= 0 and current_cci > 0):
        return "Bullish"
    # Bearish: CCI moving down from overbought or crossing below 0
    elif (current_cci > overbought and current_cci < prev_cci) or (prev_cci >= 0 and current_cci < 0):
        return "Bearish"
    else:
        return "Neutral"

def adx_strategy(df: pd.DataFrame, period: int = 14, threshold: float = 25) -> Literal["Bullish", "Bearish", "Neutral"]:
    """
    Average Directional Index (ADX) Strategy
    
    Args:
        df: DataFrame with OHLCV data
        period: ADX calculation period (default: 14)
        threshold: Trend strength threshold (default: 25)
        
    Returns:
        "Bullish", "Bearish", or "Neutral"
    """
    adx_data = ta.adx(df['high'], df['low'], df['close'], length=period)
    
    if adx_data is None or len(adx_data) < 2:
        return "Neutral"
    
    adx_value = adx_data[f'ADX_{period}'].iloc[-1]
    plus_di = adx_data[f'DMP_{period}'].iloc[-1]
    minus_di = adx_data[f'DMN_{period}'].iloc[-1]
    
    # Strong trend required
    if adx_value > threshold:
        if plus_di > minus_di:
            return "Bullish"
        elif minus_di > plus_di:
            return "Bearish"
    
    return "Neutral"



def volume_strategy(df: pd.DataFrame, period: int = 20) -> Literal["Bullish", "Bearish", "Neutral"]:
    """
    Volume-based Strategy using Volume Moving Average
    
    Args:
        df: DataFrame with OHLCV data
        period: Volume MA period (default: 20)
        
    Returns:
        "Bullish", "Bearish", or "Neutral"
    """
    if 'volume' not in df.columns:
        return "Neutral"
    
    volume_ma = ta.sma(df['volume'], length=period)
    
    if volume_ma is None or len(volume_ma) < 2:
        return "Neutral"
    
    current_volume = df['volume'].iloc[-1]
    avg_volume = volume_ma.iloc[-1]
    current_price = df['close'].iloc[-1]
    prev_price = df['close'].iloc[-2]
    
    # High volume with price increase = Bullish
    if current_volume > avg_volume * 1.5 and current_price > prev_price:
        return "Bullish"
    # High volume with price decrease = Bearish
    elif current_volume > avg_volume * 1.5 and current_price < prev_price:
        return "Bearish"
    else:
        return "Neutral"
