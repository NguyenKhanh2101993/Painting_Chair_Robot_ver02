#include "ModbusSlave.h"
#include "Config_slaves.h"
#include "Config_motor.h"
#include "StepperMotorBresenham.h"
//================================================================
//================================================================
#define ARDUINO_ADDRESS             2    // Dia chi board arduino slaver can dieu khien
Modbus node_slave(MODBUS_SERIAL, ARDUINO_ADDRESS, MODBUS_CONTROL_PIN);       
//================================================================
Motor Motor_X(setDir_X, onePulse_X);
Motor Motor_Y(setDir_Y, onePulse_Y);
Motor Motor_Z(setDir_Z, onePulse_Z);
Motor Motor_A(setDir_A, onePulse_A);

World command_motor(&Motor_X);
//================================================================
String userInput ="";
bool coil[128]; uint8_t coil_size = sizeof(coil) / sizeof(coil[0]); // Khai bao số lượng coil dùng cho write single coil
uint8_t coilY[] = {Y1, Y2, Y3, Y4, Y5, Y6, Y7, Y8, Y9, Y10, Y11, Y12, Y13, Y14, Y15, Y16};
uint8_t coilX[] = {X1, X2, X3, X4, X5, X6, X7, X8, X9, X10, X11, X12, X13, X14, X15, X16};
uint8_t coilY_size = sizeof(coilY)/sizeof(coilY[0]);
uint8_t coilX_size = sizeof(coilX)/sizeof(coilX[0]);
uint16_t speed;  // Lưu tốc độ trục X,Y,Z,A cần chạy nhận từ modbus
int32_t xung_nguyen[4]; // Lưu số xung trục X,Y,Z,A cần chạy nhận từ modbus
// biến lưu số xung của rotary encoder
int32_t pulsecounter = 0;
uint16_t sensor_value; uint16_t output_value;
static uint32_t monitor_cnt;
//===============================================================================================================
//===============================================================================================================
// Read the rotary encoder
void encoder() {
  uint8_t state_encoder_channel_B = PINA&B00000010; //digitalRead(EncoderB);
  switch (state_encoder_channel_B) {
    case 0: pulsecounter--; break;
    case 1: pulsecounter++; break;
    default: break;       
  }
}
// Enable interrupts number 4
void attach_rotary_encoder(void) {
  attachInterrupt(4, encoder, RISING); 
  pulsecounter = 0;
}
// Disable interrupts number 4
void detach_rotary_encoder(void) {
  detachInterrupt(4); // tắt ngắt 4
  pulsecounter = 0;
}
//================================================================
// Hàm đọc giá trị input
uint16_t read_input_register(void){
    static uint16_t data_input_K,data_input_C,data_input_D,data_input_G;
    data_input_K = PINK&B11111111; 
    data_input_C = PINC&B00111111; 
    data_input_D = PIND&B10000000; 
    data_input_G = PING&B00000100;
    uint16_t data_CDG = data_input_C | data_input_D | (data_input_G << 4);
    uint16_t data_input = data_input_K | data_CDG << 8;
    return data_input;
}
//================================================================
// Hàm đọc giá trị output
uint16_t read_output_register(void){
    static uint16_t data_output_A, data_output_C,data_output_D,data_output_H,data_output_B,data_output_J;
    data_output_A = PINA&B11111101; data_output_H = PINH&B01000000;
    data_output_C = PINC&B11000000; 
    data_output_D = PIND&B00001011; 
    data_output_B = PINB&B00010000;
    data_output_J = PINJ&B00000011;
    uint16_t data_AH = data_output_A | (data_output_H >>5);
    uint16_t data_CDBJ = data_output_C | data_output_D | (data_output_B >> 2) | (data_output_J >> 4);
    uint16_t data_output = data_AH << 8| data_CDBJ;
    return data_output;
}
//================================================================
// Thực hiện lệnh DELAY_STEP
void Execute_DelayStep(uint16_t delay_value){
    if (delay_value > 0){delay(delay_value);}
    else delay(1);
}            
//================================================================
// Điều khiển motor về vị trí 0 đã set
void go_to_zero_position(void) {
  if (command_motor.movingDone()){
    Serial.println("Chay dong co ve zero");
    command_motor.setSpeed_motor(200); 
    command_motor.moving(0,0,0,0,0,0); 
  }
}
//================================================================
// set 0 cho các trục x,y,z,a làm điểm zero position
void set_zero_position(void) {
  Serial.println("set 0");
  command_motor.set_zero_position();
}
//================================================================
// test vi trí 1
void go_to_1_position(void) {
  if (command_motor.movingDone()){
    Serial.println("Chay dong co position 1");
    command_motor.setSpeed_motor(200);
    command_motor.moving(-12800,0,0,0,0,0);
  }
}
// test vi trí 2
void go_to_2_position(void) {
  if (command_motor.movingDone()){
    Serial.println("Chay dong co position 2");
    command_motor.setSpeed_motor(200);
    command_motor.moving(-32000,32000,32000,32000,0,0);
  }
}
//================================================================
// Run main point to point, speed giá trị từ 0 - 200
void execute_point_to_point(int32_t *pulse, uint16_t _speed) {
  static int32_t target_xung_nguyen[MAX_AXIS]; // Lưu vị trí cần chạy tới theo đơn vị xung

  for (int i = 0; i < MAX_AXIS; i++) {
    target_xung_nguyen[i] = pulse[i] + command_motor.motor[i]->currentPosition;
   }

  if (command_motor.movingDone()){
    command_motor.setSpeed_motor(_speed); 
    command_motor.moving(target_xung_nguyen[0],target_xung_nguyen[1],target_xung_nguyen[2],target_xung_nguyen[3],0,0);
  }
}
//================================================================
// Dừng động cơ ở vị trí bất kỳ
void resume_motor(void) {
  command_motor.resumeMoving();
}
void pause_motor(void){
  command_motor.pauseMoving();
}
//================================================================
//================================================================
void function_modbus_slave(void){
    node_slave.cbVector[CB_READ_COILS] = readDigital;
    //node_slave.cbVector[CB_READ_DISCRETE_INPUTS] = readDigital;
    node_slave.cbVector[CB_WRITE_COILS] = writeDigitalOut;
    //node_slave.cbVector[CB_READ_INPUT_REGISTERS] = readAnalogIn;
    node_slave.cbVector[CB_READ_HOLDING_REGISTERS] = readMemory;
    node_slave.cbVector[CB_WRITE_HOLDING_REGISTERS] = writeMemory;
}
//================================================================
// Configure thanh ghi timer/counter 
// http://arduino.vn/bai-viet/411-timercounter-tren-avrarduino
//================================================================
/* 
TCNTn: Thanh ghi thực hiện đếm giá trị 
TCCRnA/B: Thanh ghi điều khiển:
+ CSn0,CSn1,CSn2: Cài đặt prescale
TIMSKn: Thanh ghi điều khiển ngắt. 
+ bit 5 - ICIEn: Input Capture Interrupt Enable - Cho phép ngắt khi dùng Input Capture.
+ bit 2 - OCIEnB: Output Compare Interrupt Enable 1 channel B -  Cho phép ngắt khi dùng Output Compare ở channel B.
+ bit 1 - OCIEnA: Output Compare Interrupt Enable 1 channel A -  Cho phép ngắt khi dùng Output Compare ở channel A.
+ bit 0 - TOIEn: Overflow Interrupt Enable 1 - Cho phép ngắt khi xảy ra tràn trên T/C.
*/
void timer1_setting(void){
  // timer 1 setting
    cli();
    TCCR1A = 0;
    TCCR1B = 0;
    TCCR1B |= (1 << WGM12);                   // CTC mode 4 OCR1A(TOP)
    //TCCR1B |= ((1 << CS12) | (0 << CS11) | (1 << CS10));    // clk/1024 prescaler
    TCCR1B |= ((0 << CS12) | (1 << CS11) | (1 << CS10));    // clk/64 prescaler (1 xung = 4 us)
    //TCCR1B |= ((0 << CS12) | (1 << CS11) | (0 << CS10));    // clk/8  prescaler
    sei();
}
/////////////////////////////////////////////////////////////////////////////
/// ISR
/// clk/64: 21 ~ 23 tick
/// clk/ 8: 200 tick
/// ISR에 진입할 때 TCNT는 0이 된다
/// đếm từ TCNT1 và so sánh với OCR1A cho tới khi TCNT1 = OCR1A thì sẽ có hàm ngắt xảy ra
/// trường hợp này TCNT1 ban đầu mặc định = 0
////////////////////////////////////////////////////////////////////////////
ISR(TIMER1_COMPA_vect) {
 
  if (!command_motor.movingDone()) { // nếu các motor vẫn chưa chạy xong
      OCR1A = uint16_t(command_motor.setDelay2());   // setting delay between steps
      TCNT1 = 0;
      command_motor.execute_one_pulse();
      //Serial.println(OCR1A);
  }
  else {
        //Serial.println("PULSE DONE"); 
        TIMER1_INTERRUPTS_OFF;
      }
}
//============================================================================================
//============================================================================================
void setup() {   
  Serial.begin(115200);
  MODBUS_SERIAL.begin(MODBUS_BAUDRATE); node_slave.begin(MODBUS_BAUDRATE); function_modbus_slave();
  pinMode(EncoderA, INPUT_PULLUP); pinMode(EncoderB, INPUT_PULLUP);
  for (int i = 0; i < coilY_size; i++) { pinMode(coilY[i],OUTPUT); digitalWrite(coilY[i],LOW);}
  for (int i = 0; i < coilX_size; i++) { pinMode(coilX[i], INPUT_PULLUP); }
  function_modbus_slave(); 
  command_motor.addMotor(&Motor_Y); command_motor.addMotor(&Motor_Z); command_motor.addMotor(&Motor_A);
  pinMotor_init();
  timer1_setting();
  Serial.println("Setup OK");
}
//============================================================================================
//============================================================================================
void loop() { 
  // nên đưa hàm poll vào vòng loop trong trường hợp monitor data về máy tính. không nên dùng ngắt để chạy poll. 
  //node_slave.poll();
  //sensor_value = read_input_register();
  //output_value = read_output_register();
  //Serial.println(command_motor.motor[0]->currentPosition);
  userInput = "";
  while (Serial.available() >0)
  {
    userInput += char(Serial.read());
    delay(2);
    
    if (userInput ==  "O")
    {
      go_to_zero_position();
    }
    if (userInput == "R"){
      set_zero_position();
    }
    if (userInput == "P"){ pause_motor();}
    if (userInput == "S") {resume_motor();}
    if (userInput == "1") {go_to_1_position();}
    if (userInput == "2") {go_to_2_position();}
  }

} // End loop
//============================================================================================
//============================================================================================
int32_t *convert_32bit_data(uint32_t *data, uint16_t length){
  static int32_t output_data[32];
  if (length == 1) {return 0;}
  for (int i = 0; i <  length/2; i++){
      output_data[i] = data[2*i] << 16 | data[2*i+1];
  }
  return output_data;
}
//============================================================================================
// Handle the function codes Write Holding Register(s) (FC=06, FC=16) and write data to the eeprom.
// Ghi giá trị vào eeprom địa chỉ bắt đầu từ address. số lượng data 16 bit: length
//============================================================================================
uint8_t writeMemory(uint8_t fc, uint16_t address, uint16_t length)
{
  uint32_t read_data[32];
  int32_t *i32readdata; 
  if (address < 0 || (address + length) > 32) { return STATUS_ILLEGAL_DATA_ADDRESS; }

  for (int i = 0; i < length; i++) {
    read_data[i] = node_slave.readRegisterFromBuffer(i);
  }
  i32readdata = convert_32bit_data(read_data,length);
  switch (address) {
    // Địa chỉ 0 nhận số xung cần chạy cho trục x,y,z,a
    case PULSE_EXECUTE: for (int i = 0; i <  MAX_AXIS; i++){ xung_nguyen[i] = i32readdata[i];}  break;   
    // Địa chỉ 10 nhận tốc độ cho trục x,y,z,a đơn vị % (0 - 200%)
    case FREQ_EXECUTE:  speed = read_data[0];  break;
    
    default: break;
  }
  return STATUS_OK;     
}
//============================================================================================
// Handle the function code Read Holding Registers (FC=03) and write back the values from the EEPROM (holding registers).
//============================================================================================
uint8_t readMemory(uint8_t fc, uint16_t address, uint16_t length)
{
    uint16_t value[length]; 
    if (address < 0 ||(address + length) > 32) { return STATUS_ILLEGAL_DATA_ADDRESS; }
    switch (address) {
      case PWM_VALUE_X_AXIS_MODBUS_ADDR: 
            value[0] = highWord(command_motor.motor[0]->currentPosition);
            value[1] = lowWord(command_motor.motor[0]->currentPosition); 
            break;
      case PWM_VALUE_Y_AXIS_MODBUS_ADDR:
            value[0] = highWord(command_motor.motor[1]->currentPosition);
            value[1] = lowWord(command_motor.motor[1]->currentPosition); 
            break;
      case PWM_VALUE_Z_AXIS_MODBUS_ADDR:
            value[0] = highWord(command_motor.motor[2]->currentPosition);
            value[1] = lowWord(command_motor.motor[2]->currentPosition); 
            break;
      case PWM_VALUE_A_AXIS_MODBUS_ADDR:
            value[0] = highWord(command_motor.motor[3]->currentPosition);
            value[1] = lowWord(command_motor.motor[3]->currentPosition);
            break;
      case ROTARY_ENCODER_MODBUS_ADDR:
            value[0] = highWord(pulsecounter);
            value[1] = lowWord(pulsecounter);
            break;
      case INPUT_OUTPUT_VALUE_MODBUS_ADDR:
            value[0] = sensor_value;
            value[1] = output_value;
            break;
    }
    for (int i = 0; i < length; i++){  
        node_slave.writeRegisterToBuffer(i, value[i]); // Write 16 bit data
    }
  return STATUS_OK;
}
//============================================================================================
// Handle the function codes Force Single coil (FC=05) and Force Multiple Coils (FC=15) and set the digital output pins (coils).
//============================================================================================
uint8_t writeDigitalOut(uint8_t fc, uint16_t address, uint16_t length)
{
  uint16_t address_index = address;  uint8_t xxx;
  // Check if the requested addresses exist in the array
  if (address > coil_size || (address + length) > coil_size) { return STATUS_ILLEGAL_DATA_ADDRESS; }
  // Set the output pins to the given state.

  for (int i = 0; i < length; i++) {
      if (address + i < COIL_Y1_FIRST_MODBUS_ADDR) { // địa chỉ nhỏ hơn 32 thì nhận lệnh force single coil
        coil[address+i] = node_slave.readCoilFromBuffer(i);
        if (coil[address+i] == 1){
            switch (address + i) {
              case SPRAY_ONOFF_MODBUS_ADDR:       break;
              case POINT2POINT_MODBUS_ADDR:       execute_point_to_point(xung_nguyen,speed); break;
              case PAUSE_MOTOR_MODBUS_ADDR:       pause_motor(); break;
              case DISABLE_ROTARY_ENCODER_ADDR:   detach_rotary_encoder();  break;
              case ENABLE_ROTARY_ENCODER_ADDR:    attach_rotary_encoder(); break;
              case ENABLE_HOME_MOBUS_ADDR:        go_to_zero_position(); break;  // về vị trí cảm biến gốc máy
              case SET_ZERO_POSITION_ADDR:        set_zero_position(); break;    // set 0 tọa độ chương trình
              case STOP_MOTOR_MODBUS_ADDR:         break;
              case RESUME_MOTOR_MODBUS_ADDR:      resume_motor(); break;
              default: break;
          }
        } else {
            switch (address + i){
              case SPRAY_ONOFF_MODBUS_ADDR: break;
              default: break;
            }
        }
      }
      else { // địa chỉ lớn hơn 32 thì nhận lệnh force mutiple coil cho coil vật lý output Y
        digitalWrite(coilY[(address+i)-COIL_Y1_FIRST_MODBUS_ADDR],node_slave.readCoilFromBuffer(i));
      }
  }
  return STATUS_OK;
}
//============================================================================================
// Handle the function codes Read Input Status (FC=01/02) and write back the values from the digital pins (input status).
uint8_t readDigital(uint8_t fc, uint16_t address, uint16_t length)
{
  bool state_home = false;
  // Check if the requested addresses exist in the array
  if (address > coil_size || (address + length) > coil_size) { return STATUS_ILLEGAL_DATA_ADDRESS; }
  for (int i = 0; i < length; i++) {
    if (address +i < COIL_Y1_FIRST_MODBUS_ADDR){
      switch (address+i) {
        case EXECUTE_PULSE_DONE:
              state_home = command_motor.movingDone();
              node_slave.writeCoilToBuffer(i,state_home);
              break;
        //default: break;
      } 
    } else { break; }
  }
  return STATUS_OK;
}
//============================================================================================
//end