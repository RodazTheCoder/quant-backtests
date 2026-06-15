"""
backtest/engine.py
------------------
Motor de backtest — executa qualquer estratégia sobre dados históricos e gera o relatório de performance.

Backtest simula o comportamento de uma estratégia no passado para avaliar sua viabilidade.
Não garante resultados futuros, mas é o método padrão de validação antes de operar com capital real.

Pontos críticos de integridade do backtest:
    - Look-ahead bias: uso acidental de dados futuros no cálculo de indicadores
    - Overfitting: parâmetros otimizados demais para um histórico específico, sem generalização
    - Custos de transação: taxas e spread devem ser contabilizados para evitar resultados inflados
"""

import pandas as pd
import matplotlib.pyplot as plt
from strategies.base import BaseStrategy
from risk.metrics import summary, print_summary, calculate_returns


class Backtest:

    def __init__(
        self,
        df: pd.DataFrame,
        strategy: BaseStrategy,
        initial_capital: float = 10_000.0,
        fee: float = 0.001,  # 0.1% por trade — padrão Binance
    ):
        self.df = df.copy()
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.fee = fee
        self.result = None

    def run(self) -> pd.DataFrame:
        """
        Executa o backtest e retorna o DataFrame com resultados.
        """
        print(f"\nRodando backtest: {self.strategy.name}")

        # 1. Gera os sinais da estratégia
        df = self.strategy.generate_signals(self.df)

        # 2. Calcula retornos do ativo
        df["market_return"] = df["close"].pct_change()

        # 3. Retorno da estratégia (considera posição e desconta taxa)
        df["strategy_return"] = (
            df["market_return"] * df["position"].shift(1).fillna(0)
            - self.fee * (df["signal"].abs())  # taxa nos trades
        )

        # 4. Patrimônio acumulado
        df["equity"] = self.initial_capital * (1 + df["strategy_return"]).cumprod()
        df["buy_hold"] = self.initial_capital * (1 + df["market_return"]).cumprod()

        self.result = df

        # 5. Imprime métricas
        metrics = summary(df, self.strategy.name)
        print_summary(metrics)

        return df

    def plot(self):
        """
        Gera 3 gráficos:
        1. Preço com as médias e sinais de compra/venda
        2. Patrimônio: estratégia vs buy & hold
        3. Drawdown ao longo do tempo
        """
        if self.result is None:
            print("Execute .run() antes de plotar.")
            return

        df = self.result
        fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
        fig.suptitle(f"Backtest — {self.strategy.name}", fontsize=14, fontweight="bold")

        # --- Gráfico 1: Preço + Médias + Sinais ---
        ax1 = axes[0]
        ax1.plot(df.index, df["close"], label="Preço", color="white", linewidth=1, alpha=0.8)
        for col in self.strategy.plot_columns:
            ax1.plot(df.index, df[col], label=col)

        # Sinais de compra (triângulo verde) e venda (triângulo vermelho)
        buys = df[df["signal"] == 1]
        sells = df[df["signal"] == -1]
        ax1.scatter(buys.index, buys["close"], marker="^", color="#00e676", s=80, zorder=5, label="Compra")
        ax1.scatter(sells.index, sells["close"], marker="v", color="#ff1744", s=80, zorder=5, label="Venda")

        ax1.set_ylabel("Preço (USDT)")
        ax1.legend(loc="upper left", fontsize=8)
        ax1.set_facecolor("white")

        # --- Gráfico 2: Patrimônio ---
        ax2 = axes[1]
        ax2.plot(df.index, df["equity"], label="Estratégia", color="#00e676", linewidth=1.5)
        ax2.plot(df.index, df["buy_hold"], label="Buy & Hold", color="#4fc3f7", linewidth=1.5, linestyle="--")
        ax2.axhline(self.initial_capital, color="gray", linewidth=0.5, linestyle=":")
        ax2.set_ylabel("Patrimônio (USDT)")
        ax2.legend(loc="upper left", fontsize=8)
        ax2.set_facecolor("white")

        # --- Gráfico 3: Drawdown ---
        ax3 = axes[2]
        cumulative = (1 + df["strategy_return"].fillna(0)).cumprod()
        peak = cumulative.cummax()
        drawdown = (cumulative - peak) / peak
        ax3.fill_between(df.index, drawdown, 0, color="#ff1744", alpha=0.4, label="Drawdown")
        ax3.set_ylabel("Drawdown")
        ax3.set_xlabel("Data")
        ax3.legend(loc="lower left", fontsize=8)
        ax3.set_facecolor("white")

        fig.patch.set_facecolor("white")
        plt.tight_layout()
        plt.savefig("backtest_result.png", dpi=150, bbox_inches="tight")
        plt.show()
        print("\n✓ Gráfico salvo em backtest_result.png")
