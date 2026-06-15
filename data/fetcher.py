"""
data/fetcher.py
---------------
Responsável por buscar dados de mercado.
Usa ccxt — mesma interface para 100+ exchanges (Binance, Kraken, etc.)

Como usar:
    from data.fetcher import fetch_ohlcv
    df = fetch_ohlcv("BTC/USDT", timeframe="1d", limit=365)
"""

import ccxt
import pandas as pd


def fetch_ohlcv(
    symbol: str,
    timeframe: str = "1d",
    limit: int = 500,
    exchange_id: str = "binance",
) -> pd.DataFrame:
    """
    Busca dados OHLCV (Open, High, Low, Close, Volume) de uma exchange.

    Parâmetros:
        symbol      → par de trading, ex: "BTC/USDT", "ETH/USDT"
        timeframe   → "1m", "5m", "1h", "4h", "1d", "1w"
        limit       → quantas candles buscar (máx depende da exchange)
        exchange_id → "binance", "kraken", "coinbase", etc.

    Retorna:
        DataFrame com colunas: open, high, low, close, volume
        Index: datetime (UTC)
    """
    # Inicializa a exchange — sem API key para dados públicos
    exchange_class = getattr(ccxt, exchange_id)
    exchange = exchange_class()

    # Busca os dados
    print(f"Buscando {limit} candles de {symbol} ({timeframe}) na {exchange_id}...")
    raw = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

    # Converte para DataFrame
    df = pd.DataFrame(raw, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df.set_index("timestamp", inplace=True)

    print(f"✓ {len(df)} candles carregadas | {df.index[0].date()} → {df.index[-1].date()}")
    return df


def fetch_multiple(
    symbols: list[str],
    timeframe: str = "1d",
    limit: int = 500,
    exchange_id: str = "binance",
) -> dict[str, pd.DataFrame]:
    """
    Busca dados para múltiplos ativos de uma vez.
    Retorna um dicionário: { "BTC/USDT": df, "ETH/USDT": df, ... }

    Útil para portfolio com Markowitz.
    """
    data = {}
    for symbol in symbols:
        try:
            data[symbol] = fetch_ohlcv(symbol, timeframe, limit, exchange_id)
        except Exception as e:
            print(f"✗ Erro ao buscar {symbol}: {e}")
    return data
