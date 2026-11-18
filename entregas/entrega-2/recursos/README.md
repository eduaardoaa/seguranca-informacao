# Base local de senhas bloqueadas

`senhas_comuns.txt` é uma cópia integral da lista pública `10k-most-common.txt` do
projeto SecLists, consultada em 17 nov. 2026. Apesar do nome, o arquivo contém
10.001 linhas nesta versão. O conjunto é usado somente para bloquear senhas
comuns/expostas no cadastro; não contém associação com identidades.

- Origem: <https://github.com/danielmiessler/SecLists/blob/master/Passwords/Common-Credentials/10k-most-common.txt>
- Licença: MIT; cópia incluída em `LICENSE-SecLists.txt`.
- Finalidade: consulta offline no fluxo do slide 14, ASVS 6.2.12.
- Comparação da base: `casefold()`; a senha usada pela KDF permanece inalterada.

É uma compilação limitada de senhas comuns, não uma base completa ou atualizada
de todos os vazamentos. A verificação demonstra o controle com um corpus local;
uma implantação real precisa ampliar e atualizar esse corpus com senhas expostas.
O arquivo ausente ou vazio interrompe a inicialização, sem liberar cadastros.
Nenhuma senha digitada é enviada a terceiros.

`senhas_vazadas.txt` acrescenta a cópia integral de `rockyou-50.txt`, do diretório
`Leaked-Databases` do mesmo projeto, obtida na mesma data e sob a mesma licença.
Assim, o cadastro consulta tanto senhas comuns quanto uma amostra explicitamente
proveniente de vazamento. Não há nomes de usuários ou contas reais nos arquivos.

Origem: <https://github.com/danielmiessler/SecLists/blob/master/Passwords/Leaked-Databases/rockyou-50.txt>.
Ambos os arquivos são obrigatórios. Sua união é deduplicada em memória.
