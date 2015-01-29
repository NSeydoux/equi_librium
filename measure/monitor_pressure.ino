#include <SD.h>
#include <mux.h>
// Constante de sélection de la pin hardware
const int chipSelect = 10;

// Initialisation du multiplexeur
int selectionPins[] = {4,5,6};
int nombreCapteurs = 4;
// valeur des résistances des capteurs
int sensorValue[] = {0, 0, 0, 0};

Mux mux(nombreCapteurs, A0, selectionPins, false, true);

// select the input pins for the potentiometer
// useful when using several multiplexers
int sensorPin[] = {A0};
// input pin for the arduino, useful when only using one multiplexer
int commonPin = A0;

  
// valeur de la résistance fixe du pont diviseur, en Ohm
int fixedResistor = 1000; 
float inputVoltage = 5.0;
float outputVoltage = 0.0;
long int maxSensorResistance = 60000;

// Ces deux variables seront dans une version ultérieure
// mise à jour par des boutons qui permettront de lancer
// et de stopper la mesure.
boolean beginSampling = true;
boolean endSampling = false;

File dataFile;

void setup() 
{
  Serial.begin(9600);
  Serial.print("Initializing SD card...");
  // make sure that the default chip select pin is set to
  // output, even if you don't use it:
  pinMode(10, OUTPUT);
  mux.init();
  // see if the card is present and can be initialized:
  if (!SD.begin(chipSelect)) {
    Serial.println("Card failed, or not present");
    // don't do anything more:
    return;
  }
  Serial.println("card initialized.");
  delay(2000);
}

void loop() 
{
  while(!beginSampling)
  {
   delay(200); 
  }
  while(!endSampling)
  {
    // read the value from the sensor:
    for(int i=0; i<nombreCapteurs; i++)
    {
      //outputVoltage = analogRead(sensorPin[i]) * (5.0 / 1024.0);
      mux.selectChan(i);
      delay(10);
      //outputVoltage = analogRead(commonPin) * (5.0 / 1024.0);
      outputVoltage = mux.readComPin() * (5.0 / 1024.0);
      //Serial.println(outputVoltage);
      sensorValue[i] = int(inputVoltage*fixedResistor/outputVoltage-fixedResistor);
    }
    //Serial.println("---");
    String dataString="";
    for(int i=0; i<nombreCapteurs; i++)
    {
      if(sensorValue[i]>0)
      {
        dataString += sensorValue[i];
      }
      else
      {
        dataString += maxSensorResistance;
      }
      if(i<nombreCapteurs-1)
      {
        dataString += ",";
      }
    }
    //dataString += "\n";
    dataFile = SD.open("datalog.txt", FILE_WRITE);
    dataFile.println(dataString);
    dataFile.close();
    Serial.println(dataString);
    delay(1000);     
  }
  return;
}
