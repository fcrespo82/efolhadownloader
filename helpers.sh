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
	openssl rsautl -in "$1" -encrypt -pubin -inkey ~/.ssh/id_rsa.pub.pem -passin env:ID_RSA_PASS
}

decrypt() {
	prepare_key
	openssl rsautl -in "$1" -decrypt -inkey ~/.ssh/id_rsa -passin env:ID_RSA_PASS
}