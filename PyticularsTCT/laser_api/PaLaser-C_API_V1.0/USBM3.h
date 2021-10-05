#include <sstream>
#include <string.h>


using namespace std;

    

class HIDDLL
    { 
    private:
      	static void init();
      	static void SendDataToUSB();
      	static   int parseChar(unsigned char );
      	static   void ParseByte(string);
      	static   int openFile(char *);
      	static   void SendFile();	
      	static  void readADC();	
	    
    public:

		 /* This method is used to generate sequence  */
		static __declspec( dllexport ) void  seqMODE(int mode);

		/* This method is used to turn off LASER */
		static __declspec( dllexport ) void  LASERTurnOff(void);

		 /* This method is used to send freq data to ARM   */ 
		static __declspec( dllexport ) void  sendFreq(int freq);

		 /* This method is used to enable hardware sequence for ARM.   */ 
		static __declspec( dllexport ) void  hardSeqEn(void);

		 /* This method is used to disable hardware sequence for ARM.  */ 
		static __declspec( dllexport ) void  hardSeqDis(void);

                /* This method is used to clean sequence data for ARM   */ 
		static __declspec( dllexport ) void  clearMCU(void);  

		 // This is the method used for the activation of ADC. It returns value measured by ADC in ARM MCU
		static  __declspec( dllexport ) void acquireADC(void);


		 // This method is used for selecting, parsing and sending data to ARM MCU from selected file. It opens select file dialog where file can be selected.
		 // File should be formated properly. It should contain following markers:

		/*

		freq: 2											// marker for freq parameter followed by freq value

		seqLength: 344									// marker for length of the sequence parameter followed by seqLength value

		CH number: 4									// marker for selection of number for output channels. marker is followed by CH number value

		CH1:											// marker for channel data 
		byte_0  byte_1 .................. byte_15 ;		// chanell data
		byte_16  ........................ byte_31 ;		// chanell data
		  .                                .	                .
		  .                                .	                .
		  .                                .	                . 
		  .                                .	                .    	  
		  .                                .	                .
		byte_120 .......................  byte_127 ;	// chanell data

		CH2:											// marker for channel data 
		byte_0  byte_1 .................. byte_15 ;		// chanel2 data
		byte_16  ........................ byte_31 ;		// chanel2 data
		  .                                .	                .
		  .                                .	                .
		  .                                .	                . 
		  .                                .	                .    	  
		  .                                .	                .
		byte_120 .......................  byte_127 ;	// chanel2 data

		.                                  .
		.                                  .
		.                                  .
		.                                  .
		.                                  .
		.                                  .
		.                                  .
		 
		CH8:											// marker for channel data 
		byte_0  byte_1 .................. byte_15 ;		// chanel8 data
		byte_16  ........................ byte_31 ;		// chanel8 data
		  .                                .	                .
		  .                                .	                .
		  .                                .	                . 
		  .                                .	                .    	  
		  .                                .	                .
		byte_120 .......................  byte_127 ;	// chanel8 data

		*/

		static __declspec( dllexport ) void xselectFile(void);
		static __declspec( dllexport ) void selectDefaultFile(char* dFile);

	 // This method will configure interrupt type on ARM MCU.
		 // Method not yet implemented
		 static __declspec( dllexport ) void enableEXTInterrupt(void);

		 static __declspec( dllexport ) void disableEXTInterrupt(void);

		 // This method enables DAC on ARM MCU. Value set on DAC output will be 0x000 or last set data before disable command.
		 static __declspec( dllexport ) void enableDAC(void);

 // This method enables DAC on ARM MCU. Value set on DAC output will be 0x000
		 static __declspec( dllexport ) void disableDAC(void);


		 // This method sets the value for DAC. Value is int which will be set on DAC output
		static  __declspec( dllexport ) void setDAC(int value); 

		 /* This is method is for sending data for RIT COMPARE value */ 
		static  __declspec( dllexport ) void sendInterruptPeriod(long int value);

		 /* This is method that enables RIT */
		static  __declspec( dllexport ) void RITen(void);

		/* This is method that disables RIT */
		static  __declspec( dllexport ) void RITdis(void);

	/* This is method that show ADC data */
		static __declspec( dllexport ) double showADCData(int ch);

	/* This is method that check USB connection */
		static __declspec( dllexport ) bool isDeviceAttached(void);

		/* This is method that check the LASER state */
		static __declspec( dllexport ) bool readLASERstate(void);

	        /* This method is used to generate sequence  */
         	static __declspec( dllexport ) void  CloseHID(void);

		static __declspec( dllexport ) void  ReadADC(void);
	

		//        	static __declspec( dllexport ) int selectSeqFile(void);

		//static __declspec( dllexport ) void openDevice(void);

     //////////////////////////////////////////////////////////////////
     ///////////////  USER FUNCTIONS ///////////////////////////////////
     //////////////////////////////////////////////////////////////////
	
      	static __declspec( dllexport ) void SetFrequency(float );  // set frequency



    };
	

