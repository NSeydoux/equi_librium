/*
 * Mux.h : Bibliothèque pour utiliser un multiplexer CD4051B soit en 
 * multiplexer, soit en demultiplexer.
 * Author : Nicolas Seydoux
 * Date : 19/10/2014
 */
 
 #ifndef MUX_H
 #define MUX_H
 
 #define SELECTION_PINS_COUNT 3
 
 #include "Arduino.h"
 
 class Mux
 {
	 public:
	 	// Defines the number of avalable channels, the common pin, the selection pins, the mode (mux or demux)
		// and wether the common pin is analogic or not
		Mux(int chanNum, int comPin, int selectionPins[], bool mode, bool analog);
		// Sets the selection pins in order to select the right channels
		void selectChan(int chan);
		// Only available if mode=false
		int readComPin();
		// Only available if mode=true
		void writeComPin(bool value);
		void init();
	 private:
		// Pins de sélection du canal
		int _selectionPins[SELECTION_PINS_COUNT];
		// Pin commune
		int _comPin;
		// Nombre de canaux utilisés (borne pour la valeur sélectionnée)
		int _chanNum;
		// mode permet de choisir entre le mode multiplexeur (1 vers n, mode = true)
		// et le mode démultiplexeur (n vers 1, mode = false). La différence entre
		// les deux modes est le sens d'utilisation de la pin commune.
		bool _mode;
		// Détermine si la pin commune est analogique ou numérique.
		bool _analog;
 };
 
 #endif
