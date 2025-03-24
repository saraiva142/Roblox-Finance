import pandas as pd
import os
import time
from binance.client import Client
from binance.enums import *

# Configurações iniciais
api_key = os.getenv("KEY_BINANCE")
secret_key = os.getenv("SECRET_BINANCE")

cliente_binance = Client(api_key, secret_key)

codigo_operado = "SOLBRL"
ativo_operado = "SOL"
periodo_candle = Client.KLINE_INTERVAL_15MINUTE  # Análise a cada 15 minutos
quantidade = 0.015  # Quantidade de SOL a ser operada

# Parâmetros de stop-loss e take-profit (em porcentagem)
stop_loss_percent = 1.0  # 1% de stop-loss
take_profit_percent = 3.0  # 2% de take-profit

# Função para pegar os últimos candles
def pegando_dados(codigo, intervalo):
    candles = cliente_binance.get_klines(symbol=codigo, interval=intervalo, limit=50)  # Pegando os últimos 50 candles
    precos = pd.DataFrame(candles)
    
    precos.columns = ["tempo_abertura", "abertura", "maxima", "minima", "fechamento", "volume", "tempo_fechamento", "moedas_negociadas", "numero_trades",
                      "volume_ativo_base_compra", "volume_ativo_cotacao", "-"]
    
    precos = precos[["fechamento", "maxima", "minima", "tempo_fechamento"]]
    precos["fechamento"] = precos["fechamento"].astype(float)
    precos["maxima"] = precos["maxima"].astype(float)
    precos["minima"] = precos["minima"].astype(float)
    
    precos["tempo_fechamento"] = pd.to_datetime(precos["tempo_fechamento"], unit="ms").dt.tz_localize("UTC")
    precos["tempo_fechamento"] = precos["tempo_fechamento"].dt.tz_convert("America/Sao_Paulo")
    
    return precos

# Estratégia Breakout com Stop-Loss e Take-Profit
def estrategia_breakout_com_gestao(dados, codigo_ativo, ativo_operado, quantidade, posicao, preco_entrada):
    resistencia = max(dados["maxima"].iloc[-10:])  # Pega a maior máxima dos últimos 10 candles
    suporte = min(dados["minima"].iloc[-10:])  # Pega a menor mínima dos últimos 10 candles
    preco_atual = dados["fechamento"].iloc[-1]  # Último preço de fechamento
    
    print(f"Preço Atual: {preco_atual} | Resistência: {resistencia} | Suporte: {suporte}")
    
    conta = cliente_binance.get_account()
    
    for ativo in conta["balances"]:
        if ativo["asset"] == ativo_operado:
            quantidade_atual = float(ativo["free"])
    
    # Se não estiver em uma posição, verifica se deve comprar
    if not posicao:
        if preco_atual > resistencia:
            # Confirmação de breakout: espera o candle fechar acima da resistência
            if dados["fechamento"].iloc[-2] <= resistencia and preco_atual > resistencia:
                order = cliente_binance.create_order(
                    symbol=codigo_ativo,
                    side=SIDE_BUY,
                    type=ORDER_TYPE_MARKET,
                    quantity=quantidade
                )
                print("💰 COMPROU no breakout da resistência!")
                posicao = True
                preco_entrada = preco_atual  # Define o preço de entrada para cálculo de stop-loss e take-profit
    
    # Se estiver em uma posição, verifica stop-loss e take-profit
    else:
        # Calcula os níveis de stop-loss e take-profit
        stop_loss = preco_entrada * (1 - stop_loss_percent / 100)
        take_profit = preco_entrada * (1 + take_profit_percent / 100)
        
        print(f"Preço Entrada: {preco_entrada} | Stop-Loss: {stop_loss} | Take-Profit: {take_profit}")
        
        # Verifica se o preço atingiu o stop-loss ou take-profit
        if preco_atual <= stop_loss or preco_atual >= take_profit:
            order = cliente_binance.create_order(
                symbol=codigo_ativo,
                side=SIDE_SELL,
                type=ORDER_TYPE_MARKET,
                quantity=int(quantidade_atual * 1000) / 1000
            )
            print(f"📉 VENDEU! Motivo: {'Stop-Loss' if preco_atual <= stop_loss else 'Take-Profit'}")
            posicao = False
            preco_entrada = None  # Reseta o preço de entrada
    
    return posicao, preco_entrada

# Loop principal
posicao_atual = False
preco_entrada = None

while True:
    dados_atualizados = pegando_dados(codigo=codigo_operado, intervalo=periodo_candle)
    posicao_atual, preco_entrada = estrategia_breakout_com_gestao(
        dados_atualizados, codigo_ativo=codigo_operado, 
        ativo_operado=ativo_operado, quantidade=quantidade, 
        posicao=posicao_atual, preco_entrada=preco_entrada
    )
    time.sleep(60 * 15)  # Aguarda 15 minutos para a próxima análise