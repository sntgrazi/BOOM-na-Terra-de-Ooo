# 💣 Bomberman Clone - Adventure Time Edition

Um clone completo do clássico jogo Bomberman, implementado em Python usando Pygame, com personagens do Adventure Time!

## 🎮 Como Jogar

### Controles
- **WASD** ou **Setas direcionais**: Mover o jogador
- **ESPAÇO**: Colocar bomba
- **P**: Pausar/Despausar o jogo
- **M**: Ativar/Desativar som
- **ESC**: Voltar ao menu

### Personagens Jogáveis
- **Finn**: O aventureiro corajoso
- **Jake**: O cachorro mágico
- **Marceline**: A rainha vampira
- **Princesa Jujuba**: A governante do Reino Doce

### Objetivo
- Eliminar todos os inimigos para avançar para o próximo nível
- Evite ser atingido por explosões ou inimigos
- Colete power-ups para melhorar suas habilidades
- Sobreviva com suas 3 vidas

### Power-ups
- **💣 Bomba Azul**: Aumenta o número máximo de bombas
- **🔥 Chama Laranja**: Aumenta o alcance da explosão
- **⚡ Raio Verde**: Aumenta a velocidade do jogador

## 🚀 Como Executar

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes do Python)

### Instalação Automática (Windows)
1. Execute o arquivo `install_and_run.bat`
2. O script irá verificar e instalar as dependências automaticamente

### Instalação Automática (Linux/Mac)
1. Execute o arquivo `install_and_run.sh`
2. O script irá verificar e instalar as dependências automaticamente

### Instalação Manual
1. Instale as dependências:
   ```bash
   pip install pygame numpy
   ```
2. Execute o jogo:
   ```bash
   python main.py
   ```

## 📁 Estrutura do Projeto

```
jogo/
├── main.py                 # Arquivo principal
├── requirements.txt        # Dependências Python
├── install_and_run.bat    # Script de instalação (Windows)
├── install_and_run.sh     # Script de instalação (Linux/Mac)
├── game/                  # Módulo principal do jogo
│   ├── __init__.py
│   ├── constants.py       # Constantes do jogo
│   ├── bomberman_game.py  # Classe principal
│   ├── entities.py        # Jogador, inimigos, bombas
│   ├── game_map.py        # Sistema de mapa
│   ├── sprites.py         # Sistema de sprites
│   ├── audio.py           # Sistema de áudio
│   └── ui.py             # Interface do usuário
├── images/               # Sprites dos personagens
│   ├── Finn-frame1.png
│   ├── jake-frame1.png
│   ├── marceline-frame1.png
│   └── princesa-frame1.png
└── README.md             # Este arquivo
```

## 🛠️ Tecnologias Utilizadas

- **Python 3.8+**: Linguagem principal
- **Pygame 2.5+**: Engine de jogo e renderização gráfica
- **NumPy**: Geração de áudio procedural
- **Sistema de Sprites Híbrido**: Suporte a imagens PNG/JPG + fallback desenhado
- **Arquitetura Modular**: Código organizado em módulos

## ✨ Características Implementadas

### Funcionalidades Principais
- ✅ **4 Personagens Jogáveis**: Finn, Jake, Marceline e Princesa Jujuba
- ✅ **IA Inteligente**: Inimigos com comportamento avançado (explorar, atacar, fugir)
- ✅ **Sistema de Bombas**: Bombas com sistema "fantasma" para evitar travamento
- ✅ **Detecção de Colisões**: Sistema preciso de colisões
- ✅ **Sistema de Vidas**: 3 vidas por jogador

### Interface e Experiência
- ✅ **Menus Completos**: Tela inicial, seleção de personagem, configurações
- ✅ **HUD Informativo**: Vidas, pontuação, nível, power-ups
- ✅ **Telas de Estado**: Game over, vitória, pausa
- ✅ **Controles Intuitivos**: WASD/Setas + teclas especiais

### Sistema de Áudio
- ✅ **Trilha Sonora**: Música de fundo dinâmica
- ✅ **Efeitos Sonoros**: Bomba, explosão, power-up, movimento
- ✅ **Controle de Áudio**: Mute/unmute com tecla M
- ✅ **Geração Procedural**: Sons criados com NumPy

### Power-ups e Progressão
- ✅ **Power-ups Coletáveis**: Bombas, alcance e velocidade
- ✅ **Múltiplos Níveis**: Dificuldade progressiva
- ✅ **Sistema de Pontuação**: Pontos por ações e bônus de nível
- ✅ **Progressão Salvada**: Continua do último nível

## 🎯 Objetivos Acadêmicos Atendidos

1. **Protótipo Jogável**: ✅ Jogo completamente funcional
2. **Interface Completa**: ✅ Telas de abertura, jogo e game over
3. **Trilha Sonora**: ✅ Música de fundo e efeitos sonoros
4. **Power-ups**: ✅ Sistema de melhorias coletáveis
5. **Múltiplos Níveis**: ✅ Progressão com dificuldade crescente
6. **Pontuação**: ✅ Sistema completo de scoring

## 🤖 IA dos Inimigos

- **Modo Explorar**: Movimentação aleatória nos primeiros segundos
- **Modo Atacar**: Se aproxima do jogador e coloca bombas estrategicamente  
- **Modo Fugir**: Foge de bombas próximas e do jogador quando muito perto
- **Sistema de Bombas**: Inimigos colocam bombas inteligentemente
- **Rotas de Escape**: IA verifica rotas seguras antes de colocar bombas

## 🔧 Personalização

### Modificar Configurações
Edite o arquivo `game/constants.py` para ajustar:
- Velocidades do jogador e inimigos
- Tempo das bombas
- Tamanho do mapa
- Cores e outros parâmetros

### Adicionar Sprites
1. Coloque imagens PNG na pasta `images/`
2. Modifique `game/sprites.py` para carregar as novas imagens
3. As imagens devem ter 40x40 pixels para melhor resultado

## 🐛 Solução de Problemas

### Python não encontrado
```bash
# Instale Python em: https://python.org/downloads
# Marque "Add Python to PATH" durante a instalação
```

### Erro "No module named 'pygame'"
```bash
pip install pygame numpy
```

### Jogo muito lento
- Reduza o FPS em `constants.py`
- Use um computador com melhor performance

### Sem áudio
- Verifique se pygame.mixer foi inicializado corretamente
- Pressione 'M' para verificar se não está mutado

## 📝 Créditos

- **Desenvolvimento**: Implementação completa em Python com Pygame
- **Personagens**: Baseados na série Adventure Time
- **Áudio**: Geração procedural de sons com NumPy
- **Sprites**: Sistema híbrido (imagens + desenhos)
- **Inspiração**: Baseado no clássico jogo Bomberman da Hudson Soft

---

**Versão Python**: 1.0  
**Tecnologia**: Python + Pygame + NumPy  
**Licença**: Uso Acadêmico
