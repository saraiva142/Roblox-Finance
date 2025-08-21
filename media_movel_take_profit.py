import pandas as pd
import os
import time
from binance.client import Client
from binance.enums import *
from dotenv import load_dotenv  # <-- 1. Importe a biblioteca

load_dotenv()  # <-- 2. Carregue as variáveis do arquivo .env

# Configuração da API
api_key = os.getenv("KEY_BINANCE")
secret_key = os.getenv("SECRET_BINANCE")
cliente_binance = Client(api_key, secret_key)

# Parâmetros do ativo
codigo_operado = "SOLBRL"
ativo_operado = "SOL"
periodo_candle = Client.KLINE_INTERVAL_15MINUTE  # Alterado para 15 minutos
valor_operacao = 550  # Valor fixo de compra em reais
quantidade_comprada = 0  # Armazena a quantidade comprada para vender apenas essa parte

# Variáveis de controle para Take Profit e Stop Loss
preco_compra = None  
take_profit = None
stop_loss = None
posicao = False  

def pegando_dados(codigo, intervalo):
    candles = cliente_binance.get_klines(symbol=codigo, interval=intervalo, limit=100)
    precos = pd.DataFrame(candles)

    precos.columns = ["tempo_abertura", "abertura", "maxima", "minima", "fechamento", "volume", "tempo_fechamento",
                      "moedas_negociadas", "numero_trades", "volume_ativo_base_compra", "volume_ativo_cotação", "-"]

    precos = precos[["fechamento", "tempo_fechamento"]]
    precos["fechamento"] = precos["fechamento"].astype(float)

    precos["tempo_fechamento"] = pd.to_datetime(precos["tempo_fechamento"], unit="ms").dt.tz_localize("UTC")
    precos["tempo_fechamento"] = precos["tempo_fechamento"].dt.tz_convert("America/Sao_Paulo")

    return precos

def estrategia_trade(dados, codigo_ativo, ativo_operado, valor_operacao):
    global preco_compra, take_profit, stop_loss, posicao, quantidade_comprada

    # Calculando médias móveis
    dados["media_rapida"] = dados["fechamento"].rolling(window=7).mean()
    dados["media_devagar"] = dados["fechamento"].rolling(window=40).mean()

    ultima_media_rapida = dados["media_rapida"].iloc[-1]
    ultima_media_devagar = dados["media_devagar"].iloc[-1]
    preco_atual = float(dados["fechamento"].iloc[-1])

    print(f"📊 Média Rápida: {ultima_media_rapida:.2f} | Média Devagar: {ultima_media_devagar:.2f} | Preço Atual: {preco_atual:.2f}")

    # Se já temos uma posição aberta, verificamos Take Profit e Stop Loss
    if posicao:
        if preco_atual >= take_profit:
            order = cliente_binance.create_order(
                symbol=codigo_ativo,
                side=SIDE_SELL,
                type=ORDER_TYPE_MARKET,
                quantity=quantidade_comprada  # Apenas a quantidade comprada
            )
            print(f"🎯 TAKE PROFIT atingido! Vendeu {quantidade_comprada} {ativo_operado} a {preco_atual}")
            posicao = False
            preco_compra = None  
            quantidade_comprada = 0  

        elif preco_atual <= stop_loss:
            order = cliente_binance.create_order(
                symbol=codigo_ativo,
                side=SIDE_SELL,
                type=ORDER_TYPE_MARKET,
                quantity=quantidade_comprada  # Apenas a quantidade comprada
            )
            print(f"🚨 STOP LOSS atingido! Vendeu {quantidade_comprada} {ativo_operado} a {preco_atual}")
            posicao = False
            preco_compra = None  
            quantidade_comprada = 0  

        return  

    # Estratégia de Compra (cruzamento de médias)
    if ultima_media_rapida > ultima_media_devagar and not posicao:
        quantidade = round(valor_operacao / preco_atual, 3)  # Calcula a quantidade com base em R$ 550
        order = cliente_binance.create_order(
            symbol=codigo_ativo,
            side=SIDE_BUY,
            type=ORDER_TYPE_MARKET,
            quantity=quantidade
        )

        preco_compra = preco_atual
        quantidade_comprada = quantidade  # Armazena a quantidade comprada para venda futura
        take_profit = preco_compra * 1.0075  
        stop_loss = preco_compra * 0.80  # Stop Loss de -20% 

        posicao = True

        print(f"📈 COMPRA feita: {quantidade} {ativo_operado} a {preco_compra:.2f}, Take Profit: {take_profit:.2f}, Stop Loss: {stop_loss:.2f}")

# Loop infinito para verificar a estratégia a cada 15 minutos
while True:
    dados_atualizados = pegando_dados(codigo=codigo_operado, intervalo=periodo_candle)
    estrategia_trade(dados_atualizados, codigo_operado, ativo_operado, valor_operacao)
    time.sleep(15 * 60)  # Aguarda 15 minutos
