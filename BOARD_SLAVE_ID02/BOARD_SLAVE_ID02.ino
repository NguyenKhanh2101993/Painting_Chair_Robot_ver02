#include "ModbusSlave.h"
#include "Config_slaves.h"
#include "StepperMotorBresenham.h"
//================================================================
//================================================================
#define ARDUINO_ADDRESS             2    // Dia chi board arduino slaver can dieu khien
// Mode Block Run: sẽ chạy liên tục một nhóm các point từ vị trí G05.0 đến vị trí G05.1 trong file .pnt
// Sẽ lưu các điểm đó vào bộ nhớ tạm packet_data để chạy.
#define MAX_POINT_IN_BLOCK          150   // Số điểm tối đa có thể lưu trong packet_data khi chạy mode block run
Modbus node_slave(MODBUS_SERIAL, ARDUINO_ADDRESS, MODBUS_CONTROL_PIN);       
//================================================================
Motor Motor_X; 
Motor Motor_Y; 
Motor Motor_Z; 
Motor Motor_A; 
Motor Motor_B;
Motor Motor_C;

World command_motor(&Motor_X);
//================================================================
String userInput ="";
bool coil[128]; uint8_t coil_size = sizeof(coil) / sizeof(coil[0]); // Khai bao số lượng coil dùng cho write single coil

uint8_t coilY[] = {Y1, Y2, Y3, Y4, Y5, Y6, Y7, Y8, Y9, Y10, Y11, Y12, Y13, Y14, Y15, Y16};
uint8_t coilX[] = {X1, X2, X3, X4, X5, X6, X7, X8, X9, X10, X11, X12, X13, X14, X15, X16};
uint8_t coilY_size = sizeof(coilY)/sizeof(coilY[0]);
uint8_t coilX_size = sizeof(coilX)/sizeof(coilX[0]);
int16_t speed;                     // Lưu tốc độ trục X,Y,Z,A,B,C cần chạy nhận từ modbus
int32_t xung_nguyen[MAX_AXIS];      // Lưu số xung trục X,Y,Z,A,B,C cần chạy nhận từ modbus
// mảng 2 chiều: 
// pulseX0 pulseY0 pulseZ0 pulseA0 pulseB0 pulseC0 speed0
// pulseX1 pulseY1 pulseZ1 pulseA1 pulseB1 pulseC1 speed1
// ...
static int32_t packet_data[MAX_POINT_IN_BLOCK][MAX_AXIS+1]; 
// Mảng 2 chiều (20 hàng, 5 cột) lưu packet xung 20 điểm, cột thứ 7 lưu giá trị tốc độ speed
bool STATE_RUN_BLOCK = false; // chế độ chạy theo block có N điểm đã lưu sẵn
static bool blockmovingDone = false; // cờ báo đã chạy xong 1 block N điểm liên tục
// biến lưu số xung của rotary encoder
int32_t pulsecounter = 0;
uint16_t write_output_value; // giá trị coilY cần out 
uint16_t monitor_input_value; uint16_t monitor_output_value; 
uint8_t static start_address = 0;
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
    uint16_t data_CDG;    data_CDG = data_input_C | data_input_D | (data_input_G << 4);
    static uint16_t data_input;  data_input = data_input_K | data_CDG << 8;
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
    uint16_t data_AH;       data_AH = data_output_A | (data_output_H >>5);
    uint16_t data_CDBJ;     data_CDBJ = data_output_C | data_output_D | (data_output_B >> 2) | (data_output_J >> 4);
    static uint16_t data_output;   data_output = data_AH << 8| data_CDBJ;
    return data_output;
}
//================================================================
//================================================================
// Điều khiển motor về vị trí 0 đã set
void go_to_zero_position(void) {
  if (command_motor.movingDone()){
    command_motor.moving(0,0,0,0,0,0,120); 
  }
}
//================================================================
// set 0 cho các trục x,y,z,a làm điểm zero position
void set_zero_position(void) {
  command_motor.set_zero_position();
}
//================================================================
// test vi trí 1
void go_to_1_position(void) {
  if (command_motor.movingDone()){
    Serial.println("Chay dong co position 1");
    command_motor.moving(0,0,0,32000,0,0,200);
  }
}
// test vi trí 2
void go_to_2_position(void) {
  if (command_motor.movingDone()){
    Serial.println("Chay dong co position 2");
    command_motor.moving(32000,32000,32000,-32000,0,0,200);
  }
}
//================================================================
// Run main point to point, speed giá trị từ 0 - 200, lệnh chạy point to point 
void execute_point_to_point(int32_t *pulse, uint16_t _speed) {
  static int32_t target_pos[MAX_AXIS]; // Lưu vị trí cần chạy tới theo đơn vị xung
  if (!STATE_RUN_BLOCK) {
    for (int i = 0; i < MAX_AXIS; i++) {
      target_pos[i] = pulse[i] + command_motor.motor[i]->currentPosition;
    }
    if (command_motor.movingDone()){
        command_motor.moving(target_pos[0],target_pos[1],target_pos[2],
                            target_pos[3],target_pos[4],target_pos[5],_speed);
    }
  }
}
//================================================================
// Dừng động cơ ở vị trí bất kỳ
void resume_motor(void) {
  if (!command_motor.movingDone()){
    command_motor.resumeMoving();
  }
}
void pause_motor(void){
  if (!command_motor.movingDone()){
    command_motor.pauseMoving(0);
  }
}
void stop_motor(void){
  if (!command_motor.movingDone()){ // neu movingDone = 0
    //Serial.println("stop");
    command_motor.pauseMoving(1); // dừng động cơ, tắt timer
  }
}
//================================================================
// Command bắt đầu chạy một block N điểm đã lưu trong packet data
void change_state_run_block(void){
    STATE_RUN_BLOCK = !STATE_RUN_BLOCK; //Serial.println(STATE_RUN_BLOCK);
    if (STATE_RUN_BLOCK) { 
      command_motor.re_init_params();
      TIMER1_INTERRUPTS_ON; start_address = 0;}
    else { blockmovingDone = false; start_address = 0; }
}

//================================================================
// Lưu packets 20 điểm cần chạy. tay máy sẽ chạy từ điểm 1 tới 20 sau đó quay lại chạy điểm 1.
// Nhờ vậy sẽ tối ưu thời gian chờ nhận giá trị từ máy tính để chạy điểm tiếp theo, để giảm hiện tượng motor bị giật
// Lưu giá trị bao gồm xung và speed vào mảng 2 chiều packet_data[20][7] ở hàng thứ index
// Chỉ được dùng trong chế độ auto
void save_packet_data(int32_t *pulse, int16_t _speed){
 
  if (start_address < MAX_POINT_IN_BLOCK) {
    // lưu giá trị xung
    for (int i = 0; i < MAX_AXIS; i++){
      packet_data[start_address][i] = pulse[i];
    }
    // lưu giá trị speed
    packet_data[start_address][MAX_AXIS] = _speed;
    //Serial.println(packet_data[start_address][MAX_AXIS]);

    start_address++; 
    if (start_address == MAX_POINT_IN_BLOCK || _speed < 0 ) { start_address = 0;}
  }
}
//================================================================
// Truy xuất giá trị xung và speed ở hàng thứ index của mảng 2 chiều đang lưu data của xung và speed
// Nếu trong packet_data, giá trị speed = 0, là tín hiệu kết thúc chạy auto.
int32_t *get_packet_data(uint8_t index){
  static int32_t get_data[MAX_AXIS + 1];
  for (int i = 0; i < MAX_AXIS + 1; i++) { 
    get_data[i] = packet_data[index][i];
  }
  return get_data;
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
      OCR1A = command_motor.setDelay2();   // setting delay between steps
      TCNT1 = 0;
      command_motor.execute_one_pulse();
  }
  // nếu đã chạy xong 1 packet data (command_motor.movingDone() == true)
  // kiểm tra chế độ auto mode để chạy tiếp hoặc cho tắt ngắt timer1
  else { 
        if (STATE_RUN_BLOCK == true) { 
          int32_t *get_data; static uint8_t counter_line = 0; int32_t target[MAX_AXIS];

          get_data = get_packet_data(counter_line);
          counter_line++; if (counter_line == MAX_POINT_IN_BLOCK) {counter_line = 0;}
          
          for (int i = 0; i < MAX_AXIS; i++) { target[i] = get_data[i] + command_motor.motor[i]->currentPosition;}
          
          if (get_data[MAX_AXIS] < 0) { // giá trị tốc độ -1 -> tín hiệu kết thúc auto, chạy về zero
            blockmovingDone = true; counter_line = 0; TIMER1_INTERRUPTS_OFF;
            //Serial.println("END RUN BLOCK MODE");
          }
         
          else { command_motor.moving(target[0],target[1],target[2],target[3],target[4],target[5],get_data[6]);} 
        }
        else { TIMER1_INTERRUPTS_OFF; }
      }
}
//============================================================================================
void change_state_spray(void){


}
//============================================================================================
// Ghi giá trị coilY ra cổng OUTPUT: 0000 0000 0000 0000; 16 cổng, giá trị 16 bit
void change_state_coilY(uint16_t value){
  PORTA_OUT = (PORTA_OUT & ~(B11111101)) | ((value >> 2) & 0x00FF);

}
//============================================================================================
void setup() {   
  Serial.begin(115200);
  MODBUS_SERIAL.begin(MODBUS_BAUDRATE); node_slave.begin(MODBUS_BAUDRATE); function_modbus_slave();
  pinMode(EncoderA, INPUT_PULLUP); pinMode(EncoderB, INPUT_PULLUP);
  for (int i = 0; i < coilY_size; i++) { pinMode(coilY[i],OUTPUT); digitalWrite(coilY[i],LOW);}
  for (int i = 0; i < coilX_size; i++) { pinMode(coilX[i], INPUT_PULLUP); }
  command_motor.addMotor(&Motor_Y); command_motor.addMotor(&Motor_Z); command_motor.addMotor(&Motor_A);
  command_motor.addMotor(&Motor_B); command_motor.addMotor(&Motor_C);
  pinMotor_init();
  timer1_setting();
  Serial.println("Slave id2 Setup OK");
}
//============================================================================================
//============================================================================================
void loop() { 
  // nên đưa hàm poll vào vòng loop trong trường hợp monitor data về máy tính. không nên dùng ngắt để chạy poll. 
  node_slave.poll();
  monitor_input_value = read_input_register();
  monitor_output_value = read_output_register();
  /*
  //Serial.println(command_motor.motor[3]->currentPosition);
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
*/

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
    // Địa chỉ 0 nhận số xung cần chạy cho trục x,y,z,a,b,c
    case PULSE_EXECUTE: for (int i = 0; i <  MAX_AXIS; i++) { xung_nguyen[i] = i32readdata[i];} 
                                                              speed = i32readdata[MAX_AXIS]; break;   
    // Ghi giá trị coil Y ra các chân đã define
    case WRITE_YCOIL:   write_output_value = read_data[0]; break;
    default: break;
  }

  return STATUS_OK;     
}
//============================================================================================
// Handle the function code Read Holding Registers (FC=03) and write back the values from the EEPROM (holding registers).
//============================================================================================
uint8_t readMemory(uint8_t fc, uint16_t address, uint16_t length)
{
    uint16_t value[32]; uint8_t count; count = 0;
    if (address < 0 ||(address + length) > 32) { return STATUS_ILLEGAL_DATA_ADDRESS; }
    switch (address) {
      case CURRENT_POSITION_MODBUS_ADDR: 
            for (int i = 0; i < MAX_AXIS; i++) { 
              value[count++] = highWord(command_motor.motor[i]->currentPosition);
              value[count++] = lowWord(command_motor.motor[i]->currentPosition);
            } break;
      case ROTARY_ENCODER_MODBUS_ADDR:
            value[0] = highWord(pulsecounter);
            value[1] = lowWord(pulsecounter);
            break;
      case INPUT_OUTPUT_VALUE_MODBUS_ADDR:
            value[0] = monitor_input_value;
            value[1] = monitor_output_value;
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
  // Check if the requested addresses exist in the array
  if (address > coil_size || (address + length) > coil_size) { return STATUS_ILLEGAL_DATA_ADDRESS; }
  // Set the output pins to the given state.

  for (int i = 0; i < length; i++) {
      if (address + i < COIL_Y1_FIRST_MODBUS_ADDR) { // địa chỉ nhỏ hơn 32 thì nhận lệnh force single coil
        coil[address+i] = node_slave.readCoilFromBuffer(i);
        if (coil[address+i] == 1){
            switch (address + i) {
              case SPRAY_ONOFF_MODBUS_ADDR:           change_state_spray(); break;
              case POINT2POINT_MODBUS_ADDR:           execute_point_to_point(xung_nguyen,speed); break;
              case PAUSE_MOTOR_MODBUS_ADDR:           pause_motor(); break;
              case DISABLE_ROTARY_ENCODER_ADDR:       detach_rotary_encoder();  break;
              case ENABLE_ROTARY_ENCODER_ADDR:        attach_rotary_encoder(); break;
              case ENABLE_HOME_MOBUS_ADDR:            go_to_zero_position(); break;  // về vị trí cảm biến gốc máy
              case SET_ZERO_POSITION_ADDR:            set_zero_position(); break;    // set 0 tọa độ chương trình
              case STOP_MOTOR_MODBUS_ADDR:            stop_motor(); break;
              case RESUME_MOTOR_MODBUS_ADDR:          resume_motor(); break;
              case SAVE_PACKET_DATA_MODBUS_ADDR:      save_packet_data(xung_nguyen,speed); break;
              case CHANGE_STATE_RUN_BLOCK_MODBUS_ADDR: change_state_run_block(); break;
              case CHANGE_STATE_COIL_Y_MODBUS_ADDR:    change_state_coilY(write_output_value); break;
              default: break;
          }
        } 
      } else { // địa chỉ lớn hơn 32 thì nhận lệnh force mutiple coil cho coil vật lý output Y
        digitalWrite(coilY[(address+i)-COIL_Y1_FIRST_MODBUS_ADDR],node_slave.readCoilFromBuffer(i));
        }
  }
  return STATUS_OK;
}
//============================================================================================
// Handle the function codes Read Input Status (FC=01/02) and write back the values from the digital pins (input status).
uint8_t readDigital(uint8_t fc, uint16_t address, uint16_t length)
{
  bool state_home; state_home = false;
  // Check if the requested addresses exist in the array
  if (address > coil_size || (address + length) > coil_size) { return STATUS_ILLEGAL_DATA_ADDRESS; }
  for (int i = 0; i < length; i++) {
    if (address +i < COIL_Y1_FIRST_MODBUS_ADDR){
      switch (address+i) {
        case EXECUTE_PULSE_DONE:
              if (STATE_RUN_BLOCK == true) {state_home = blockmovingDone;}
              else                         {state_home = command_motor.movingDone();}
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