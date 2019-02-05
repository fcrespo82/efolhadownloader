#!/bin/bash

if test -f ./config ; then
	. ./config
	matricula=$(echo $matricula | base64 --decode -)
	senha=$(echo $senha | base64 --decode -)
else
	read -p "Matricula: " matricula
	matricula=$(printf "%06d" $matricula)
	read -s -p "Senha: " senha
	echo
	echo matricula=$(echo $matricula | base64 -) > ./config
	echo senha=$(echo $senha | base64 -) >> ./config
fi

rm /tmp/efolhasession
# Cookie
http --session /tmp/efolhasession https://www.e-folha.prodesp.sp.gov.br/desc_dempagto/entrada.asp?cliente=050 &> /dev/null
echo "Got Cookie?"

# Login
http --session /tmp/efolhasession --form POST https://www.e-folha.prodesp.sp.gov.br/desc_dempagto/PesqSenha.asp txtMatricula=$matricula txtNPA=000000000 txtSenha=$senha btOK=ENTRAR &> /dev/null
echo "Autenticado"

# Folhas
folhas=$(http --session /tmp/efolhasession --form POST https://www.e-folha.prodesp.sp.gov.br/desc_dempagto/Folhas.asp | grep -o Atualiza\(.\*\)\; | grep -o \'.\*\')
echo "Listando folhas"

for folha in $folhas; do
	tipo=$(echo $folha | cut -d, -f1 | tr -d "'")
	sequencia=$(echo $folha | cut -d, -f2 | tr -d "'")
	mesref=$(echo $folha | cut -d, -f3 | tr -d "'")
	anoref=$(echo $folha | cut -d, -f4 | tr -d "'")
	strTarget=$(echo $folha | cut -d, -f5 | tr -d "'")

	if [ -f $anoref-$mesref-$tipo-$sequencia-$matricula.pdf ]; then
		echo "Pulando $anoref-$mesref-$tipo-$sequencia-$matricula.pdf"
		continue
	else
		echo "Baixando $anoref-$mesref-$tipo-$sequencia-$matricula.pdf"
		http --session /tmp/efolhasession --form --timeout 60 POST https://www.e-folha.prodesp.sp.gov.br/desc_dempagto/DemPagtoP.asp Tipo=$tipo sequencia=$sequencia mesref=$mesref anoref=$anoref strTarget=$strTarget > $anoref-$mesref-$tipo-$sequencia-$matricula.pdf
		if [ $? -gt 0 ]; then
			rm $anoref-$mesref-$tipo-$sequencia-$matricula.pdf
			echo "Erro ao baixar $anoref-$mesref-$tipo-$sequencia-$matricula.pdf"
			echo "Execute o comando de novo"
		fi
	fi
done