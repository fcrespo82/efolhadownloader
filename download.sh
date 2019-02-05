#!/bin/sh

read -p "Matricula: " matricula 
read -s -p "Senha: " senha
echo

folhas=$(http --form POST https://www.e-folha.prodesp.sp.gov.br/desc_dempagto/Folhas.asp txtMatricula=$matricula txtNPA=000000000 txtSenha=$senha Cookie:ASPSESSIONIDCUQRQDDT=IAGPCNHDOHPBPJOINKJHKMLC | grep -o Atualiza\(.\*\)\; | grep -o \'.\*\')

for folha in $folhas; do
	tipo=$(echo $folha | cut -d, -f1 | tr -d "'")
	sequencia=$(echo $folha | cut -d, -f2 | tr -d "'")
	mesref=$(echo $folha | cut -d, -f3 | tr -d "'")
	anoref=$(echo $folha | cut -d, -f4 | tr -d "'")
	strTarget=$(echo $folha | cut -d, -f5 | tr -d "'")

	http --form POST https://www.e-folha.prodesp.sp.gov.br/desc_dempagto/DemPagtoP.asp Tipo=$tipo sequencia=$sequencia mesref=$mesref anoref=$anoref btOK=ENTRAR strTarget=$strTarget txtMatricula=$matricula txtNPA=000000000 txtSenha=$senha Cookie:ASPSESSIONIDCUQRQDDT=IAGPCNHDOHPBPJOINKJHKMLC > $anoref-$mesref-$tipo-$matricula.pdf
done