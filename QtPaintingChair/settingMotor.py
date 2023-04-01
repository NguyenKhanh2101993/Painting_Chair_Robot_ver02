import json

class makeJsonSetting:
    def __init__(self):
        self.config = {}
        self.motorX = {}; self.motorY = {}; self.motorZ = {}
        self.motorA = {}; self.motorB = {}; self.motorC = {}
        self.gearRatio = [1,1,1,1,1,1]
        self.Xpins = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
        self.Ypins = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
        self.Xsensor = [1,1,1,1,1,1,1,1]
        self.Youtput = [1,1,1,1,1,1,1,1]

        self.config = {"motor": { 
                            "motorX": self.motorX, "motorY": self.motorY,  "motorZ": self.motorZ, 
                            "motorA": self.motorA,  "motorB": self.motorB,  "motorC": self.motorC },
                       "gearInfor": self.gearRatio,
                       "defineXpins": self.Xpins,
                       "defineYpins": self.Ypins,
                       "defineSensor": self.Xsensor,
                       "defineOutput": self.Youtput
                       }
#============================================================================================
    def getYoutputInfor(self):
        yOutputConfig = None
        with open('configFile.json', 'r') as f:
            configFile = json.load(f)
            yOutputConfig = configFile['defineOutput']
        f.close()
        return yOutputConfig
    
    def setYoutputInfor(self, value):
        for i in range(len(value)):
            self.Youtput[i] = value[i]
        with open('configFile.json', 'r') as f:
            configFile = json.load(f)
        f.close()
        configFile['defineOutput'] = self.Youtput
        with open('configFile.json', 'w') as f:
            json.dump(configFile,f)
        f.close()
#============================================================================================
    def getXsensorInfor(self):
        xSensorConfig = None
        with open('configFile.json', 'r') as f:
            configFile = json.load(f)
            xSensorConfig = configFile['defineSensor']
        f.close()
        return xSensorConfig
    
    def setXsensorInfor(self, value):
        for i in range(len(value)):
            self.Xsensor[i] = value[i]
        with open('configFile.json', 'r') as f:
            configFile = json.load(f)
        f.close()
        configFile['defineSensor'] = self.Xsensor
        with open('configFile.json', 'w') as f:
            json.dump(configFile,f)
        f.close()

#============================================================================================            
# truy xuất thông tin XY pins defined
    def getXpinsInfor(self):
        xPinsConfig = None
        with open('configFile.json', 'r') as f:
            configFile = json.load(f)
            xPinsConfig = configFile['defineXpins']
        f.close()
        return xPinsConfig
    
    def setXpinsInfor(self, value):
        for i in range(len(value)):
            self.Xpins[i] = value[i]
        with open('configFile.json', 'r') as f:
            configFile = json.load(f)
        f.close()
        configFile['defineXpins'] = self.Xpins
        with open('configFile.json', 'w') as f:
            json.dump(configFile,f)
        f.close()
#============================================================================================        
    def getYpinsInfor(self):
        yPinsConfig = None
        with open('configFile.json', 'r') as f:
            configFile = json.load(f)
            yPinsConfig = configFile['defineYpins']
        f.close()
        return yPinsConfig
    
    def setYpinsInfor(self, value):
        for i in range(len(value)):
            self.Ypins[i] = value[i]
        with open('configFile.json', 'r') as f:
            configFile = json.load(f)
        f.close()    
        configFile['defineYpins'] = self.Ypins
        with open('configFile.json', 'w') as f:
            json.dump(configFile,f)
        f.close()
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
        with open('configFile.json', 'r') as f:
            configFile = json.load(f)
            motorConfig = configFile['motor']
        f.close()
        motorConfig['motorX'] = self.motorX
        motorConfig['motorY'] = self.motorY
        motorConfig['motorZ'] = self.motorZ
        motorConfig['motorA'] = self.motorA
        motorConfig['motorB'] = self.motorB
        motorConfig['motorC'] = self.motorC
        configFile['motor'] = motorConfig
        with open('configFile.json', 'w') as f:
            json.dump(configFile,f)
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
        with open('configFile.json', 'r') as f:
            configFile = json.load(f)
        f.close()
        configFile['gearInfor'] = self.gearRatio
        with open('configFile.json', 'w') as f:
            json.dump(configFile,f)
        f.close()