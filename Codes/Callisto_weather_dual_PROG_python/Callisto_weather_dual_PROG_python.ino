/* Supun Liyanaarachchi
  e-CALLISTO weather extended - v0.1
  Dual core processing
*/


//====================================================================
//              NTP server initializing
//====================================================================
#include <NTPClient.h>
#include <WiFiUdp.h>
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "lk.pool.ntp.org", 19800, 60000);

//====================================================================
//              Dual core initializing
//====================================================================
TaskHandle_t Task1;
TaskHandle_t Task2;

//====================================================================
//              connection - credential
//====================================================================
#include <WiFi.h>
#include <HTTPClient.h>
const char* ssid = "AstroACCIMTSLT";
const char* password = "*********";
const char* serverName = "https://192.168.1.101/e-callisto/MCUconnect/setData.php";
unsigned long timerDelay = 1000;




//====================================================================
//              RTC - integration
//====================================================================
#include "RTClib.h"
RTC_DS3231 rtc;

int sleep_hou=14;
int sleep_min=46;
int sleep_sec=00;

int wake_hou=14;
int wake_min=50;
int wake_sec=00;


//===================================================================
//            POST method
//===================================================================
String SEND="Z-";
String PASS="";
bool min_check=true;
bool sec_check=true;
bool check_avail=false;

// Wifi Send
void WifiSend(String SEND){
  if(WiFi.status() == WL_CONNECTED) {
      WiFiClient client;
      HTTPClient http;
      // Your Domain name with URL path or IP address with path
      http.begin(serverName);
      // Specify content-type header
      http.addHeader("Content-Type", "application/x-www-form-urlencoded");
      // Data to send with HTTP POST
      String postData = "temp="+SEND;
      auto httpCode = http.POST(postData);
      String payload = http.getString();
      Serial.println(postData);
      Serial.println(payload);
      // Free resources
      http.end();
  }
  else{
    Serial.println("WiFi Disconnected");
    WiFi.begin(ssid, password);
    while(WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
    }
    Serial.println("");
    Serial.print("Connected to WiFi network with IP Address: ");
    Serial.println(WiFi.localIP());
    }  
}



//===================================================================
//            DHT11 Sensor
//===================================================================
#include "DHT.h"
#define DHTPIN 4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// DHT11 
String readDHT(){
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  float f = dht.readTemperature(true);
  if (isnan(h) || isnan(t) || isnan(f)) {
    String dhtVal = "D-";
    dhtVal.concat("E");
    dhtVal.concat("-");
    return dhtVal;
  }else{
    String dhtVal = "D-";
    dhtVal.concat(h);
    dhtVal.concat("-");
    dhtVal.concat(t);
    dhtVal.concat("-");
    return dhtVal;
    }
  }


//===================================================================
//            BMP180 Sensor
//===================================================================
#include <Wire.h>
#include <Adafruit_BMP085.h>
Adafruit_BMP085 bmp;

//BMP180
String readBMP(){
  float p = bmp.readPressure();
  float t = bmp.readTemperature();
  float a = bmp.readAltitude();
if (isnan(p) || isnan(t) || isnan(a)) {
   String bmpVal = "B-";
   bmpVal.concat("E");
   bmpVal.concat("-");
   return bmpVal;
  }else{
    String bmpVal = "B-";
    bmpVal.concat(p);
    bmpVal.concat("-");
    bmpVal.concat(t);
    bmpVal.concat("-");
    bmpVal.concat(a);
    bmpVal.concat("-");
    return bmpVal;
   }
  }


//===================================================================
//            Rain Sensor
//===================================================================
#define rainAnalog 35

//Rain module
String readRainMod(){
  int rainAnalogVal = analogRead(rainAnalog);
  if (isnan(rainAnalogVal)) {
     String rainVal = "R-";
     rainVal.concat("E");
     rainVal.concat("-");
     return rainVal;
    }else{
      String rainVal = "R-";
      rainVal.concat(rainAnalogVal);
      rainVal.concat("-");
      return rainVal;
    }
  }

//===================================================================
//            LDR Sensor
//===================================================================
#define ldrAnalog 34

//LDR
String readLDR(){
  float LDRVal = analogRead(ldrAnalog);
  if (isnan(LDRVal)) {
     String ldrVal = "L-";
     ldrVal.concat("E");
     ldrVal.concat("-");
     return ldrVal;
    }else{
      String ldrVal = "L-";
      ldrVal.concat(LDRVal);
      ldrVal.concat("-");
      return ldrVal; 
    }
  }


//====================================================================
//              SD Card
//====================================================================
#include "FS.h"
#include "SD.h"
#include "SPI.h"

 
String appendFile(fs::FS &fs, const char * path, const char * message){
    Serial.printf("Appending to file: %s\n", path);

    File file = fs.open(path, FILE_APPEND);
    if(!file){
        Serial.println("Failed to open file for appending");
        return;
    }
    if(file.print(message)){
        Serial.println("Message appended");
    } else {
        Serial.println("Append failed");
    }
    file.close();
    return "append";
}




//====================================================================
//              setup()
//====================================================================

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  Serial.println("Connecting");
  while(WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected to WiFi network with IP Address: ");
  Serial.println(WiFi.localIP());

  //NTp server begin
  timeClient.begin();
  timeClient.update();
  
  // rtc begin
  rtc.begin();
  rtc.adjust(DateTime(timeClient.getEpochTime()));

  dht.begin();
  bmp.begin();

    //create a task that will be executed in the Task1code() function, with priority 1 and executed on core 0
  xTaskCreatePinnedToCore(
                    Task1code,   /* Task function. */
                    "Task1",     /* name of task. */
                    10000,       /* Stack size of task */
                    NULL,        /* parameter of the task */
                    1,           /* priority of the task */
                    &Task1,      /* Task handle to keep track of created task */
                    0); 

      //create a task that will be executed in the Task2code() function, with priority 1 and executed on core 1
  xTaskCreatePinnedToCore(
                    Task2code,   /* Task function. */
                    "Task2",     /* name of task. */
                    10000,       /* Stack size of task */
                    NULL,        /* parameter of the task */
                    1,           /* priority of the task */
                    &Task2,      /* Task handle to keep track of created task */
                    1);

    if(!SD.begin()){
        Serial.println("Card Mount Failed");
        return;
    }
    uint8_t cardType = SD.cardType();

    if(cardType == CARD_NONE){
        Serial.println("No SD card attached");
        return;
    }
    uint64_t cardSize = SD.cardSize() / (1024 * 1024);
    
}



//====================================================================
//              task1() - acqiring weather data
//====================================================================
void Task1code( void * pvParameters ){
  for(;;){
  DateTime now = rtc.now();
  char timee[10];
  sprintf( timee, "%02d:%02d:%02d", now.hour(), now.minute(),now.second() );
  char hourr[3];
  sprintf( hourr, "%02d", now.hour() );
  char secc[3];
  sprintf( secc, "%02d", now.second() );
  char minss[3];
  sprintf( minss, "%02d", now.minute() );
  int sec=atoi(secc);
  int mins=atoi(minss);
  int hou=atoi(hourr);

  String timeGet="";
  //timeGet=timeGet+hou+":"+mins+":"+sec;

  if(0>hou & hou<10){
     timeGet=timeGet+"0"+hou; 
  }
  else{
    timeGet=timeGet+hou; 
  }
               timeGet=timeGet+":";
    if(mins<10){
     timeGet=timeGet+"0"+mins; 
  }
  else{
    timeGet=timeGet+mins; 
  }
              timeGet=timeGet+":";
    if(sec<10){
     timeGet=timeGet+"0"+sec; 
  }
  else{
    timeGet=timeGet+sec; 
  }

  //Serial.println(timeGet);



  int now_time_in_s=hou*3600+mins*60+sec;
  int wake_time_in_s=wake_hou*3600+wake_min*60+wake_sec;
  int sleep_time_in_s=sleep_hou*3600+sleep_min*60+sleep_sec;

  
  if((now_time_in_s>=sleep_time_in_s) && (now_time_in_s<wake_time_in_s)){

    
    
    int uS_TO_S_FACTOR=1000000;  /* Conversion factor for micro seconds to seconds */
    int TIME_TO_SLEEP=wake_time_in_s-now_time_in_s ;       /* Time ESP32 will go to sleep (in seconds) */
    Serial.println(TIME_TO_SLEEP);
    esp_sleep_enable_timer_wakeup(TIME_TO_SLEEP * uS_TO_S_FACTOR);
    Serial.println("sleep activated");
    esp_deep_sleep_start();
    
    
    }
  
  if(sec%5 == 0){
    if(sec_check){
      Serial.print("Seconds :");
      Serial.println(sec);
      
      String DHT_SEND =readDHT();
      String BMP_SEND =readBMP();
      String RAIN_SEND =readRainMod();
      String LDR_SEND =readLDR();

      SEND.concat(DHT_SEND);
      SEND.concat(BMP_SEND);
      SEND.concat(RAIN_SEND);
      SEND.concat(LDR_SEND);

      Serial.print("Data Array :");
      Serial.println(SEND);
     
      sec_check=false;
    }
  }
  else{
      sec_check=true;
     }

  if(mins%15 == 0){
    if(min_check){
      //WifiSend(SEND);
      PASS=SEND;
      check_avail=true;
      Serial.print("min done :");
      Serial.println(mins);
      //Serial.println(SEND);
      min_check=false;
      SEND="X-";
      SEND.concat(timeGet);
      SEND=SEND+"-A-";
    }
    }
  else{
      min_check=true;
     }
  } 
}


//====================================================================
//              task2() - wifi send data
//====================================================================
void Task2code( void * pvParameters ){
  for(;;){
    //Serial.println("Data Send started !");
    if(check_avail){
        WifiSend(PASS);
        Serial.print("Data Send completed !");
        Serial.println(PASS);
        appendFile(SD, "/DataStreamArray.txt", PASS+"\n");
        check_avail=false;
        PASS="";
      }else{
        delay(500);
        }
  }
}


void loop() {

}
