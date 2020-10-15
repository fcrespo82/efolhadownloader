#!/bin/bash

prepare_key() {
	if [ ! -f ~/.ssh/id_rsa.pub.pem ]; then 
		if [ -f ~/.ssh/id_rsa ]; then 
			openssl rsa -in ~/.ssh/id_rsa -pubout -out ~/.ssh/id_rsa.pub.pem
		else
			echo "Você não tem uma chave rsa. Por favor crie usando ssh-keygen para usar a funcionalidade de criptografia e salvar as configurações." 1>&2
			return 100
		fi
	fi
	return 0
}

encrypt() {
	prepare_key
	cat $1 | openssl rsautl -encrypt -pubin -inkey ~/.ssh/id_rsa.pub.pem
}

decrypt() {
	prepare_key
	cat $1 | openssl rsautl -decrypt -inkey ~/.ssh/id_rsa
}

if [ -f ./config.enc ] && [ -f ~/.ssh/id_rsa.pub.pem ]; then
	eval $(decrypt ./config.enc)
	#echo $matricula-$senha
else
	read -p "Matricula: " matricula
	matricula=$(printf "%06d" $matricula)
	read -s -p "Senha: " senha
	echo
	
	prepare_key
	if [ $? -eq 0 ]; then 
		echo matricula=$matricula > ./config
		echo senha=$senha >> ./config
		encrypt ./config > ./config.enc && rm ./config
	fi
fi

rm /tmp/efolhasession &> /dev/null
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