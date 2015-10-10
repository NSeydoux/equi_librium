#include <SD.h>
#include <mux.h>
#include <rider_manager.h>

// TODO : Ajouter les deux mux, et les déclarer dans le tableau de mux et de pins communes
#define MUX_COUNT 4
#define CHAN_COUNT 8
// POur l'instant, 2 entrées sont inopérables
#define SENSOR_COUNT 32
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
int analog_pins[MUX_COUNT] = {A0, A1, A2, A3};
Mux mux[MUX_COUNT] = 
{
  Mux(8, A0, selectionPins, false, true),
  Mux(8, A1, selectionPins, false, true),
  Mux(8, A2, selectionPins, false, true),
  Mux(8, A3, selectionPins, false, true)
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
const byte all = B00000000;

/*************** INITIALISATION ***************/

boolean init_SD()
{
  //Serial.println("Initializing SD card...");
  // make sure that the default chip select pin is set to
  // output, even if you don't use it:
  if (!SD.begin(P_CHIPSELECT)) 
  {
    //Serial.println("Card failed, or not present");
    // don't do anything more:
    blink_error();
    return false;
  }
  //Serial.println("card initialized.");
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
  if(!riderManager.init())
  {
    blink_error();
  }
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
  while(!isMeasureEnabled())
  {
    if(isRiderButtonPressed())
    {
      current_rider_number = (current_rider_number + 1)%MAX_RIDER_COUNT;
      afficher_nombre(current_rider_number);
      if(current_rider_number > riderManager.getNumberOfRiders())
      {
         if(!riderManager.addRider())
         {
           blink_error();
         }
      }
    }
    delay(100);
  }
}

// TODO : Mesurer le temps d'exécution de cette fonction
void perform_measure()
{
   //Serial.println("Measure started");
   DATAFILE = riderManager.addRecord(current_rider_number);
   // TODO uncomment me
   /*while(isMeasureEnabled())
   {
     for(int i=0; i<CHAN_COUNT; i++)
     {
       read_chan_value(i);
     }
     writeSensorValue(DATAFILE);
   }*/
   // TODO comment loo
   while(isMeasureEnabled())
   {
     //long t0=millis();
     tmp_read_input();
     //long t1=millis();
     //Serial.println("Measure : "+String(t1-t0)+"ms");
     writeSensorValue(DATAFILE);
   }
   //Serial.println("Measure done");
   DATAFILE.close();
   //Serial.println("File closed");
}

int regular_sensor_num_match(int mux_n, int chan_n)
{
  return chan_n+mux_n*CHAN_COUNT;
}

// Computes the number of the sensor in the array 
// regarding the multiplexer and the channel
// returns -1 if no sensor can be matched
int tmp_sensor_num_match(int mux_n, int chan_n)
{
  int sensor_n;
   switch(mux_n)
   {
     case 0:
       sensor_n = chan_n+mux_n*CHAN_COUNT;
     break;
     case 1:
       if(chan_n<6)
       {
         // normal case, before the broken inputs
         sensor_n = chan_n+mux_n*CHAN_COUNT;
       }
       else
       {
         sensor_n = -1;
       }
     break;
     case 2:
       sensor_n = chan_n+mux_n*CHAN_COUNT-2;
     break;
     case 3:
       sensor_n = chan_n+mux_n*CHAN_COUNT-2;
     break;
     default:
       sensor_n = -1;
     break;
   }
   return sensor_n;
}

// fonction qui sert à lire les entrée tant que la carte a un défaut
void tmp_read_input()
{
   for(int c=0; c<CHAN_COUNT; c++)
   {
     mux[0].selectChan(c);
     for(int m=0; m<MUX_COUNT; m++)
     {
       // On remplace les valeurs mesurées sur les channels defecteux par les 
       // valeurs mesurées sur les autres channels
       outputVoltage = mux[m].readComPin() * (5.0 / 1024.0);
       //int sensor_val_num = tmp_sensor_num_match(m, c);
       int sensor_val_num = regular_sensor_num_match(m, c);
       if(sensor_val_num != -1)
       {
         sensorValue[sensor_val_num] = int(inputVoltage*fixedResistor/outputVoltage-fixedResistor);
       }
     }
   }
}

// Lit la valeur de la channel chan sur tous les multiplexeurs
void read_chan_value(int chan)
{
  // Il suffit de sélectionner la channel une fois, les 4 mutliplexeurs étant 
  // cablés de la meme façon
  mux[0].selectChan(chan);
  for(int m=0; m<MUX_COUNT; m++)
  {
    outputVoltage = mux[m].readComPin() * (5.0 / 1024.0);
    //Serial.println("Reading value number "+String(chan+m*CHAN_COUNT));
    sensorValue[chan+m*CHAN_COUNT] = int(inputVoltage*fixedResistor/outputVoltage-fixedResistor);
  }
}

// Cette fonction écrit durablement le contenu du tableau de valeurs de capteurs
// sur la carte SD
void writeSensorValue(File f)
{
    //long t0 = millis();
    dataString="";
    for(int i=0; i<SENSOR_COUNT; i++)
    {
      //Serial.println("Valeur pour le capteur "+i+" : "+sensorValue[i]);
      // 2 est une valeur seuil arbitraire pour filtrer les erreurs de mesures
      if(sensorValue[i]>2)
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
    //long t1=millis();
    f.println(dataString);
    //long t2=millis();
    //Serial.println(dataString);
    //long t3=millis();
    //Serial.println("Building : "+String(t1-t0)+"ms, Writing : "+String(t2-t1)+"ms, Serial : "+String(t3-t2)+"ms");
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

void blink_error()
{
  while(true)
  {
    blink_once();
  }
}

void blink_once()
{
    afficher_data(blank);
    delay(200);
    afficher_data(all);
    delay(200);
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
  //Serial.begin(9600);
  init_pins();
  delay(500);
  init_var();
  delay(500);
  while(isMeasureEnabled())
  {
    // Si le bouton de mode est enclenché, on stoppe le processus
    blink_once();
  }
  afficher_nombre(current_rider_number);
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
     perform_measure();
     blink_segment();
     break;
   default:
     blink_error();
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
}
