# Entrega 2 — Hash e autenticação segura

**Disciplina:** Segurança da Informação — Unit  
**Equipe:** Eduardo Andrade Almeida, Gabriel Lima de Carvalho e Hyago Oliveira Costa  
**Docente:** Ana Carla do Nascimento Santos

[Guia de execução e apresentação à professora](docs/guia-apresentacao.html):
passo a passo, explicação do código, demonstração e perguntas para ensaiar.

## Problema e solução

Aplicação simples de terminal para cadastrar usuários e verificar senhas sem
persistir seu texto original. Usa Python, SQLite e a biblioteca padrão, sem
framework ou instalação de pacotes. Esta entrega fica em `entregas/entrega-2/`.

## Execução

Requisito: Python 3.10 ou superior, com SQLite e OpenSSL (disponíveis no Python
oficial). Execute os comandos abaixo **na raiz do repositório**, em um terminal:

```sh
python entregas/entrega-2/src/menu.py
```

Escolha `1` para cadastrar e `2` para entrar. Exemplo exclusivamente fictício:
usuário `aluno_demo`, frase `caderno azul junto da janela`. No terminal interativo
do Windows, cada caractere digitado aparece como `*`; Backspace apaga o último.
Em outros ambientes, a entrada usa `getpass`, sem exibir os caracteres.
Use uma frase diferente de exemplos públicos para uso real.
O cadastro persiste em `entregas/entrega-2/dados/usuarios.sqlite3`, ignorado pelo Git.
O caminho é calculado pelo arquivo Python e independe do diretório atual.
Não é necessário instalar o `requirements.txt` da Entrega 1.

O menu segue o estilo da Entrega 1: moldura, cores no terminal interativo,
títulos, mensagens de sucesso/falha e pausa para voltar ao menu.
Verde indica teste aprovado; amarelo destaca bloqueios esperados (proteção
funcionando); vermelho indica falha inesperada. A execução conjunta termina
com uma tabela de resultados e a duração total.

| Opção | Operação |
| --- | --- |
| 1 | Cadastro persistente, com as sete etapas explicadas |
| 2 | Login, com as cinco etapas explicadas |
| 3 | Demonstrar login correto |
| 4 | Demonstrar rejeição de senha incorreta |
| 5 | Demonstrar rejeição de usuário inexistente |
| 6 | Demonstrar salts e hashes diferentes para a mesma senha |
| 7 | Demonstrar bloqueio de senha comum/vazada |
| 8 | Demonstrar rejeição após adulterar o hash |
| 9 | Executar os seis cenários em sequência |
| 0 | Sair |

As opções 3 a 9 usam apenas contas fictícias em bancos temporários e não alteram
os cadastros das opções 1 e 2. Cada cenário confere o resultado esperado antes
de anunciar sucesso. O cadastro exibe salt e hash em hexadecimal para estudo;
a senha digitada não é exibida. O login explica o fluxo sem exibir o hash candidato.

## Algoritmo e parâmetros

| Item | Decisão |
| --- | --- |
| Derivação | PBKDF2-HMAC-SHA256 por `hashlib.pbkdf2_hmac` |
| Custo | 600.000 iterações |
| Salt | 16 bytes (128 bits), novo por cadastro, de `secrets.token_bytes` |
| Hash derivado | 32 bytes (256 bits) |
| Comparação | `hmac.compare_digest`, sobre dois valores de 32 bytes |
| Persistência | SQLite: usuário, algoritmo, iterações, salt e hash; nenhuma coluna de senha |
| Senhas | 8 a 128 caracteres, Unicode e espaços preservados, sem exigir classes de caracteres |
| Base de bloqueio | SecLists: senhas comuns e amostra vazada RockYou; consulta local |

PBKDF2 é uma das opções aceitas pela professora e dispensa dependências. O custo
segue o slide 14 (página 14 do PDF) e o parâmetro de PBKDF2-SHA256 documentado pela
[OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html).
Isso não constitui certificação FIPS da aplicação. A alternativa Argon2id oferece
resistência baseada também em memória e deve ser considerada numa evolução.

**Por que não SHA-256 isolado?** Sua rapidez permite testar muitas senhas por
segundo. Sem salt, senhas iguais também geram hashes iguais e favorecem tabelas
pré-computadas. O salt individual distingue os registros; PBKDF2 eleva o custo
de cada tentativa. Salt não é secreto e fica junto do hash. Não há chave para
descriptografar uma senha: a verificação deriva outro valor e o compara.

## Fluxo

1. Cadastro: normalizar usuário; validar tamanho da senha e consultar base local.
2. Gerar salt; derivar hash; gravar os cinco campos com SQL parametrizado.
3. Login: buscar o registro; derivar o candidato usando os parâmetros armazenados e validados.
4. Comparar com `hmac.compare_digest`; aceitar somente a correspondência de um usuário existente.
5. Para usuário inexistente, executar derivação fictícia e responder a mesma mensagem de falha.

Duplicidade não sobrescreve o cadastro. Senha errada e usuário inexistente mostram
`Usuário ou senha inválidos.`. A derivação fictícia reduz diferenças óbvias de
tempo; ela não torna constante o tempo de todo o login.

## Testes e evidências

```sh
python -X utf8 entregas/entrega-2/tests/executar.py
python -X utf8 entregas/entrega-2/src/demo.py
```

O executor mostra os testes em tempo real, com nomes legíveis, status colorido
e duração por teste. Salva automaticamente uma cópia sem códigos ANSI em
`evidencias/testes.txt`. O comando padrão do unittest também continua disponível:
`python -X utf8 -m unittest discover -s entregas/entrega-2/tests -v`.

Para salvar uma nova evidência:

```sh
python -X utf8 entregas/entrega-2/src/demo.py --salvar entregas/entrega-2/evidencias/demonstracao.txt
python -X utf8 entregas/entrega-2/tests/executar.py
```

A demonstração cria um SQLite temporário dentro de `dados/`, exibe os registros
protegidos e testa sucesso e falhas. Não altera o banco do menu e remove seu próprio
banco ao encerrar. Hashes e salts mudam em cada execução. Os testes também usam
bancos temporários independentes e **os parâmetros reais de 600.000 iterações**.

- [Evidência de cadastro protegido e autenticação](evidencias/demonstracao.txt)
- [Resultado dos testes automatizados](evidencias/testes.txt)
- [Execução dos seis cenários pelo novo menu](evidencias/menu.txt)
- [Documentação acadêmica com capa e folha de rosto](docs/relatorio.html), imprimível em A4.
- [Relatório em PDF](docs/relatorio.pdf).

## Atendimento aos documentos

| Requisito | Implementação / evidência |
| --- | --- |
| Cadastro/login e KDF apropriada | `src/autenticacao.py`, `src/menu.py`; PBKDF2 com 600 mil iterações |
| Hash e salt armazenados | Esquema SQLite e registros exibidos por `src/demo.py` |
| Login correto e incorreto | Testes automatizados e demonstração |
| Comparação segura da biblioteca | `hmac.compare_digest` e teste que verifica sua utilização |
| SHA-256 isolado inadequado | Explicação neste README e no relatório |
| ASVS 11.4.1 e 11.4.2 (slides) | KDF aprovada; ausência de MD5 e de hash genérico isolado |
| ASVS 6.2.1 e 6.2.5 (slides) | Mínimo de 8 caracteres; sem regras de composição |
| ASVS 6.2.12 (slides) | Consulta à base local de senhas comuns/expostas, com cobertura limitada documentada |
| Código, testes, evidências e documentação do fluxo | Pastas `src/`, `tests/`, `evidencias/` e `docs/` |
| Capa, contracapa e seções do modelo | Relatório acadêmico; folha de rosto como contracapa |

## Riscos, limitações e melhorias

Escopo didático e local. Não há serviço web, sessão persistente, MFA, recuperação
de conta ou limitação de tentativas; login apenas informa o resultado. Não usar
este protótipo como serviço público sem implementar esses controles e TLS.
O banco não é cifrado: uma cópia permite tentativas de quebra offline, mesmo com
KDF. Proteger permissões e backups continua necessário. A senha existe na memória
durante a operação; Python não garante sua limpeza imediata.

As bases incluídas são limitadas, estáticas e derivadas de compilações públicas. Não
detecta toda senha vazada; exige atualização e uma base maior em produção. O cadastro
revela duplicidade de usuário na interface local. Custo da KDF deve ser medido no
ambiente de destino; atualização de parâmetros exige migração/rehash planejado.
Não se afirma conformidade integral com ASVS ou ISO.

## Referências

- SANTOS, Ana Carla do Nascimento. *Atividade — Projeto Integrador: Segurança Aplicada ao Desenvolvimento*. Material da disciplina, 2026, p. 2–3.
- SANTOS, Ana Carla do Nascimento. *Aula 01 — Unidade 02*. Material da disciplina, 2026, páginas 6, 14, 17, 19 e 21.
- [OWASP — Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html).
- [Python — hashlib.pbkdf2_hmac](https://docs.python.org/3.13/library/hashlib.html#hashlib.pbkdf2_hmac).
- [Python — hmac.compare_digest](https://docs.python.org/3.13/library/hmac.html#hmac.compare_digest).
- [OWASP — Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html).
- [SecLists — origem e licença da base](recursos/README.md).
