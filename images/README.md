# 🎨 Como Adicionar Sprites ao Jogo

## 📁 Estrutura de Arquivos de Imagem

Coloque suas imagens PNG/JPG na pasta `images/` com os seguintes nomes:

### 👤 Personagens
- `finn-frame1.png` - Finn (Adventure Time - Aventureiro)
- `jake-frame1.png` - Jake (Adventure Time - Cachorro)
- `marceline-frame1.png` - Marceline (Adventure Time - Vampira)
- `princesa-frame1.png` - Princesa Jujuba (Adventure Time - Princesa)

### 👾 Inimigos
- `enemy.png` - Sprite principal do inimigo
- `enemy_walk1.png` *(opcional)* - Frame 1 da animação do inimigo
- `enemy_walk2.png` *(opcional)* - Frame 2 da animação do inimigo

### 💣 Bomba
- `bomb.png` - Sprite da bomba

### 💥 Explosão
- `explosion.png` - Sprite básico da explosão
- `explosion_center.png` *(opcional)* - Centro da explosão
- `explosion_horizontal.png` *(opcional)* - Parte horizontal da explosão
- `explosion_vertical.png` *(opcional)* - Parte vertical da explosão

### ⭐ Power-ups
- `powerup_bomb.png` - Power-up de bomba extra
- `powerup_range.png` - Power-up de alcance da explosão
- `powerup_speed.png` - Power-up de velocidade

### 🧱 Cenário *(opcional)*
- `wall.png` - Parede indestrutível
- `brick.png` - Tijolo destrutível

## 📏 Especificações Técnicas

### Tamanho Recomendado
- **Personagens e Elementos**: 16x16 pixels ou 32x32 pixels
- **Formato**: PNG com transparência ou JPG
- **Estilo**: Pixel art para melhor resultado

### Como o Sistema Funciona

1. **Carregamento Automático**: O jogo tenta carregar todas as imagens automaticamente
2. **Fallback Inteligente**: Se uma imagem não for encontrada, usa o sprite desenhado manualmente
3. **Sem Interrupção**: O jogo funciona perfeitamente mesmo sem as imagens

## 🚀 Passos para Adicionar suas Sprites

1. **Prepare suas imagens** (16x16 ou 32x32 pixels)
2. **Renomeie** com os nomes exatos listados acima
3. **Coloque** na pasta `images/`
4. **Execute** o jogo - as imagens serão carregadas automaticamente!

## ✨ Exemplo de Estrutura Final

```
jogo/
├── images/
│   ├── player.png           ✅ Essencial
│   ├── enemy.png            ✅ Essencial
│   ├── bomb.png             ✅ Essencial
│   ├── explosion.png        ✅ Essencial
│   ├── powerup_bomb.png     ✅ Recomendado
│   ├── powerup_range.png    ✅ Recomendado
│   ├── powerup_speed.png    ✅ Recomendado
│   ├── player_walk1.png     ⭐ Opcional
│   ├── player_walk2.png     ⭐ Opcional
│   └── wall.png             ⭐ Opcional
├── index.html
├── game.js
├── sprites.js
└── style.css
```

## 🎯 Dicas de Design

- **Mantenha o estilo consistente** entre todas as sprites
- **Use transparência** para bordas suaves
- **Evite detalhes muito pequenos** em sprites 16x16
- **Teste** as cores para garantir boa visibilidade no fundo verde

---

**💡 Não tem as imagens ainda?** Não tem problema! O jogo funciona perfeitamente com as sprites desenhadas automaticamente. Você pode adicionar as imagens posteriormente.
