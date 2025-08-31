# 💣 Game Design Document (GDD)
## Bomberman Clone - Adventure Time Edition

---

## 📋 **Informações Básicas do Projeto**

| **Aspecto** | **Detalhes** |
|-------------|--------------|
| **Título do Jogo** | Bomberman Clone - Adventure Time Edition |
| **Gênero** | Puzzle/Ação, Arcade |
| **Plataforma** | PC (Windows/Linux/Mac) |
| **Engine** | Python + Pygame |
| **Público-alvo** | 10+ anos, fãs de jogos clássicos e Adventure Time |
| **Modo de jogo** | Single Player vs AI |
| **Resolução** | 800x600 pixels |
| **Estilo visual** | 2D, pixel art inspirado em Adventure Time |

---

## 🎯 **Visão Geral do Jogo**

### **Conceito Principal**
Um clone fiel do clássico jogo Bomberman, ambientado no universo Adventure Time. O jogador controla personagens icônicos da série em batalhas estratégicas usando bombas para eliminar inimigos e destruir obstáculos.

### **Pillars de Design**
1. **Estratégia**: Planejamento de movimento e colocação de bombas
2. **Reflexos**: Reação rápida para evitar explosões
3. **Progressão**: Sistema de power-ups e níveis crescentes
4. **Nostalgia**: Mecânicas clássicas do Bomberman original

---

## 🎮 **Mecânicas de Jogo**

### **Controles**
| **Ação** | **Tecla** | **Função** |
|----------|-----------|------------|
| Movimento | WASD / Setas | Move o personagem em 4 direções |
| Bomba | Espaço | Coloca uma bomba na posição atual |
| Pausar | P | Pausa/despausa o jogo |
| Som | M | Liga/desliga áudio |
| Menu | ESC | Volta ao menu principal |

### **Sistema de Bombas**
- **Timer**: 3 segundos até explosão
- **Alcance inicial**: 2 tiles em cruz
- **Duração da explosão**: 0.5 segundos
- **Limite inicial**: 1 bomba por vez
- **Dano**: Elimina inimigos e destrói blocos quebráveis

### **Sistema de Movimento**
- **Velocidade do jogador**: 2 pixels por frame
- **Velocidade dos inimigos**: 1 pixel por frame
- **Grid-based**: Movimento alinhado ao grid 40x40 pixels
- **Colisão**: Verificação precisa com margem interna

### **Sistema de Power-ups**
| **Power-up** | **Cor** | **Efeito** |
|--------------|---------|------------|
| 💣 Bomba Extra | Azul | +1 bomba máxima |
| 🔥 Alcance | Laranja | +1 tile de alcance |
| ⚡ Velocidade | Verde | Aumenta velocidade |

---

## 👥 **Personagens**

### **Personagens Jogáveis**
1. **Finn (Aventureiro)**
   - Sprite: `Finn-frame1.png`
   - Características: Balanceado

2. **Jake (Cachorro Mágico)**
   - Sprite: `jake-frame1.png`
   - Características: Balanceado

3. **Marceline (Rainha Vampira)**
   - Sprite: `marceline-frame1.png`
   - Características: Balanceado

4. **Princesa Jujuba**
   - Sprite: `princesa-frame1.png`
   - Características: Balanceado

### **Inimigos (AI)**
- **Comportamento**: Sistema inteligente com 3 modos
  - **Exploração**: Movimento aleatório seguro
  - **Ataque**: Aproximação cautelosa do jogador
  - **Fuga**: Escape de situações perigosas

- **IA Defensiva**: Sistema ultra-conservador
  - Cooldown: 2-3 minutos antes da primeira bomba
  - Agressividade: 1-5% apenas
  - Verificações de segurança: 8+ rotas de fuga necessárias

---

## 🗺️ **Ambiente e Level Design**

### **Estrutura do Mapa**
- **Dimensões**: 20x15 tiles (800x600 pixels)
- **Tile size**: 40x40 pixels
- **Layout**: Grade estruturada com paredes fixas e blocos destruíveis

### **Tipos de Tiles**
| **Tipo** | **Descrição** | **Propriedades** |
|----------|---------------|------------------|
| Vazio | Espaço livre | Permite movimento |
| Parede | Obstáculo fixo | Indestrutível, bloqueia movimento |
| Bloco | Obstáculo quebrado | Destrutível por bombas |
| Bomba | Explosivo ativo | Temporário, 3s timer |
| Explosão | Área de dano | Temporário, 0.5s |

### **Sistema de Cores**
- **Paredes**: Cinza escuro (68, 68, 68)
- **Blocos**: Marrom tijolo (205, 133, 63)
- **Explosões**: Laranja-vermelho (255, 107, 53)
- **UI**: Preto semi-transparente + texto branco

---

## 🔊 **Sistema de Áudio**

### **Configuração Técnica**
- **Frequência**: 22050 Hz
- **Buffer**: 512 samples
- **Canais**: Stereo (2 canais)
- **Formato**: 16-bit signed

### **Sistema de Sons**
- **Toggle**: Tecla M para ligar/desligar
- **Estrutura**: Preparado para SFX e música
- **Gerador**: `sounds/audioGenerator.js` para criação de efeitos

---

## 🏆 **Sistema de Progressão**

### **Objetivos do Jogo**
- **Principal**: Eliminar todos os inimigos
- **Secundário**: Coletar power-ups
- **Sobrevivência**: Evitar explosões e inimigos

### **Sistema de Vidas**
- **Vidas iniciais**: 3 vidas
- **Game Over**: Ao perder todas as vidas
- **Vitória**: Eliminar todos os inimigos

### **Estados de Jogo**
1. **START**: Tela inicial
2. **CHARACTER_SELECT**: Seleção de personagem
3. **PLAYING**: Gameplay ativo
4. **PAUSED**: Jogo pausado
5. **GAME_OVER**: Derrota
6. **VICTORY**: Vitória

---

## 🛠️ **Especificações Técnicas**

### **Arquitetura do Código**
```
📁 Estrutura do Projeto
├── main.py                 # Entry point
├── game/
│   ├── __init__.py
│   ├── bomberman_game.py   # Core game loop
│   ├── constants.py        # Configurações globais
│   ├── entities.py         # Player, Enemy, Bomb, Explosion
│   ├── game_map.py         # Mapa e colisões
│   ├── sprites.py          # Sistema de sprites
│   ├── ui.py               # Interface do usuário
│   └── audio.py            # Sistema de áudio
├── images/                 # Assets visuais
└── sounds/                 # Assets de áudio
```

### **Dependências**
- **Python**: 3.7+
- **Pygame**: 2.0+
- **NumPy**: Para cálculos matemáticos

### **Performance**
- **FPS**: 60 fps constantes
- **Resolução**: Fixa 800x600
- **Otimizações**: Collision detection otimizada, sprites estáticos

---

## 🎨 **Direção de Arte**

### **Estilo Visual**
- **Inspiração**: Adventure Time + Bomberman clássico
- **Paleta**: Cores vibrantes, contrastantes
- **Sprites**: Estáticos, sem animação (otimização)
- **UI**: Minimalista, não-obstrutiva

### **Assets Visuais**
- **Personagens**: 4 sprites únicos (Adventure Time)
- **Tiles**: Sistema de cores sólidas
- **Efeitos**: Explosões com cores vibrantes
- **Interface**: Texto limpo sobre fundos semi-transparentes

---

## 🧪 **Plano de Testes**

### **Aspectos Testados**
1. **Movimento**: Fluidez e precisão das colisões
2. **Bombas**: Timer, explosões, alcance
3. **IA**: Comportamento defensivo, sobrevivência
4. **Power-ups**: Funcionamento correto dos efeitos
5. **Performance**: 60 FPS estáveis

### **Casos de Teste Críticos**
- Jogador não deve ficar preso em bombas próprias
- Bots não devem se auto-eliminar
- Colisões precisas em bordas de tiles
- Sistema de pause/unpause funcional

---

## 📈 **Roadmap de Desenvolvimento**

### **Fase 1 - Core Gameplay** ✅
- [x] Sistema básico de movimento
- [x] Mecânica de bombas
- [x] Sistema de colisões
- [x] IA básica dos inimigos

### **Fase 2 - Polish & Balance** ✅
- [x] Otimização da IA (sistema defensivo)
- [x] Refinamento de colisões
- [x] Sistema de sprites estáticos
- [x] Interface de usuário

### **Fase 3 - Documentação** 🚧
- [x] Game Design Document
- [ ] Manual do usuário
- [ ] Documentação técnica

### **Possíveis Expansões Futuras**
- [ ] Múltiplos níveis
- [ ] Multiplayer local
- [ ] Sistema de pontuação
- [ ] Mais personagens Adventure Time
- [ ] Efeitos sonoros completos
- [ ] Animações de sprites

---

## 📞 **Informações de Contato**

| **Aspecto** | **Detalhes** |
|-------------|--------------|
| **Versão atual** | 1.0 |
| **Data de criação** | Agosto 2025 |
| **Status** | Em desenvolvimento - fase de polish |
| **Licença** | Projeto educacional |

---

*Este Game Design Document serve como referência completa para o desenvolvimento e manutenção do Bomberman Clone - Adventure Time Edition. Mantenha este documento atualizado conforme o projeto evolui.*
