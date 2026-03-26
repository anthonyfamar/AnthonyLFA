## 🧠 Mapa Mental do Projeto

![Mapa Mental](/MapaMental.png)

📌 Leitor de Temperatura com Raspberry Pi

Este projeto tem como objetivo realizar a leitura de temperatura utilizando uma Raspberry Pi e um sensor conectado a ela.

A aplicação foi desenvolvida em C# e funciona de forma contínua, capturando a temperatura do ambiente em intervalos de tempo e exibindo os valores diretamente no console.

A proposta é ser uma solução simples e prática, ideal para quem deseja iniciar projetos com automação, monitoramento ou Internet das Coisas (IoT).

🚀 O que o projeto faz
Realiza a leitura da temperatura automaticamente
Exibe os valores em tempo real
Funciona diretamente na Raspberry Pi
Não depende de ferramentas complexas
🎯 Objetivo

Demonstrar de forma simples como integrar hardware (sensor de temperatura) com software em C#, criando uma base para projetos maiores como monitoramento remoto, automação residencial ou controle de ambientes.

⚙️ Como funciona

O projeto utiliza um sensor de temperatura conectado à Raspberry Pi, que é responsável por medir a temperatura do ambiente.

Esse sensor envia os dados diretamente para o sistema da Raspberry Pi, onde eles ficam disponíveis como se fossem um arquivo interno. A aplicação em C# lê esse arquivo periodicamente, interpreta o valor da temperatura e exibe o resultado na tela.

De forma resumida, o processo acontece assim:

1. O sensor mede a temperatura do ambiente
2. A Raspberry Pi recebe essa informação
3. O sistema salva o valor em um arquivo interno
4. O programa em C# lê esse arquivo
5. A temperatura é convertida e exibida no console

Tudo isso acontece automaticamente em intervalos de poucos segundos, permitindo um acompanhamento contínuo da temperatura em tempo real.
