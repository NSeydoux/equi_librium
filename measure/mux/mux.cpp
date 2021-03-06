#include "mux.h"

Mux::Mux(int chanNum, int comPin, int selectionPins[], bool mode, bool analog)
{
	//memcpy(this->_selectionPins, selectionPins, 3);
	for(int i=0; i<SELECTION_PINS_COUNT; i++)
	{
		this->_selectionPins[i] = selectionPins[i];
	}
	this->_chanNum = chanNum;
	this->_comPin = comPin;
	this->_mode = mode;
	this->_analog = analog;
}

void Mux::init()
{
	for(int i=0; i<SELECTION_PINS_COUNT; i++)
	{
		pinMode(this->_selectionPins[i], OUTPUT);
		//Serial.println("Setting up output "+String(this->_selectionPins[i]));
		// On met toutes les pins de sélection à 0
		digitalWrite(this->_selectionPins[i], LOW);
	}
	
	if(this->_mode)
	{
		// Mode multiplexeur -> on écrit sur la pin commune
		pinMode(this->_comPin, OUTPUT);
	}
	else
	{
		// Mode démultiplexeur -> on lit sur la pin commune
		pinMode(this->_comPin, INPUT);
	}
}

void Mux::selectChan(int chan)
{
	//Serial.println("Selecting chan "+String(chan));
	for (int i=0; i<SELECTION_PINS_COUNT; i++)
	{
		int state = bitRead(chan, i);
		if(state == 0)
		{
			//Serial.println("Selection pin "+String(i)+" equals LOW");
			digitalWrite(this->_selectionPins[i], LOW);
		}
		else
		{
			//Serial.println("Selection pin "+String(i)+" equals HIGH");
			digitalWrite(this->_selectionPins[i], HIGH);
		}
	}
}

int Mux::readComPin()
{
	// Si mode=false, l'opération est autorisée
	if(!this->_mode)
	{
		if(this->_analog)
		{
			return analogRead(this->_comPin);
		}
	}
	return -1;
}
	
void Mux::writeComPin(bool value)
{
	if(this->_mode && !this->_analog)
	{
		digitalWrite(this->_comPin, value?HIGH:LOW);
	}
}

