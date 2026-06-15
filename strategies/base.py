"""
strategies/base.py
------------------
Classe base para todas as estratégias.

Todas as estratégias herdam de BaseStrategy, garantindo que o backtest engine
consiga executar qualquer uma delas por meio de uma interface comum (.generate_signals()).

Exemplo de implementação:
    from strategies.base import BaseStrategy

    class MinhaEstrategia(BaseStrategy):
        def generate_signals(self, df):
            # retorna df com coluna "signal": 1 (compra), -1 (venda), 0 (neutro)
            return df
"""

from abc import ABC, abstractmethod
import pandas as pd


class BaseStrategy(ABC):
    """
    Classe abstrata — define a interface padrão de toda estratégia.
    Não deve ser instanciada diretamente; deve ser herdada por estratégias concretas.
    """

    def __init__(self, name: str):
        self.name = name
        self.plot_columns = []  # Colunas adicionais para plotar (além de 'close')

    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Recebe OHLCV, retorna o mesmo DataFrame com coluna 'signal':
            1  → sinal de compra (long)
           -1  → sinal de venda (short ou saída)
            0  → sem posição
        """
        pass

    def __repr__(self):
        return f"Strategy({self.name})"
