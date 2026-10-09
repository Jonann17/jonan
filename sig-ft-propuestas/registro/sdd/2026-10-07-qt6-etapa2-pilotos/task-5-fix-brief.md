# Task 5 — ronda de correção visual (pedido do controlador)
A tela Qt do Tradutor deve ficar visualmente igual à CTk (`sigft/app/views/translator.py`). Defeitos medidos em captura real, a corrigir no código COMPARTILHADO:
1. `blocos.botao(altura=)` ignorado (QSS global min-height 28px vence setFixedHeight) — fazer a altura valer, com teste.
2. "gray" do Tk = #808080 (Tk 8.6 usa o valor W3C), não #BEBEBE: `cinza_tk`, teste, e tirar o literal "#BEBEBE" da tela.
3. `#console` = CTkTextbox do tema: fundo gray20 #333333, sem borda.
4. Margens/espaços do ModuleFrame não embutido iguais ao CTk (show_frame padx/pady 20 + grid padx 20/pady 10 por linha). Home Qt NÃO muda. Modo embutido fica com margem 0.
5. Espaços internos do cartão do Tradutor iguais aos pady do CTk.
6. Botão do glossário: borda do CTkButton do tema (#949A9F) e texto text_light.
7. Quebra de linha: tirar o alinhamento do layout inteiro em `blocos.cartao` e remover o paliativo setWordWrap(False) da tela.
Restrições: não mexer em frontend.py nem na interface CTk; check.sh e `ruff check .` verdes; um commit local.
