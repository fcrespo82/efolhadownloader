#!/bin/sh

os=$(uname -s)
case $os in
	Darwin)
		if ! [ -x "$(command -v brew)" ]; then
			/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
		fi
		brew install httpie
		break
		;;
	Linux)
		apt-get install httpie -y
		break
		;;
esac
