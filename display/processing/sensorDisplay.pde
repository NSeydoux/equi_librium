int realWidth = 660;
int realHeight = 500;
float sensorD = 15;
int nbSensors = 2;
// Variable partagée indiquant le nombre de mesures
int nbSamples;
// Tableau partagé indiquant la position de chaque capteur
int[][] sensorCoordinate;
// Tableau partagé indiquant l'évolution des données au cours du temps
int[][] dataset;
// Tableau partagé rassemblant les informations des deux tableaux précédents, que l'on va représenter
Sensor[][] sensorArray;

// Fonction qui bloque l'exécution du programme pendant ms millisecondes
void myDelay(int ms)
{
   try
  {    
    Thread.sleep(ms);
  }
  catch(Exception e){}
}

void initializeSensorMapping()
{
  // Load text file as a string
  String[] rawSensorMapping = loadStrings("sensorMapping_test_2");
  // on prépare une matrice pour accueillir les coordonnées de chaque capteur
  sensorCoordinate = new int[nbSensors][2];
  int[] tmpCoord = new int[2];
  for(int i=0; i<rawSensorMapping.length; i++)
  {
    tmpCoord = int(split(rawSensorMapping[i], ','));
    sensorCoordinate[i][0] = tmpCoord[0];
    sensorCoordinate[i][1] = tmpCoord[1];
  }
}

void initializeDataset()
{
  // On va charger la valeur des capteurs au cours du temps
  String[] rawDataset = loadStrings("dataset_test_2");
  dataset = new int[rawDataset.length][nbSensors];
  nbSamples = rawDataset.length;
  int[] tmpData = new int[nbSensors];
  for(int i=0; i<rawDataset.length; i++)
  {
    // Convert string into an array of integers using ',' as a delimiter
    tmpData = int(split(rawDataset[i],','));
    for(int j=0; j<nbSensors; j++)
    {
      // dataSet représentera l'état des capteurs au cours du temps, 
      // chaque colonne représentant un vecteur de capteurs à un instant donné
      dataset[i][j] = tmpData[j];
      print(tmpData[j],",");
    }
    print("\n");
  }
}

void initializeSensorArray()
{
  sensorArray = new Sensor[nbSamples][nbSensors];
  for(int i=0; i<nbSamples; i++)
  {
     for(int j=0; j<nbSensors; j++)
    {
       sensorArray[i][j] = new Sensor(sensorCoordinate[j][0]+300, sensorCoordinate[j][1]+200, sensorD, dataset[i][j]);
    } 
  }
}

void setup() {
  size(realWidth,realHeight);
  frameRate(50);
  initializeSensorMapping();
  initializeDataset();
  // Maintenant qu'on connait les coordonnées de chaque capteur, 
  // et l'évolution de leur valeur au cours du temps, 
  // on peut à présent créer la matrice
  // de l'évolution des capteurs au cours du temps
  initializeSensorArray();
  print("Nombre de capteurs : ", nbSensors, "\n");
  print("Nombre de mesures : ", nbSamples, "\n");
  //noLoop();
}
int nbLoops = 0;
void draw() {
  nbLoops += 1;
  background(255);  
  //for (int i = 0; i < nbSamples; i++)
  //{
    print(nbLoops%nbSamples, "\n");
    for(int j=0; j<nbSensors; j++)
    {
      sensorArray[nbLoops%nbSamples][j].display();
    }
  //}
}

class Sensor 
{
  // a sensor is composed of a location and a resistance value, as well as a diameter
  float x,y;   // x,y location
  float d; // diameter
  float r; // relative resistance
  
  float rMax = 60000.0;
  float rMin = 280.0;
  
  Sensor(float tempX, float tempY, float tempD, int tempR)
  {
    x = tempX;
    y = tempY;
    d = tempD;
    // On transforme la pression en une valeur relative sur l'échelle de rMin à rMax
    //r = ((tempR-rMin))/rMax;
    r = tempR;
  } 
  
  void display() 
  {
    noStroke();
    // La couleur est calculée en niveau de gris
    // La résistance augmente quand la pression diminue, 
    // et plus la pression est forte plus on veut un affichage noir.
    // Si la résistance est maximum, on a pas de pression donc blanc (255)
    // Au contraire, si la résistance est faible, pression donc noir (0)
    // on crée un gradient en créant des cercles concentriques de transparence 
    // croissante.
    for(int i=1; i<=3*d; i++)
    {
      // Pour le détail du calcul, CF feuille
      fill(46.55*log(r)-262.10,46.55*log(r)-262.10,46.55*log(r)-262.10, 255/i);
      ellipse(x,y,d+i,d+i);
    }
  }
}
