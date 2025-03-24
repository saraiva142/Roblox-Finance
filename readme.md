# 📈 Média Móvel Take Profit

## 📌 Sobre o Projeto
Este é um **bot de trading automatizado** que utiliza médias móveis para **comprar e vender criptomoedas** na Binance, aplicando estratégias de **Take Profit** e **Stop Loss**. Ele analisa os preços a cada 15 minutos e toma decisões baseadas na média móvel rápida (7 períodos) e na média móvel lenta (40 períodos).

### 🚀 Como Funciona?
1. O bot verifica os preços da criptomoeda **SOL/BRL** na Binance.
2. Ele calcula duas médias móveis:
   - **Média rápida (7 períodos)**
   - **Média lenta (40 períodos)**
3. Se a média rápida **cruzar para cima** da média lenta, o bot realiza uma **compra**.
4. Após a compra, ele define automaticamente:
   - **Take Profit**: Venda quando atingir **0,75% de lucro**.
   - **Stop Loss**: Venda caso o preço caia **20% abaixo da compra**.
5. O bot continua monitorando até atingir uma dessas condições e então **vende a posição**.

---

## 🔧 Configuração e Instalação

### 1️⃣ Pré-requisitos
Antes de iniciar, você precisará de:
- **Conta na Binance** (para acessar a API)
- **Chave de API e Chave Secreta** da Binance
- **Python 3.8+** instalado
- **Bibliotecas necessárias**: `pandas`, `python-binance`

### 2️⃣ Instalando as Dependências
Abra o terminal e execute:
```bash
pip install pandas python-binance
```

### 3️⃣ Configuração da API Binance
Crie um arquivo `.env` na mesma pasta do script e adicione suas credenciais:
```env
KEY_BINANCE=suas_chave_aqui
SECRET_BINANCE=seu_segredo_aqui
```

### 4️⃣ Executando o Bot
Basta rodar o seguinte comando no terminal:
```bash
python media_movel_take_profit.py
```
O bot começará a rodar e verificará os preços a cada 15 minutos.

---

## ⚠️ Avisos Importantes
- Este bot **não garante lucros**. Faça testes antes de operar com dinheiro real.
- Certifique-se de **ter saldo suficiente** na conta da Binance.
- Ajuste os parâmetros de **Take Profit e Stop Loss** conforme sua estratégia.
- Recomenda-se rodar o bot em um **servidor ou computador ligado 24/7**.

---

## 🤝 Contribuição
Se quiser sugerir melhorias, sinta-se à vontade para abrir um **pull request** ou relatar problemas na aba de **issues**!

---

🚀 **Bons trades!** 📈💰

