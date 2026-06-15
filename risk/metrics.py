"""
risk/metrics.py
---------------
Métricas de performance e risco de uma estratégia.

Retorno positivo isolado não é suficiente para avaliar uma estratégia —
é necessário medir o risco assumido para gerá-lo. As métricas aqui implementadas
são o padrão da indústria para avaliação quantitativa de estratégias.
"""

import numpy as np
import pandas as pd


def calculate_returns(df: pd.DataFrame) -> pd.Series:
    """
    Retornos diários do preço de fechamento.
    Ex: se fechou 100 ontem e 105 hoje → retorno = 5%
    """
    return df["close"].pct_change().dropna()


def sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0, periods: int = 365) -> float:
    """
    Sharpe Ratio: retorno ajustado pelo risco.

    Fórmula: (retorno_médio - taxa_livre_risco) / desvio_padrão * √períodos

    Interpretação:
        < 0    → estratégia pior que ficar em caixa
        0–1    → aceitável
        1–2    → bom
        > 2    → excelente (raro no mundo real)

    periods = 365 para cripto (mercado 24/7), 252 para ações
    """
    excess = returns - risk_free_rate / periods
    if returns.std() == 0:
        return 0.0
    return float((excess.mean() / returns.std()) * np.sqrt(periods))


def max_drawdown(returns: pd.Series) -> float:
    """
    Max Drawdown: maior queda do pico ao vale.

    Ex: -0.45 significa que a estratégia caiu 45% do seu pico máximo em algum momento.
    É a métrica de risco mais importante na prática — mostra o pior cenário real.
    """
    cumulative = (1 + returns).cumprod()
    peak = cumulative.cummax()
    drawdown = (cumulative - peak) / peak
    return float(drawdown.min())


def win_rate(signals: pd.Series, returns: pd.Series) -> float:
    """
    Percentual de trades com retorno positivo.
    """
    trade_returns = returns[signals != 0]
    if len(trade_returns) == 0:
        return 0.0
    return float((trade_returns > 0).sum() / len(trade_returns))


def total_return(returns: pd.Series) -> float:
    """
    Retorno total acumulado do período.
    """
    return float((1 + returns).prod() - 1)


def summary(df: pd.DataFrame, strategy_name: str = "Estratégia") -> dict:
    """
    Gera um resumo completo de performance.
    Recebe o DataFrame com a coluna 'signal' gerada pela estratégia.
    """
    returns = calculate_returns(df)

    # Retorno da estratégia: só conta quando há posição
    strategy_returns = returns * df["position"].shift(1).fillna(0)

    metrics = {
        "Estratégia":       strategy_name,
        "Período":          f"{df.index[0].date()} → {df.index[-1].date()}",
        "Total Return":     f"{total_return(strategy_returns):.2%}",
        "Buy & Hold":       f"{total_return(returns):.2%}",
        "Sharpe Ratio":     f"{sharpe_ratio(strategy_returns):.2f}",
        "Max Drawdown":     f"{max_drawdown(strategy_returns):.2%}",
        "Win Rate":         f"{win_rate(df['signal'], strategy_returns):.2%}",
        "Nº de Trades":     int((df["signal"] != 0).sum()),
    }

    return metrics


def print_summary(metrics: dict):
    print("\n" + "=" * 40)
    for k, v in metrics.items():
        print(f"  {k:<18} {v}")
    print("=" * 40)
