# 💥 BOOM na Terra de Ooo

Bem-vindo à Terra de Ooo! Junte-se a Finn, Jake e outros heróis em uma aventura explosiva cheia de ação e estratégia. Coloque bombas, derrote inimigos e explore os reinos mágicos neste jogo inspirado no clássico Bomberman, mas com todo o charme e diversão do Adventure Time!

## 🌟 O que é BOOM na Terra de Ooo?

BOOM na Terra de Ooo é um jogo de ação e estratégia onde você controla seus personagens favoritos do Adventure Time em batalhas explosivas. Navegue pelos diferentes reinos, use bombas estrategicamente para derrotar inimigos e colete power-ups para se tornar ainda mais poderoso!

## 🎮 Como Jogar

### Controles
- **WASD** ou **Setas direcionais**: Mover o personagem
- **ESPAÇO**: Colocar bomba
- **P**: Pausar/Despausar o jogo
- **M**: Ativar/Desativar som
- **ESC**: Voltar ao menu

### Heróis da Terra de Ooo
- **🗡️ Finn**: O aventureiro corajoso com seu chapéu de urso
- **🐕 Jake**: O cachorro mágico que pode se transformar
- **🧛‍♀️ Marceline**: A rainha vampira com poderes sombrios
- **👑 Princesa Jujuba**: A governante científica do Reino Doce
- **🔥 Princesa Chama**: A poderosa governante do Reino do Fogo
- **🍬 Princesa Jellybean**: A doce princesa colorida

### Objetivo da Aventura
- 💀 Elimine todos os inimigos para avançar para o próximo reino
- 💥 Use bombas estrategicamente para quebrar obstáculos
- ⚡ Evite explosões e inimigos perigosos
- 🎁 Colete power-ups mágicos para aumentar seus poderes
- ❤️ Sobreviva com suas 3 vidas preciosas

### Power-ups Mágicos
- **💣 Bomba Extra**: Permite carregar mais bombas ao mesmo tempo
- **🔥 Poder do Fogo**: Aumenta o alcance explosivo das suas bombas
- **⚡ Velocidade**: Torna seu personagem mais rápido e ágil

## 🚀 Como Começar Sua Aventura

### 💻 Opção 1: Executável Windows (Recomendado)
**A maneira mais fácil de jogar!**

1. **Gerar o executável:**
   - Execute o arquivo `build_executable.bat`
   - Aguarde o processo de build (pode demorar alguns minutos)

2. **Jogar:**
   - Vá para a pasta `dist\BOOM na Terra de Ooo\`
   - Execute `BOOM na Terra de Ooo.exe`
   - Pronto! Seu jogo está rodando! 🎮

**Vantagens do executável:**
- ✅ Não precisa instalar Python
- ✅ Funciona em qualquer PC Windows
- ✅ Pode ser copiado para outros computadores
- ✅ Inicialização mais rápida

### 🐍 Opção 2: Executar com Python

#### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes do Python)

#### Instalação Rápida (Windows)
1. Execute o arquivo `install_and_run.bat`
2. O script instalará tudo automaticamente e iniciará o jogo!

#### Instalação Rápida (Linux/Mac)
1. Execute o arquivo `install_and_run.sh`
2. O script instalará tudo automaticamente e iniciará o jogo!

#### Instalação Manual
1. Instale as dependências mágicas:
   ```bash
   pip install -r requirements.txt
   ```
2. Inicie sua aventura:
   ```bash
   python main.py
   ```

## 🗺️ Explorando os Reinos

O jogo inclui diferentes temas baseados nos reinos do Adventure Time:

- **🌿 Reino de Ooo**: O reino principal com suas paisagens verdes
- **🍭 Reino Doce**: O colorido reino da Princesa Jujuba
- **🔥 Reino do Fogo**: O ardente domínio da Princesa Chama

## 📁 Estrutura da Aventura

```
boom-terra-de-ooo/
├── main.py                 # Portal principal para a Terra de Ooo
├── requirements.txt        # Ingredientes mágicos necessários
├── install_and_run.bat    # Script de aventura (Windows)
├── install_and_run.sh     # Script de aventura (Linux/Mac)
├── game/                  # Módulo principal da aventura
│   ├── __init__.py
│   ├── constants.py       # Regras da Terra de Ooo
│   ├── bomberman_game.py  # Motor da aventura
│   ├── entities.py        # Heróis, vilões e bombas
│   ├── game_map.py        # Mapas dos reinos
│   ├── sprites.py         # Aparência dos personagens
│   ├── audio.py           # Sons da aventura
│   └── ui.py             # Interface mágica
├── images/               # Retratos dos heróis
│   ├── finn_idle.png
│   ├── jake_idle_down.png
│   ├── marceline_idle_down.png
│   └── [outros sprites...]
├── sounds/               # Efeitos sonoros
└── README.md             # Este pergaminho
```

## 🛠️ Tecnologias Mágicas Utilizadas

- **Python 3.8+**: A linguagem principal desta aventura
- **Pygame 2.5+**: Motor gráfico para renderizar a Terra de Ooo
- **NumPy**: Geração de efeitos sonoros mágicos
- **Sistema Híbrido de Sprites**: Suporte a imagens + desenhos automáticos
- **Arquitetura Modular**: Código organizado como os reinos de Ooo

## ✨ Aventuras Implementadas

### Funcionalidades Principais
- ✅ **6 Heróis Jogáveis**: Finn, Jake, Marceline, Princesa Jujuba, Princesa Chama e Princesa Jellybean
- ✅ **IA Inteligente**: Inimigos com comportamentos únicos (explorar, atacar, fugir)
- ✅ **Sistema de Bombas Estratégico**: Bombas inteligentes que não te prendem
- ✅ **Detecção Precisa**: Sistema avançado de colisões
- ✅ **Sistema de Vidas**: 3 chances para completar sua missão

### Interface da Aventura
- ✅ **Menus Épicos**: Tela de início, seleção de herói, configurações
- ✅ **HUD Informativo**: Vidas, pontuação, reino atual, power-ups ativos
- ✅ **Telas de Estado**: Derrota, vitória, pausa
- ✅ **Controles Intuitivos**: Fácil de aprender, difícil de dominar

### Trilha Sonora da Terra de Ooo
- ✅ **Música Ambiente**: Trilhas que combinam com cada reino
- ✅ **Efeitos Sonoros**: Explosões, power-ups, movimentos
- ✅ **Controle de Áudio**: Silenciar/ativar som com a tecla M
- ✅ **Sons Procedurais**: Efeitos únicos gerados matematicamente

### Progressão e Power-ups
- ✅ **Power-ups Coletáveis**: Melhore suas habilidades de combate
- ✅ **Múltiplos Reinos**: Cada nível com desafios únicos
- ✅ **Sistema de Pontuação**: Ganhe pontos por estratégia e habilidade
- ✅ **Progressão Contínua**: Continue de onde parou

## 🎯 Missões Acadêmicas Completadas

1. **Protótipo Jogável**: ✅ Aventura completamente funcional
2. **Interface Completa**: ✅ Todas as telas necessárias implementadas
3. **Trilha Sonora**: ✅ Áudio imersivo e efeitos sonoros
4. **Power-ups**: ✅ Sistema de melhorias estratégicas
5. **Múltiplos Níveis**: ✅ Progressão através dos reinos
6. **Pontuação**: ✅ Sistema completo de scoring e ranking

## 🤖 Inteligência dos Vilões

Os inimigos na Terra de Ooo possuem IA avançada:

- **🔍 Modo Exploração**: Patrulham o território procurando por heróis
- **⚔️ Modo Ataque**: Perseguem heróis e colocam bombas estrategicamente  
- **🏃 Modo Fuga**: Fogem de explosões e situações perigosas
- **🧠 Estratégia de Bombas**: Calculam rotas de escape antes de atacar
- **🛡️ Autopreservação**: Priorizam sobrevivência em situações críticas

## 🔧 Personalizações Avançadas

### Modificar Configurações dos Reinos
Edite `game/constants.py` para personalizar:
- Velocidades dos heróis e vilões
- Tempo de explosão das bombas
- Tamanho dos mapas dos reinos
- Cores e efeitos visuais

### Adicionar Novos Heróis
1. Adicione sprites PNG na pasta `images/`
2. Configure em `game/sprites.py`
3. Recomendado: sprites de 40x40 pixels para melhor qualidade

## 🐛 Solução de Problemas na Aventura

### Python não encontrado
```bash
# Baixe Python em: https://python.org/downloads
# IMPORTANTE: Marque "Add Python to PATH" na instalação
```

### Erro "No module named 'pygame'"
```bash
pip install pygame numpy
```

### Aventura muito lenta
- Ajuste o FPS em `constants.py`
- Use um computador com melhor desempenho
- Feche outros programas pesados

### Sem efeitos sonoros
- Verifique se o pygame.mixer inicializou corretamente
- Pressione 'M' para verificar se o áudio não está mutado
- Verifique as configurações de áudio do sistema

## 🏆 Créditos da Aventura

- **🎮 Desenvolvimento**: Implementação completa em Python com Pygame
- **👥 Personagens**: Inspirados na incrível série Adventure Time
- **🎵 Áudio**: Sistema avançado de geração procedural com NumPy
- **🎨 Arte**: Sistema híbrido de sprites (imagens + desenhos automáticos)
- **💡 Inspiração**: Baseado no clássico Bomberman, reimaginado na Terra de Ooo
- **🌟 Tema**: Adventure Time - criado por Pendleton Ward

---

**🎮 Versão**: BOOM 1.0  
**⚡ Tecnologia**: Python + Pygame + NumPy  
**📜 Licença**: Uso Acadêmico  
**🏰 Reino**: Terra de Ooo  

**Que a aventura comece! 💥**