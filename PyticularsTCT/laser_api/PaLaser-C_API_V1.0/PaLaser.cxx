#include <iostream>
#include <fstream>

#include <stdio.h>

#include <sstream>
#include <wchar.h>
#include <string.h>
#include <stdlib.h>
#include "hidapi.h"
#include "usbm3.h"

#pragma comment(lib, "USBM3.lib") 

int main(int argc, char* argv[])
{     
  // The PaLaser.exe is intended as a demonstrator how to use Particulars Laser
  // with Microsoft Visual C++. It only takes one parameter per each execution 
  // so setting the laser can require several calls.
  //
  // example:
  // PaLaser.exe -f 
  // 




  // see if the device is attached
  if(argc>1)
    {
  if(HIDDLL::isDeviceAttached()) 
    printf("Device is attached!\n");  
      else 
  { printf("Device is not attached!\n"); exit(0);} 

  // check if the laser is on

  if(HIDDLL::readLASERstate()) 
    printf("Laser in ON and running!\n");
  else
    printf("Laser in OFF!\n");
  
  // first see if the simple operation (single frequency is chosen) 

      if(!strcmp(argv[1],"-f") )
	{  
	 float freq=atof(argv[2]);
	 if(freq<=0) 
	   {
	     printf("Switching the laser OFF\n");
	     HIDDLL::LASERTurnOff();
	   }
	 else 
	   {
	      HIDDLL::SetFrequency(atof(argv[2]));
   	      printf("Frequency set to %d Hz\n",(int) freq);
	   }
	}

      if(!strcmp(argv[1],"-off") )
	{
	  HIDDLL::LASERTurnOff();
	}

      if(!strcmp(argv[1],"-mc"))
	{
	  printf("Complex data taking - pulses controlled by MCU\n");
	  if(!strcmp(argv[2],"clear"))  {HIDDLL::LASERTurnOff(); HIDDLL::clearMCU(); printf("Sequence cleared\n");}
	  if(!strcmp(argv[2],"pulse"))     {HIDDLL::sendFreq( (atoi(argv[3])-440)/180  ); printf("Pulse duration set\n");}
	  if(!strcmp(argv[2],"start"))     {HIDDLL::seqMODE(1); printf("Sequence started\n");}
      	  if(!strcmp(argv[2],"file"))     {if(argc<4) HIDDLL::xselectFile(); else  HIDDLL::selectDefaultFile(argv[3]);}
      	  if(!strcmp(argv[2],"time"))     { 
	                                  HIDDLL::RITen();  
	                                  HIDDLL::sendInterruptPeriod( atoi(argv[3])); 
					  printf("Timer interupt ON :: Sequence timer %d\n",atoi(argv[3])); 
	                                  }

      	  if(!strcmp(argv[2],"ext"))     {   HIDDLL::RITdis();  printf("External interupt ON %d\n"); }
	    
	  
	}

      if(!strcmp(argv[1],"-p"))
	{
	  int DAC=atoi(argv[2]);
	  if(DAC>=0 && DAC<3300) 
	    {
	  printf("Turning the laser OFF ... ");
	  HIDDLL::LASERTurnOff(); 
	  printf("enabling DAC ... ");
	  HIDDLL::enableDAC();
	  printf("Pulse setting to DAC=%d mV [0-3300 mV]\n",DAC);
	  HIDDLL::setDAC(DAC);
	  
	    }
	  else
	    {
	      printf("Disabling DAC\n");
	      HIDDLL::disableDAC();
	    }
	  
	}

     if(!strcmp(argv[1],"-s"))
	{
	  printf("Laser state\n");
	  HIDDLL::acquireADC();
	  //	  double TempD = (double) HIDDLL::showADCData(3);
	  printf("T=%5.2f C\n",HIDDLL::showADCData(3)/10.);
	}


    }
  else 
    {
      printf("PaLaser [option] [arguments] \n");
      printf("[option] -off -> swithches off the laser\n\n");
      printf("[option] -f  -> single/simple frequency running \n");
      printf("[argument] value ; if frequency [value] is <0 laser is turned OFF \n\n");
      printf("[option] -mc  -> running the laser in microcontroller (MCU) mode \n");
      printf("[argument] clear ; clears the bit pattern in MCU memory\n");
      printf("[argument] start ; starts sequence in the MCU memory (timmer of extern interupt should be chosen)\n");
      printf("[argument] pulse + value; sets the time [value] between two pulses defined in the pattern file (frequency of the pulses)\n");
      printf("[argument] file + value; loads the bit pattern file [value]. The default file in streamfile.txt \n");
      printf("[argument] time + value; enables time interupt and sets the time in ms [value] between two sequences [frequency of the sequence]\n\n");

      printf("[option] -p  -> setting the pulse duration / amplitude");
      printf("[argument] value; sets the DAC value in mV \n\n");

      printf("[option] -s  -> reads the laser state - temperature\n.");
      printf("Note that the laser should be off when reading.\n");

    }
			// 	else
// 			       HIDDLL
//				 ::LASERTurnOff();			
			
				//			}

			//  HIDDLL::acquireADC();
   //    HIDDLL::clearMCU();
//       HIDDLL::selectSeqFile();
//       HIDDLL::seqMODE(1);
//       HIDDLL::CloseHID();

}
