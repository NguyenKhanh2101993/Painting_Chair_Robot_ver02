import json

class makeJsonSetting:
    def __init__(self):
        self.config = {}
        self.motorX = {}; self.motorY = {}; self.motorZ = {}
        self.motorA = {}; self.motorB = {}; self.motorC = {}
        self.gearRatio = [1,1,1,1,1,1]
        self.config = {"motor": { 
                            "motorX": self.motorX, "motorY": self.motorY,  "motorZ": self.motorZ, 
                            "motorA": self.motorA,  "motorB": self.motorB,  "motorC": self.motorC },
                       "gearInfor": self.gearRatio }
#============================================================================================
# truy xuat thong tin motor setting tu json        
    def getMotorInfo(self):
        motorSetting = []
        with open('configFile.json', 'r') as f:
            configFile = json.load(f) # load file json
            motorConfig = configFile['motor']      # truy xuất phần tử motor

            readMotorX = motorConfig['motorX']    # truy xuất phần tử motorX trong motor
            readMotorY = motorConfig['motorY']    # truy xuất phần tử motorY trong motor
            readMotorZ = motorConfig['motorZ']    # truy xuất phần tử motorZ trong motor
            readMotorA = motorConfig['motorA']    # truy xuất phần tử motorA trong motor
            readMotorB = motorConfig['motorB']    # truy xuất phần tử motorB trong motor
            readMotorC = motorConfig['motorC']    # truy xuất phần tử motorC trong motor
        motorSetting = [readMotorX, readMotorY, readMotorZ, readMotorA, readMotorB, readMotorC]
        f.close()
        return motorSetting
#============================================================================================
    def setMotorInfor(self, gear, microstep, diameter):
        # update giá trị
        self.motorX['gear'] = gear[0]; self.motorX['microStep'] = microstep[0];     self.motorX['diameter'] = diameter[0]
        self.motorY['gear'] = gear[1]; self.motorY['microStep'] = microstep[1];     self.motorY['diameter'] = diameter[1]
        self.motorZ['gear'] = gear[2]; self.motorZ['microStep'] = microstep[2];     self.motorZ['diameter'] = diameter[2]
        self.motorA['gear'] = gear[3]; self.motorA['microStep'] = microstep[3];     self.motorA['diameter'] = diameter[3]
        self.motorB['gear'] = gear[4]; self.motorB['microStep'] = microstep[4];     self.motorB['diameter'] = diameter[4]
        self.motorC['gear'] = gear[5]; self.motorC['microStep'] = microstep[5];     self.motorC['diameter'] = diameter[5]

        with open('configFile.json', 'w') as f:
            json.dump(self.config,f)
        f.close()
#============================================================================================
    def getGearRatio(self):
        gearCalculated = []
        try:
            with open('configFile.json', 'r') as f:
                configFile = json.load(f) # load file json
                gearCalculated = configFile['gearInfor']      # truy xuất phần tử gearInfor
            f.close()    
            
        except Exception as e:
            print("getGearRatio error: ", str(e))
        return gearCalculated
#============================================================================================
    def setGearInfor(self, value):
        for i in range(len(self.gearRatio)):
            self.gearRatio[i] = value[i]
        with open('configFile.json', 'w') as f:
            json.dump(self.config,f)
        f.close()