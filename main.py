"""
main.py
-------
Ponto de entrada da aplicação. Orquestra a busca de dados, definição de estratégia,
execução do backtest e geração dos gráficos.

Uso:
    python main.py

Parâmetros configuráveis:
    - symbol: par de trading (ex: "ETH/USDT", "SOL/USDT")
    - timeframe: granularidade das candles (ex: "4h", "1h", "1w")
    - fast/slow: períodos das médias móveis
"""

from data.fetcher import fetch_ohlcv
from strategies.ema_cross import EMACross
from strategies.sma_cross import SMACross
from backtest.engine import Backtest


def main():
    # ── 1. Buscar dados ──────────────────────────────────────────────────
    df = fetch_ohlcv(
        symbol="BTC/USDT",
        timeframe="1d",   # candles diárias
        limit=500,        # ~500 dias de histórico
    )

    # ── 2. Definir estratégia ────────────────────────────────────────────
    strategy = EMACross(fast=20, slow=50)

    # ── 3. Rodar backtest ────────────────────────────────────────────────
    bt = Backtest(
        df=df,
        strategy=strategy,
        initial_capital=100,  # USDT simulado
        fee=0.001,               # 0.1% por trade (padrão Binance)
    )

    result = bt.run()

    # ── 4. Visualizar ────────────────────────────────────────────────────
    bt.plot()


if __name__ == "__main__":
    main()
