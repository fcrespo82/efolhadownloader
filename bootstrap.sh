#!/bin/sh

os=$(uname -o)
case $os in
	Darwin)
		/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
		brew install httpie;
		break
		;;
	Linux)
		apt-get install httpie -y;
		break
		;;
esac