#!/bin/bash

NAME="python"
VERSION="3.10.5-1"
PACKAGE="$NAME=$VERSION"
RESULT=`pacman -Q $PACKAGE`
if [ "$RESULT" = "$NAME $VERSION" ]; 
then
echo "$NAME already installed"
else
echo "Installing: $NAME $VERSION"
sudo pacman -Sy $PACKAGE --noconfirm
fi

NAME="rhvoice"
VERSION="1.8.0-1"
PACKAGE="$NAME=$VERSION"
RESULT=`pacman -Q $PACKAGE`
if [ "$RESULT" = "$NAME $VERSION" ]; 
then
echo "$NAME already installed"
else
echo "Installing: $NAME $VERSION"
sudo pacman -Sy $PACKAGE --noconfirm
fi

NAME="scons"
VERSION="4.3.0-3"
PACKAGE="$NAME=$VERSION"
RESULT=`pacman -Q $PACKAGE`
if [ "$RESULT" = "$NAME $VERSION" ]; 
then
echo "$NAME already installed"
else
echo "Installing: $NAME $VERSION"
sudo pacman -Sy $PACKAGE --noconfirm
fi

NAME="gcc"
VERSION="12.1.0-2"
PACKAGE="$NAME=$VERSION"
RESULT=`pacman -Q $PACKAGE`
if [ "$RESULT" = "$NAME $VERSION" ]; 
then
echo "$NAME already installed"
else
echo "Installing: $NAME $VERSION"
sudo pacman -Sy $PACKAGE --noconfirm
fi

NAME="flite"
VERSION="2.2-1"
PACKAGE="$NAME=$VERSION"
RESULT=`pacman -Q $PACKAGE`
if [ "$RESULT" = "$NAME $VERSION" ]; 
then
echo "$NAME already installed"
else
echo "Installing: $NAME $VERSION"
sudo pacman -Sy $PACKAGE --noconfirm
fi

NAME="expat"
VERSION="2.4.8-1"
PACKAGE="$NAME=$VERSION"
RESULT=`pacman -Q $PACKAGE`
if [ "$RESULT" = "$NAME $VERSION" ]; 
then
echo "$NAME already installed"
else
echo "Installing: $NAME $VERSION"
sudo pacman -Sy $PACKAGE --noconfirm
fi

NAME="pkgconf"
VERSION="1.8.0-1"
PACKAGE="$NAME=$VERSION"
RESULT=`pacman -Q $PACKAGE`
if [ "$RESULT" = "$NAME $VERSION" ]; 
then
echo "$NAME already installed"
else
echo "Installing: $NAME $VERSION"
sudo pacman -Sy $PACKAGE --noconfirm
fi

NAME="speech-dispatcher"
VERSION="0.11.1-3"
PACKAGE="$NAME=$VERSION"
RESULT=`pacman -Q $PACKAGE`
if [ "$RESULT" = "$NAME $VERSION" ]; 
then
echo "$NAME already installed"
else
echo "Installing: $NAME $VERSION"
sudo pacman -Sy $PACKAGE --noconfirm
fi

NAME="boost"
VERSION="1.79.0-1"
PACKAGE="$NAME=$VERSION"
RESULT=`pacman -Q $PACKAGE`
if [ "$RESULT" = "$NAME $VERSION" ]; 
then
echo "$NAME already installed"
else
echo "Installing: $NAME $VERSION"
sudo pacman -Sy $PACKAGE --noconfirm
fi

sudo pip3 install vosk==0.3.42

sudo pip3 install pyaudio==0.2.11

sudo pip3 install pymorphy2==0.9.1

sudo pip3 install pyautogui==0.9.53

sudo pip3 install pynput==1.7.6
