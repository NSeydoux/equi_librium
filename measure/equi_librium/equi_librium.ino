#include <SD.h>
#include <mux.h>
#include <rider_manager.h>

// TODO : Ajouter les deux mux, et les déclarer dans le tableau de mux et de pins communes
#define MUX_COUNT 2
#define CHAN_COUNT 8
#define SENSOR_COUNT 16
#define MAX_RIDER_COUNT 10

/*************** DÉCLARATIONS ***************/

typedef enum {SELECT, RECORD} T_Mode;

T_Mode current_mode;

/*** Broches de controle du registre à décalage ***/
// Broche connectée au ST_CP du 74HC595
const int P_VERROU = 4;
// Broche connectée au SH_CP du 74HC595
const int P_HORLOGE = 5;
// Broche connectée au DS du 74HC595
const int P_DATA = 3;

/*** Broche de controle de la carte SD ***/
// Constante de sélection de la pin hardware
const int P_CHIPSELECT = 10;
File DATAFILE;
RiderManager riderManager = RiderManager(P_CHIPSELECT);

/*** Broche reliées aux boutons d'input ***/
// Bouton de choix du cavalier
const int P_RIDER_BUTTON = 2;
const int P_MODE_BUTTON = 6;

/*** Constantes liées au multiplexeurs ***/
// Initialisation du multiplexeur
int selectionPins[3] = {7, 8, 9};
int analog_pins[MUX_COUNT] = {A0, A1};//, A2, A3};
Mux mux[MUX_COUNT] = 
{
  Mux(8, A0, selectionPins, false, true),
  Mux(8, A1, selectionPins, false, true)
//  Mux(8, A2, selectionPins, false, true), 
//  Mux(8, A3, selectionPins, false, true)
};

/*** Constantes liées aux cavaliers ***/
int current_rider_number = 0;

/*** Constantes liées à la mesure de résistance et aux capteurs***/
// valeur de la résistance fixe du pont diviseur, en Ohm
int fixedResistor = 1000; 
float inputVoltage = 5.0;
float outputVoltage = 0.0;
long int maxSensorResistance = 60000;
// valeur des résistances des capteurs
int sensorValue[SENSOR_COUNT];

String dataString;

// Ces deux variables seront dans une version ultérieure
// mise à jour par des boutons qui permettront de lancer
// et de stopper la mesure.
boolean beginSampling = true;
boolean endSampling = false;

/*** Constantes pour l'affichage 7 segments ***/
const byte numeral[10] = 
{
  B11111100, // 0
  B01100000, // 1
  B11011010, // 2
  B11110010, // 3
  B01100110, // 4
  B10110110, // 5
  B10111110, // 6
  B11100000, // 7
  B11111110, // 8
  B11100110 //9
};
const byte blank = B11111111;

/*************** INITIALISATION ***************/

boolean init_SD()
{
  Serial.println("Initializing SD card...");
  // make sure that the default chip select pin is set to
  // output, even if you don't use it:
  if (!SD.begin(P_CHIPSELECT)) 
  {
    Serial.println("Card failed, or not present");
    // don't do anything more:
    return false;
  }
  Serial.println("card initialized.");
  return true;
}

void init_var()
{
  for(int i=0; i<SENSOR_COUNT; i++)
  {
    sensorValue[i] = 0;
  }
  
  for(int i=0; i<MUX_COUNT; i++)
  {
    mux[i].init();
  }
  current_mode = SELECT;
  riderManager.init();
  afficher_nombre(current_rider_number);
}

void init_pins()
{
  // 2
  pinMode(P_RIDER_BUTTON, INPUT);
  // 3
  pinMode(P_DATA,         OUTPUT);
  // 4
  pinMode(P_VERROU,       OUTPUT);
  // 5
  pinMode(P_HORLOGE,      OUTPUT);
  // 6
  pinMode(P_MODE_BUTTON,  INPUT);
  // 7, 8, 9 -> Multiplexeurs (configurées dans la librairie mux)
  // 10, 11, 12, 13 -> shield SD
  pinMode(P_CHIPSELECT,   OUTPUT); 
}

/*************** FONCTIONS MÉTIER ***************/

boolean isRiderButtonPressed()
{
  return digitalRead(P_RIDER_BUTTON);
}

boolean isMeasureEnabled()
{
  return digitalRead(P_MODE_BUTTON);
}

// Cette fonction est active tant que les mesures ne sont pas lancées. Elle permet de 
// choisir le numéro  du cavalier pour lequel on va faire une séance de mesures.
void select_rider()
{
  Serial.println("Selecting the rider...");
  while(!isMeasureEnabled())
  {
    if(isRiderButtonPressed())
    {
      current_rider_number = (current_rider_number + 1)%MAX_RIDER_COUNT;
      afficher_nombre(current_rider_number);
      if(current_rider_number > riderManager.getNumberOfRiders())
      {
         riderManager.addRider();
      }
    }
    delay(100);
  }
  Serial.print("Selected rider : ");
  Serial.println(current_rider_number);
}

// TODO : Mesurer le temps d'exécution de cette fonction
void perform_measure()
{
   Serial.println("Measure started");
   DATAFILE = riderManager.addRecord(current_rider_number);
   while(isMeasureEnabled())
   {
     for(int i=0; i<CHAN_COUNT; i++)
     {
       read_chan_value(i);
     }
     writeSensorValue(DATAFILE);
   }
   Serial.println("Measure done");
   DATAFILE.close();
   Serial.println("File closed");
}

// Lit la valeur de la channel chan sur tous les multiplexeurs
void read_chan_value(int chan)
{
  // Il suffit de sélectionner la channel une fois, les 4 mutliplexeurs étant 
  // cablés de la meme façon
  mux[0].selectChan(chan);
  delay(5);
  for(int m=0; m<MUX_COUNT; m++)
  {
    outputVoltage = mux[m].readComPin() * (5.0 / 1024.0);
    Serial.println("Reading value number "+String(chan+m*CHAN_COUNT));
    sensorValue[chan+m*CHAN_COUNT] = int(inputVoltage*fixedResistor/outputVoltage-fixedResistor);
  }
}

// Cette fonction écrit durablement le contenu du tableau de valeurs de capteurs
// sur la carte SD
void writeSensorValue(File f)
{
    Serial.println("Writing new record...");
    dataString="";
    for(int i=0; i<SENSOR_COUNT; i++)
    {
      if(sensorValue[i]>0)
      {
        dataString += sensorValue[i];
      }
      else
      {
        dataString += maxSensorResistance;
      }
      if(i<SENSOR_COUNT-1)
      {
        dataString += ",";
      }
    }
    dataString += "\n";
    f.println(dataString);
    Serial.println("New record written");
}

/*************** UTILITAIRE AFFICHEUR 7 SEGMENTS ***************/

void blink_segment()
{
  for(int i=0; i<3; i++)
  {
   afficher_data(blank);
   delay(200);
   afficher_nombre(current_rider_number);
   delay(200); 
  }
}

void afficher_data(char data)
{
  //On active le verrou le temps de transférer les données
  digitalWrite(P_VERROU, LOW);
  //on envoi toutes les données grâce à notre belle fonction
  envoi_ordre(P_DATA, P_HORLOGE, 1, data);
  //et enfin on relâche le verrou
  digitalWrite(P_VERROU, HIGH);
  //une petite pause pour constater l'affichage 
  delay(100);
}

// Affiche le modulo 10 du nombre passé en paramètre sur un afficheur 7 segments
void afficher_nombre(int nombre)
{
  afficher_data(~numeral[nombre%10]);
}
 
void envoi_ordre(int dataPin, int clockPin, boolean sens, char donnee)
{
    //on va parcourir chaque bit de l'octet
    for(int i=0; i<8; i++)
    {
        //on met l'horloge à l'état bas
        digitalWrite(clockPin, LOW);
        //on met le bit de donnée courante en place
        if(sens)
        {            
            digitalWrite(dataPin, donnee & 0x01 << i);
        }
        else
        {
            digitalWrite(dataPin, donnee & 0x80 >> i);
        }
        //enfin on remet l'horloge à l'état haut pour faire prendre en compte cette dernière
        digitalWrite(clockPin, HIGH);
    }
}

/*************** MAIN ***************/

void setup()
{
  Serial.begin(9600);
  init_pins();
  delay(500);
  init_var();
  delay(500);
}

void loop() 
{
  switch(current_mode)
  {
   case SELECT:
     select_rider();
     break;
   case RECORD:
     blink_segment();
     while(isMeasureEnabled())
     {
       perform_measure();
     }
     blink_segment();
     break;
  }
  // Transition d'un mode à l'autre si nécessaire
  if(isMeasureEnabled())
  {
    current_mode = RECORD;
  }
  else
  {
    current_mode = SELECT;
  }
  delay(100);
}
