#!/bin/sh

read -p "Matricula: " matricula
matricula=$(printf "%06d" $matricula)
read -s -p "Senha: " senha
echo

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

	if [ -f $anoref-$mesref-$tipo-$matricula.pdf ]; then
		echo "Pulando $anoref-$mesref-$tipo-$matricula.pdf"
		continue
	else
		echo "Baixando $anoref-$mesref-$tipo-$matricula.pdf"
		http --session /tmp/efolhasession --form POST --timeout 60 https://www.e-folha.prodesp.sp.gov.br/desc_dempagto/DemPagtoP.asp Tipo=$tipo sequencia=$sequencia mesref=$mesref anoref=$anoref strTarget=$strTarget > $anoref-$mesref-$tipo-$matricula.pdf
	fi
done