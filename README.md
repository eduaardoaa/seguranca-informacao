# Entrega 1 — Criptografia Assimétrica e Confiança

**Disciplina:** Segurança da Informação — Unit  
**Aluno:** Eduardo Andrade Almeida, Gabriel Lima de Carvalho, Hyago Oliveira Costa
**Docente:** Ana Carla do Nascimento Santos

---

## O que é esse projeto

Esse projeto implementa dois mecanismos de criptografia em Python para proteger mensagens trocadas entre serviços:

**Cifragem híbrida (AES-256-GCM + RSA-OAEP):** a mensagem é cifrada com AES e a chave AES é protegida com RSA. Só quem tem a chave privada consegue decifrar.

**Assinatura digital (RSA-PSS):** o remetente assina a mensagem e o destinatário consegue verificar se ela foi alterada ou não.

---

## Como instalar

```bash
pip install -r requirements.txt
```

---

## Como testar

```bash
cd entrega1-criptografia
python3 src/menu.py
```

Vai aparecer um menu no terminal com as opções:

- **1** — cifra e decifra uma mensagem normalmente (sucesso)
- **2** — adultera o texto cifrado e tenta decifrar (detecta a alteração)
- **3** — tenta decifrar com a chave errada (rejeita)
- **4** — assina e verifica uma mensagem (sucesso)
- **5** — altera a mensagem depois de assinar (assinatura fica inválida)
- **6** — tenta uma assinatura falsa com bytes aleatórios (rejeita)
- **7** — roda todos os testes de uma vez
- **0** — sai

---

## Como funciona

### Cifragem híbrida

O RSA não consegue cifrar mensagens grandes diretamente, então a solução é: gera uma chave AES aleatória, usa ela pra cifrar a mensagem, e cifra essa chave AES com RSA. O destinatário decifra a chave AES com a chave privada RSA e usa ela pra decifrar a mensagem.

O modo AES-GCM também verifica integridade — se um único byte for alterado no texto cifrado, ele rejeita automaticamente. Isso torna desnecessário usar um HMAC separado.

### Assinatura digital

O remetente usa a chave privada pra gerar uma assinatura sobre a mensagem. O receptor verifica com a chave pública. Se a mensagem foi alterada em qualquer coisa, a verificação falha. A mensagem fica em texto claro — a assinatura não cifra nada, só garante quem enviou e que não foi adulterada.

---

## Diferença entre sigilo e autenticidade

**Sigilo:** só o destinatário consegue ler o conteúdo (garantido pela cifragem).

**Autenticidade:** dá pra confirmar quem enviou e que a mensagem não foi alterada (garantido pela assinatura digital).

Os dois são independentes. Uma mensagem pode ser cifrada sem ser assinada, ou assinada sem ser cifrada. Em sistemas reais, geralmente os dois são usados juntos.

---

## Certificados digitais e PKI

Na criptografia assimétrica, um problema é: como garantir que a chave pública que você recebeu é mesmo da pessoa certa? Um atacante poderia trocar a chave.

A solução é a PKI (Public Key Infrastructure): uma Autoridade Certificadora (CA) emite certificados digitais (padrão X.509) que vinculam uma chave pública a uma identidade. Assim dá pra verificar se a chave é legítima.

Nesse projeto as chaves ficam salvas em arquivos locais só pra demonstração. Em produção seriam distribuídas via certificados X.509.

---

## Arquivos do projeto

```
src/cifragem_hibrida.py    — cifragem AES-GCM + RSA-OAEP
src/assinatura_digital.py  — assinatura RSA-PSS
src/demo_completo.py       — roda todos os testes direto no terminal
src/menu.py                — menu interativo
chaves/                    — gerado automaticamente ao rodar
requirements.txt           — dependência: biblioteca cryptography (PyCA)
```

---

## Limitações

- A chave privada é salva sem senha (só pra fins de demonstração)
- Não tem PKI real, as chaves são arquivos locais
- Sem proteção contra replay attack
- RSA-2048 vai ficar vulnerável com computadores quânticos — a migração seria pra algoritmos pós-quânticos (ML-KEM, ML-DSA)
