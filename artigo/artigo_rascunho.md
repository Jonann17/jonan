<!--
RASCUNHO v0.1 — artigo da disciplina Tópicos Especiais em Energia e Sustentabilidade II (entrega 3)
Base: plano de trabalho do TCC (v5, 21/09/2026). Texto para ser reescrito pelos autores.
Marcadores: [CITA NECESARIA] [DATO] [REFERENCIA A VERIFICAR]
Ver artigo/PENDIENTES.md para a lista de lacunas.
-->

# PROTEÇÃO DE INSTALAÇÕES RESIDENCIAIS NA RECARGA DE VEÍCULOS ELÉTRICOS: SISTEMA COOPERATIVO DE BAIXO CUSTO

Jonathan Ariel Salinas Espinola¹, Joylan Nunes Maciel², Jorge Javier Gimenez Ledesma²

¹ Universidade Federal da Integração Latino-Americana (UNILA), Engenharia de Energia, Foz do Iguaçu, Brasil. jas.espinola.2022@aluno.unila.edu.br
² Universidade Federal da Integração Latino-Americana (UNILA), [PROGRAMA], Foz do Iguaçu, Brasil. [e-mail]

## RESUMO

A recarga residencial de veículos elétricos (VE) impõe uma carga elevada e prolongada, de 4 a 12 h, a instalações dimensionadas antes da sua existência, expondo-as à sobrecarga da entrada de serviço e ao aquecimento localizado em tomadas, emendas e terminais com resistência de contato elevada. O disjuntor termomagnético atua lentamente entre 1,0 e 1,45 vezes a corrente nominal e não detecta pontos quentes, e as soluções comerciais de monitoramento são fechadas, dependentes do carregador ou de custo elevado. Propõe-se um sistema aberto e de baixo custo, composto por dois dispositivos cooperativos baseados em ESP32: o Nó A mede a corrente da entrada e o Nó B mede a corrente e a temperatura do circuito do VE e aciona um contator. A comunicação por ESP-NOW com heartbeat garante falha segura, e uma máquina de estados com quatro níveis (Normal, Alerta, Pré-desligamento e Desligado) combina limiares de 80, 90 e 95% da corrente nominal do disjuntor geral, limiares de 55 e 70 °C e o resíduo de um modelo térmico de primeira ordem. Definiram-se os requisitos, a arquitetura, a lógica de proteção e um plano de validação em bancada e em campo, com critérios de erro de corrente de até 2%, erro quadrático médio do modelo térmico de até 3 °C, latência de até 2 s e custo do par de até R$ 800. A contribuição consiste em uma camada complementar de proteção, independente do carregador e replicável, com validação metrológica e conjunto de dados abertos previstos.

**Palavras-chave:** veículos elétricos; recarga residencial; proteção de instalações elétricas; monitoramento térmico; hardware aberto.

## ABSTRACT

Residential electric vehicle (EV) charging imposes a high and prolonged load, lasting 4 to 12 h, on installations sized before its existence, exposing them to service-entrance overload and to localized heating in outlets, splices and terminals with high contact resistance. The thermal-magnetic circuit breaker reacts slowly between 1.0 and 1.45 times its rated current and does not detect hot spots, while commercial monitoring solutions are closed, charger-dependent or costly. An open, low-cost system composed of two cooperative ESP32-based devices is proposed: Node A measures the service-entrance current, and Node B measures the current and temperature of the EV circuit and drives a contactor. ESP-NOW communication with a heartbeat ensures fail-safe operation, and a four-level state machine (Normal, Alert, Pre-shutdown and Shutdown) combines thresholds of 80, 90 and 95% of the main breaker rated current, thresholds of 55 and 70 °C, and the residual of a first-order thermal model. Requirements, architecture, protection logic and a bench and field validation plan were defined, with acceptance criteria of current error up to 2%, thermal-model root mean square error up to 3 °C, latency up to 2 s and a cost of up to R$ 800 for the pair. The contribution is a complementary, charger-independent and replicable protection layer, with planned metrological validation and an open dataset.

**Keywords:** electric vehicles; residential charging; electrical installation protection; thermal monitoring; open hardware.

## 1 INTRODUÇÃO

A eletrificação do transporte reduz a emissão de poluentes no uso final e desloca para a rede de distribuição uma demanda antes atendida por combustíveis fósseis [CITA NECESARIA]. No Brasil, a frota de VE cresce a cada ano, e a maior parte da recarga ocorre na residência do usuário, durante a noite [CITA NECESARIA]. A recarga residencial apoia a adoção do VE, decorrente da conveniência e do menor custo da energia em relação à recarga pública, mas transfere para a instalação de baixa tensão a responsabilidade de suprir uma carga de 1,5 a 7,4 kW por períodos de 4 a 12 h [CITA NECESARIA].

As instalações residenciais existentes foram dimensionadas sem essa carga. Quando o VE é recarregado simultaneamente com o chuveiro elétrico e o forno, a corrente total pode superar a corrente nominal (I_n) do disjuntor geral, e o fator de demanda adotado no projeto deixa de representar a operação real [CITA NECESARIA]. Mesmo sem sobrecarga, a corrente elevada e contínua aquece tomadas, emendas e terminais com resistência de contato elevada, condição agravada no Brasil pela recarga em modo 2, com cabo portátil conectado a tomadas de 10 ou 20 A (IEC 61851-1) [REFERENCIA A VERIFICAR]. O disjuntor termomagnético não atua nessa situação: entre 1,13 e 1,45 I_n, o tempo de disparo pode chegar a 1 h (IEC 60898-1), e um ponto quente localizado não altera a corrente do circuito [REFERENCIA A VERIFICAR].

Apesar de existirem medidores de energia de baixo custo, algoritmos de gestão de carga e carregadores com sensores de temperatura integrados, ainda não se dispõe de um sistema aberto e de baixo custo que (i) combine a medição na entrada de serviço e no circuito do VE, (ii) relacione corrente e temperatura por meio de um modelo térmico para detectar conexões degradadas, (iii) funcione com qualquer carregador, inclusive em tomada, e (iv) seja validado em bancada e em campo com incerteza declarada.

O objetivo geral deste trabalho é desenvolver e validar experimentalmente um sistema de baixo custo, com dois dispositivos cooperativos, que monitore a corrente da entrada da residência e a corrente e a temperatura do circuito de recarga do VE, emitindo alarmes e interrompendo a recarga por contator antes que a instalação opere em condição de risco. Os objetivos específicos são: sistematizar a literatura, as normas e as soluções comerciais; especificar requisitos, limiares e modos de falha; projetar e construir os dois dispositivos; implementar a comunicação, a lógica de proteção escalonada, o modelo térmico e o painel de visualização; avaliar a exatidão de corrente e temperatura e identificar o modelo térmico em bancada; avaliar o desempenho funcional em bancada e em campo com VE real; comparar o custo com soluções comerciais; e publicar o conjunto de dados.

Formulam-se três hipóteses: (H1) o erro relativo da medição de corrente é de até 2% entre 5 e 40 A; (H2) o sistema interrompe a recarga antes do disparo do disjuntor geral, sem desligamentos indevidos em transitórios; e (H3) o resíduo entre a temperatura medida e a estimada identifica uma conexão degradada antes de 70 °C.

A Seção 2 apresenta a fundamentação teórica e as lacunas da literatura; a Seção 3, os materiais e o método; a Seção 4, os resultados da etapa de projeto; a Seção 5, a discussão; e a Seção 6, a conclusão.

## 2 FUNDAMENTAÇÃO TEÓRICA

### 2.1 Recarga residencial e limites da instalação

A IEC 61851-1 define quatro modos de recarga condutiva. No modo 2, o VE é conectado a uma tomada comum por um cabo com dispositivo de controle e proteção integrado (IC-CPD); no modo 3, a recarga ocorre por um equipamento dedicado (wallbox), fixado à instalação [REFERENCIA A VERIFICAR]. Nos modos 2 e 3, o sinal Control Pilot (CP) informa ao VE a corrente máxima disponível, o que permite a gestão de carga, mas exige carregador compatível [REFERENCIA A VERIFICAR].

A capacidade da instalação é limitada pela potência disponibilizada pela distribuidora (ANEEL REN 1000/2021) e pelo disjuntor geral [REFERENCIA A VERIFICAR]. A IEC 60364-7-722 e a ABNT NBR 17019 tratam da alimentação de VE em instalações de baixa tensão e da consideração da recarga no cálculo da demanda [REFERENCIA A VERIFICAR]. Como a recarga é uma carga contínua, a hipótese de não simultaneidade, implícita nos fatores de demanda residenciais, deixa de valer durante a noite, quando coincide com o chuveiro e com a cocção [CITA NECESARIA].

### 2.2 Aquecimento de conexões e modelo térmico

A potência dissipada em uma conexão é P = I²R_c, em que R_c é a resistência de contato. Oxidação, afrouxamento e baixa pressão de contato elevam R_c e, com corrente contínua de 16 a 32 A, produzem aquecimento localizado capaz de degradar a isolação [CITA NECESARIA]. A ABNT NBR 5410 limita a temperatura de condutores com isolação de PVC a 70 °C em regime contínuo [REFERENCIA A VERIFICAR].

O comportamento térmico do ponto de conexão pode ser aproximado por um modelo de primeira ordem:

C_th · dT/dt = I²R − (T − T_amb)/R_th   (1)

em que C_th é a capacidade térmica, R_th a resistência térmica para o ambiente e T_amb a temperatura ambiente. Em regime permanente, a elevação de temperatura é ΔT = R_th·R·I², e a constante de tempo é τ = R_th·C_th. Identificados os parâmetros com uma conexão íntegra, o resíduo r = T_medida − T_estimada permanece próximo de zero; um aumento sustentado de r indica elevação de R_c, antes que a temperatura absoluta atinja o limite da isolação [CITA NECESARIA].

O disjuntor termomagnético segue as curvas da IEC 60898-1: não deve disparar em até 1 h com 1,13 I_n e deve disparar em até 1 h com 1,45 I_n [REFERENCIA A VERIFICAR]. Essa faixa protege o condutor contra sobrecarga, mas não contra pontos quentes, e permite que a entrada opere acima de I_n por longos períodos.

### 2.3 Medição de baixo custo e comunicação

A corrente alternada pode ser medida por transformadores de corrente (TC) de núcleo bipartido com conversor ADS1115, por sensores de efeito Hall (ACS712) ou por módulos integrados (PZEM-004T), com cálculo do valor eficaz (RMS) por amostragem [CITA NECESARIA]. A temperatura pode ser medida por termistores NTC, sensores digitais DS18B20 ou termopares tipo K, e a exatidão depende do acoplamento térmico entre sensor e conexão [CITA NECESARIA]. O ESP32 integra Wi-Fi e o protocolo ESP-NOW, que permite troca direta de mensagens entre dispositivos sem roteador, com latência baixa [CITA NECESARIA].

A concordância entre o sistema e um instrumento de referência é avaliada por erro relativo, pela análise de Bland-Altman e, para o modelo térmico, pelo erro quadrático médio (RMSE), com incerteza expressa segundo o Guia para a Expressão da Incerteza de Medição (GUM) [REFERENCIA A VERIFICAR].

### 2.4 Lacunas da literatura

Os estudos levantados distribuem-se em quatro grupos [DATO: L1–L16 da matriz de síntese]: impacto da recarga na instalação e na rede; gestão de carga; medidores de baixo custo; e monitoramento térmico e segurança. Os trabalhos de impacto quantificam a sobrecarga, mas não propõem proteção local [CITA NECESARIA]; os de gestão de carga dependem do sinal CP ou de carregadores comunicáveis [CITA NECESARIA]; os medidores de baixo custo registram consumo, sem atuação nem modelo térmico [CITA NECESARIA]; e os trabalhos térmicos medem temperatura sem relacioná-la à corrente por um modelo [CITA NECESARIA] (LINJA-AHO, 2024) [REFERENCIA A VERIFICAR]. No mercado, o Tesla Wall Connector, o LEONICS IC-CDP, o CLAMPER Mobi Plug, as soluções Wallbox/HEYCAR, o DCC-9, os medidores Emporia e Shelly e o painel SPAN cobrem parte dos requisitos, mas são fechados, restritos a um tipo de carregador ou de custo elevado [DATO: matriz de mercado]. Nenhum dos trabalhos atende simultaneamente aos critérios (i) a (iv) da Seção 1.

## 3 MATERIAIS E MÉTODO

### 3.1 Tipo e delineamento da pesquisa

Trata-se de pesquisa aplicada, experimental e quantitativa, orientada ao desenvolvimento de um artefato tecnológico. O trabalho organiza-se em oito etapas, com entregas quinzenais: revisão da literatura e das normas; especificação de requisitos e modos de falha; projeto e construção dos dispositivos; firmware e lógica de proteção; ensaios de bancada; ensaio de campo; análise de custo; e divulgação dos resultados e dos dados.

### 3.2 Dados

Os dados serão gerados pelo próprio sistema e por instrumentos de referência: séries temporais de corrente RMS na entrada e no circuito do VE, temperatura na tomada, no plugue e no condutor, temperatura ambiente, estado da máquina de estados e eventos de comunicação, com carimbo de tempo. O ensaio de campo ocorrerá em uma residência com VE real [DATO: ficha técnica da residência — I_n do disjuntor geral, tipo de ligação, carregador e VE], durante quatro semanas. O conjunto de dados será publicado no IEEE DataPort.

### 3.3 Instrumentos e ferramentas

O Nó A e o Nó B utilizarão ESP32 [DATO: modelo da placa], TC de núcleo bipartido com ADS1115 [DATO: modelo e relação do TC], sensores DS18B20 e termistores NTC [DATO: modelos], contator [DATO: modelo e corrente nominal] e fonte isolada. O firmware será desenvolvido em [DATO: framework e versão], com registro e alertas por MQTT [DATO: broker e versão]. A referência metrológica será o analisador de qualidade de energia da UNILA [DATO: modelo e classe de exatidão] e, para temperatura, [DATO: termopar ou câmera termográfica de referência]. A análise será feita em [DATO: Python e bibliotecas, com versões].

### 3.4 Método de análise e métricas

Definiram-se sete ensaios (Tabela 1). No ensaio metrológico (V1), a corrente será variada de 2 a 40 A, e o erro relativo e a concordância de Bland-Altman serão calculados contra o analisador de referência. No ensaio térmico (V2), o circuito operará com 16 a 20 A por 2 a 4 h, primeiro com conexão íntegra, para identificar C_th e R_th da Equação (1), e depois com terminal afrouxado, para avaliar o resíduo. No ensaio funcional (V3), cinco cenários (S1 a S5) reproduzirão sobrecarga da entrada, aquecimento da conexão, transitórios de partida e perda de comunicação [DATO: definição de S1–S5]. A incerteza de todas as medições será declarada segundo o GUM.

Tabela 1 – Ensaios de validação e critérios de aceitação.

| Ensaio | Objetivo | Critério de aceitação |
|---|---|---|
| V1 Metrológico | Exatidão de corrente, 2–40 A | Erro relativo ≤ 2% acima de 5 A (H1) |
| V2 Térmico | Identificação do modelo e detecção de conexão degradada | RMSE ≤ 3 °C; detecção antes de 70 °C (H3) |
| V3 Funcional | Cenários S1–S5 em bancada | Latência ≤ 2 s; desligamento antes do disjuntor geral, sem desligamentos indevidos (H2) |
| V4 Campo | Operação com VE real por 4 semanas | Operação contínua; [DATO: critério] |
| V5 Custo | Comparação com soluções comerciais | Par ≤ R$ 800 |
| V6 Visualização | Painel e alertas | [DATO: critério] |
| V7 Dados | Publicação aberta | Conjunto documentado no IEEE DataPort |

Fonte: Autores (2026).

## 4 RESULTADOS

> Nota para os autores: nesta fase só há resultados de projeto (requisitos, arquitetura e lógica). Os valores medidos de V1–V7 entram aqui quando existirem. Não apresentar critérios de aceitação como resultados.

### 4.1 Requisitos e limiares

Os requisitos definidos foram: medição da corrente total da entrada e da corrente do circuito do VE; medição da temperatura na tomada ou no plugue e no condutor; interrupção da recarga por contator, sem uso do sinal CP; operação com qualquer carregador, inclusive em modo 2; falha segura em caso de perda de comunicação; registro contínuo e alertas remotos; e custo do par de até R$ 800. Os limiares adotados derivam da I_n do disjuntor geral e do limite de 70 °C da isolação de PVC (Tabela 2).

Tabela 2 – Estados da lógica de proteção e condições de transição.

| Estado | Condição de entrada | Ação |
|---|---|---|
| 0 Normal | I_entrada < 80% I_n e T < 55 °C | Registro |
| 1 Alerta | I_entrada ≥ 80% I_n ou T ≥ 55 °C | Alerta local e remoto |
| 2 Pré-desligamento | I_entrada ≥ 90% I_n ou resíduo térmico acima do limiar [DATO] | Alerta e temporização para desligamento |
| 3 Desligado | I_entrada ≥ 95% I_n, T ≥ 70 °C ou perda de heartbeat > 5 s | Abertura do contator |

Fonte: Autores (2026).

### 4.2 Arquitetura

A arquitetura separa a medição da entrada e a atuação no circuito do VE (Figura 1) [DATO: Figura 1 – diagrama da arquitetura]. O Nó A, instalado no quadro de distribuição, mede a corrente total e a compara com a I_n do disjuntor geral. O Nó B, instalado no circuito do VE, mede a corrente e a temperatura da conexão, executa o modelo térmico e aciona o contator. Os nós trocam mensagens por ESP-NOW, com heartbeat periódico: se o Nó B ficar mais de 5 s sem mensagem do Nó A, o contator é aberto. O MQTT foi restrito ao registro e aos alertas, sem participação na decisão de proteção, de modo que a indisponibilidade da rede Wi-Fi ou do broker não altera a atuação.

### 4.3 Lógica de proteção

A máquina de estados da Tabela 2 escalona a resposta: o estado de Alerta informa o usuário sem interromper a recarga, o Pré-desligamento antecipa a interrupção e o Desligado abre o contator. A histerese entre os limiares de entrada e de saída de cada estado evita oscilação próxima aos limites [DATO: valores de histerese e temporizações]. O resíduo térmico atua no estado 2, antes do limite absoluto de 70 °C do estado 3.

### 4.4 Estimativa de custo

[DATO: Tabela 3 – lista de materiais e custo estimado do Nó A e do Nó B, em R$, com data e fonte dos preços.]

## 5 DISCUSSÃO

### 5.1 Interpretação

A separação entre medição da entrada e atuação no circuito do VE foi o principal resultado de projeto: o Nó A observa a instalação inteira, e o Nó B interrompe apenas a carga que pode ser postergada, sem desligar o restante da residência. A restrição da decisão de proteção ao enlace ESP-NOW, com heartbeat e abertura do contator na ausência de mensagens, faz com que falhas de comunicação levem ao estado seguro. A combinação de limiares absolutos com o resíduo do modelo térmico responde ao segundo risco, o aquecimento sem sobrecarga, que o disjuntor não detecta.

### 5.2 Comparação com estudos anteriores

Diferentemente das soluções de gestão de carga baseadas no sinal CP [CITA NECESARIA], a atuação por contator não depende do carregador e atende à recarga em modo 2. Em relação aos medidores de baixo custo [CITA NECESARIA], o sistema acrescenta atuação e modelo térmico; em relação aos carregadores com sensor de temperatura integrado [CITA NECESARIA], monitora também a entrada de serviço e a tomada da instalação. [DATO: completar com a matriz de síntese L1–L16.]

### 5.3 Implicações teóricas e práticas

Do ponto de vista prático, o sistema oferece uma camada de proteção para residências que passam a recarregar VE sem reforma imediata da instalação, e o hardware aberto permite replicação e adaptação. Do ponto de vista metodológico, a validação com incerteza declarada e a publicação dos dados permitem comparar trabalhos futuros sobre o mesmo problema.

### 5.4 Limitações

Todavia, o sistema é uma camada complementar e não substitui disjuntor, dispositivo DR ou DPS. A interrupção por contator encerra a recarga em vez de reduzir a corrente, como faria a modulação pelo sinal CP. O modelo térmico de primeira ordem depende do acoplamento entre sensor e conexão e da identificação dos parâmetros por instalação. A validação de campo será feita em uma única residência, o que limita a generalização.

## 6 CONCLUSÃO

Propôs-se um sistema de baixo custo, com dois dispositivos cooperativos, para monitorar e proteger instalações residenciais durante a recarga de VE. Definiram-se os requisitos, a arquitetura com Nó A e Nó B, a comunicação com falha segura, a lógica de proteção em quatro estados e o plano de validação em bancada e em campo. A proposta responde às duas condições de risco que o disjuntor geral não trata, a operação prolongada acima da corrente nominal e o aquecimento localizado de conexões, com atuação independente do carregador. As contribuições são a arquitetura cooperativa, o uso do resíduo térmico para detectar conexões degradadas e o compromisso com hardware e dados abertos. Todavia, os critérios de exatidão, latência e custo ainda dependem dos ensaios. Como trabalhos futuros, preveem-se a execução dos ensaios V1 a V7, a modulação da corrente pelo sinal CP em carregadores compatíveis e a avaliação em mais residências.

## AGRADECIMENTOS

[Opcional.]

## DECLARAÇÃO DE USO DE INTELIGÊNCIA ARTIFICIAL

Durante a preparação deste trabalho, os autores utilizaram Claude (Anthropic) com a finalidade de estruturar o texto a partir do plano de trabalho do TCC e de revisar linguagem e estilo. Após o uso, o conteúdo foi revisado e editado pelos autores, que assumem total responsabilidade pelo conteúdo.

## REFERÊNCIAS

> Todas as referências abaixo precisam ser conferidas (atividade A1.5) e completadas com as do portfólio (L1–L16). Ordem alfabética, ABNT NBR 6023:2018.

AGÊNCIA NACIONAL DE ENERGIA ELÉTRICA (ANEEL). **Resolução Normativa nº 1.000, de 7 de dezembro de 2021**. [REFERENCIA A VERIFICAR]

ASSOCIAÇÃO BRASILEIRA DE NORMAS TÉCNICAS. **NBR 5410**: instalações elétricas de baixa tensão. Rio de Janeiro: ABNT, [ANO]. [REFERENCIA A VERIFICAR]

ASSOCIAÇÃO BRASILEIRA DE NORMAS TÉCNICAS. **NBR 17019**: instalações elétricas de baixa tensão – requisitos para instalações em locais especiais – alimentação de veículos elétricos. Rio de Janeiro: ABNT, [ANO]. [REFERENCIA A VERIFICAR]

BLAND, J. M.; ALTMAN, D. G. Statistical methods for assessing agreement between two methods of clinical measurement. **The Lancet**, v. 327, n. 8476, p. 307–310, 1986. [REFERENCIA A VERIFICAR]

INTERNATIONAL ELECTROTECHNICAL COMMISSION. **IEC 60364-7-722**: low-voltage electrical installations – part 7-722: requirements for special installations or locations – supplies for electric vehicles. Geneva: IEC, [ANO]. [REFERENCIA A VERIFICAR]

INTERNATIONAL ELECTROTECHNICAL COMMISSION. **IEC 60898-1**: electrical accessories – circuit-breakers for overcurrent protection for household and similar installations – part 1. Geneva: IEC, [ANO]. [REFERENCIA A VERIFICAR]

INTERNATIONAL ELECTROTECHNICAL COMMISSION. **IEC 61851-1**: electric vehicle conductive charging system – part 1: general requirements. Geneva: IEC, [ANO]. [REFERENCIA A VERIFICAR]

JOINT COMMITTEE FOR GUIDES IN METROLOGY. **JCGM 100:2008**: evaluation of measurement data – guide to the expression of uncertainty in measurement. [S. l.]: JCGM, 2008. [REFERENCIA A VERIFICAR]

LINJA-AHO, V. [Título]. **[Periódico]**, 2024. DOI: [A CONFIRMAR]. [REFERENCIA A VERIFICAR]
