#include "byzance.h"
#include "RGB_matrix.h"


#define  PIN_R1   X00
#define  PIN_G1   X01
#define  PIN_B1   X02
#define  PIN_R2   X03
#define  PIN_G2   X04
#define  PIN_B2   X05
#define  PIN_A    X06
#define  PIN_B    X07
#define  PIN_C    X08
#define  PIN_D    X09
#define  PIN_CLK  X10
#define  PIN_LAT  X11
#define  PIN_OE   X12


void bin_busy(bool busy);

// Get actual time
struct tm * get_time(){
   time_t time_utc;
   time_t time_local;
   struct tm *p_local;

   p_local  = (tm*)malloc(sizeof(tm));

   // load UTC time to variable
   time(&time_utc);

   int timeoffset;
    Byzance::get_timeoffset(&timeoffset);

    // calculate local time using timeoffset getter
   time_local = time_utc + timeoffset;

   // convert localtime from timestamp to time struct
   memcpy(p_local, gmtime(&time_local), sizeof(tm));
    return  p_local;
}

// Draws disabled piture at line line
void draw_disabled(int line){
  char disabled [] = 
{0,0,0,1,1,0,0,
0,0,0,1,0,0,0,
0,0,1,1,1,1,0,
0,1,0,1,0,0,0,
0,1,0,1,1,0,0,
0,1,0,0,1,1,0,
0,0,1,1,0,0,1};
  for(int k=0; k<7; k++){
    for(int i=0; i<7; i++){
     if(disabled[k*7+i]){
       RGB_matrix::set_pixel(11+i, (line-1)*8+k, GREEN);
     }
    }
  }
}

// Draws NOTdisabled picture at line line
void draw_NOTdisabled(int line){
  char NOTdisabled [] = 
{1,0,0,1,1,0,0,
0,1,0,1,0,0,0,
0,0,1,1,1,1,0,
0,1,0,1,0,0,0,
0,1,0,1,1,0,0,
0,1,0,0,1,1,0,
0,0,1,1,0,0,1};
  for(int k=0; k<7; k++){
    for(int i=0; i<7; i++){
     if(NOTdisabled[k*7+i]){
       RGB_matrix::set_pixel(11+i, (line-1)*8+k, RED);
     }
    }
  }
}

// Resets the place where was disabled to empty
void draw_black(int xStart, int yStart){
  for(int k=0; k<7; k++){
    for(int i=0; i<7; i++){
     RGB_matrix::set_pixel(xStart+i, yStart+k, NONE);
    }
  }
}

// Writes text text in color color at line line
void lineColor(char *text, char color, int line){
  RGB_matrix::set_color(color);
  RGB_matrix::put_line(text, line);
}

// Writes char character in color color on the last space in line line
void lastChar(char character, char color, int line){
  RGB_matrix::set_color(color);
  RGB_matrix::put_char(59, (line-1)*8, character);
}

// Writes char character in color color on the space before last space in line line
void beforeLastChar(char character, char color, int line){
  RGB_matrix::set_color(color);
  RGB_matrix::put_char(53, (line-1)*8, character);
}

// Writes char routeNum in color color on the beginning of the line line
void routeNumber(char *routeNum, char color, int line){
  RGB_matrix::set_color(color);
  RGB_matrix::put_line(routeNum, line);
}

// Global counter for characters
unsigned int charCount = 0;
unsigned int shift = 0;
// Displays rolling char routeNam in color color on the line line (with free space for routeNumber, disabled, lastChars)
void routeName(char *routeNam, char color, int line){
  RGB_matrix::set_color(color);
  int lenName = strlen(routeNam); 
  RGB_matrix::put_char(19, (line-1)*8, ' ');
  for(int i=0; i<5; i++){
     RGB_matrix::put_char(19+6-shift+i*6, (line-1)*8, routeNam[(i+charCount) % lenName]);
     }
}

// Displays rolling char text in color color on the line line, first pixel on place int xStart
void rollText(char *text, char color, int xStart, int line){
  RGB_matrix::set_color(color);
  int lenText = strlen(text);
  RGB_matrix::put_char(xStart, (line-1)*8, ' ');
  for(int i=0; i<5; i++){
     RGB_matrix::put_char(xStart+6-shift+i*6, (line-1)*8, text[(i+charCount) % lenText]);
     }
}

void init(){

   //Initialization of the static class of the display
   RGB_matrix::Init(PIN_R1,PIN_R2,PIN_G1,PIN_G2,PIN_B1,PIN_B2,PIN_CLK,PIN_LAT,PIN_OE,PIN_A,PIN_B,PIN_C,PIN_D);

   /* Is very handy to attach this callback to RGB_Matrix ticker, when you need to
   update program from cloud. Inner ticker of the RGB_Matrix class could block the update process at the background
   */
   Byzance::attach_bin_busy(&bin_busy);

   // Chenge the color of text
   RGB_matrix::set_color(RGB_MATRIX_COLOR::GREEN);
   // Change the color of background
   RGB_matrix::set_background(RGB_MATRIX_COLOR::NONE);
}

void loop(){
   struct tm * time;
   time = get_time();

   char routeNum1[] = "20";
   char routeNum2[] = "16";
//   char routeNum3[] = "12";
   char routeNum4[] = "3!";

   char routeNam1[] = "SIDLISTE BARRANDOV   ";
   char routeNam2[] = "LEHOVEC   ";
//   char routeNam3[] = "VYSTAVISTE HOLESOVICE   ";
   char routeNam4[] = "VYLUKA - POUZIJTE LINKU 5 ZE ZASTAVKY MORAN   ";

   char line4[15];
   sprintf(line4, "        %d:%02d", time->tm_hour, time->tm_min);
   free(time);
   lineColor(line4, PINK, 4);

   char text[] = "V useku Lihovar - Hlubocepy ocekavejte zpozdeni 4 minuty   ";
   rollText(text, PINK, 0, 4);

   draw_disabled(1);
   draw_NOTdisabled(2);

   routeNumber(routeNum1, GREEN, 1);
   routeNumber(routeNum2, YELLOW, 2);
//   routeNumber(routeNum3, YELLOW, 3);
   routeNumber(routeNum4, RED, 3);

   routeName(routeNam1, GREEN, 1);
   routeName(routeNam2, YELLOW, 2);
//   routeName(routeNam3, YELLOW, 3);
   routeName(routeNam4, RED, 3);
   
   lastChar('1', GREEN, 1);
   beforeLastChar('1', YELLOW, 2);
   lastChar('0', YELLOW, 2);
//   beforeLastChar('1', YELLOW, 3);
   lastChar('8', RED, 3);

   // Set one pixel (x, y, color)
   //RGB_matrix::set_pixel(0,0,LIGHT_BLUE);

   // Put char on the coordinates (50,20)
   //RGB_matrix::put_char(50,20,'!');
   shift++;
   if (shift == 6){
    charCount++;
    shift = 0;
   }
   Thread::wait(100);
}


void bin_busy(bool busy){
   if(busy){
          RGB_matrix::detach_ticker();
   }else {
     RGB_matrix::attach_ticker();
   }
}