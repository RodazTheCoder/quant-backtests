"""
strategies/ema_cross.py
-----------------------
Estratégia de cruzamento de médias móveis exponenciais (EMA Crossover).

Lógica:
    - Calcula duas médias móveis: rápida (ex: 20 períodos) e lenta (ex: 50)
    - Quando a rápida CRUZA PRA CIMA a lenta  → sinal de COMPRA  (1)
    - Quando a rápida CRUZA PRA BAIXO a lenta → sinal de VENDA  (-1)
    - Enquanto não cruza                       → sem posição      (0)

Funciona bem em mercados com tendências claras e tende a gerar sinais falsos
em mercados laterais (chop), o que impacta negativamente o resultado.
"""

import pandas as pd
from strategies.base import BaseStrategy


class EMACross(BaseStrategy):

    def __init__(self, fast: int = 20, slow: int = 50):
        """
        fast → períodos da média rápida (padrão: 20)
        slow → períodos da média lenta  (padrão: 50)
        """
        super().__init__(name=f"EMA({fast},{slow})")
        self.fast = fast
        self.slow = slow
        self.plot_columns = ["ema_fast", "ema_slow"]


    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Calcula as médias móveis
        df["ema_fast"] = df["close"].ewm(span=self.fast, adjust=False).mean()
        df["ema_slow"] = df["close"].ewm(span=self.slow, adjust=False).mean()

        # Posição: 1 quando rápida > lenta, -1 quando rápida < lenta
        df["position"] = 0
        df.loc[df["ema_fast"] > df["ema_slow"], "position"] = 1
        df.loc[df["ema_fast"] < df["ema_slow"], "position"] = -1

        # Sinal: só nos momentos de MUDANÇA de posição (o cruzamento em si)
        # shift(1) pega o valor anterior — se mudou, é um cruzamento
        df["signal"] = 0
        df.loc[
            (df["position"] == 1) & (df["position"].shift(1) != 1), "signal"
        ] = 1   # cruzou pra cima → compra
        df.loc[
            (df["position"] == -1) & (df["position"].shift(1) != -1), "signal"
        ] = -1  # cruzou pra baixo → venda

        return df
