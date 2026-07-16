// WinAmp · Physical Edition — RP2040 controls firmware (skeleton).
//
// Owns physical I/O + real-time motor loops for the motorized faders, and
// speaks the ASCII serial protocol in docs/serial-protocol.md.
//
// This is a STRUCTURAL skeleton: the protocol, control-loop shape, and mux
// scanning are real; pin numbers and PID gains are placeholders to tune on the
// bench. Bring up ONE fader on direct pins first (see firmware/README.md).
//
// NOTE (I/O architecture): the full build does NOT direct-wire everything — the
// Pico hasn't the pins (see hardware/wiring.md). Motors: 2x PCA9685 over I2C.
// Touch: MPR121. Buttons: MCP23017. OLED readout: SSD1322 over SPI, fed by the
// Pi's `DISP TITLE/TIME/INFO` commands. The MOTOR_PIN table below is only for
// the single-fader bring-up stage.

#include <Arduino.h>

// ----------------------------- configuration ------------------------------ //
static const uint8_t NUM_FADERS = 10;   // 0-6 EQ, 7 preamp, 8 volume, 9 seek
static const uint16_t FADER_MAX = 1023; // 10-bit ADC range reported to the Pi
static const uint32_t LOOP_HZ = 1000;   // PID update rate

// CD74HC4067 16-ch analog mux: 4 select lines + 1 common ADC input.
static const uint8_t MUX_S[4] = {2, 3, 4, 5};
static const uint8_t MUX_ADC = 26;      // GP26 / ADC0

// Per-fader H-bridge PWM pins {IN1, IN2}. Placeholders — set to your wiring.
static const uint8_t MOTOR_PIN[NUM_FADERS][2] = {
    {6, 7}, {8, 9}, {10, 11}, {12, 13}, {14, 15},
    {16, 17}, {18, 19}, {20, 21}, {22, 26 /*TODO*/}, {27 /*TODO*/, 28 /*TODO*/},
};
static const uint8_t FADER_MUX_CH[NUM_FADERS] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9};
static const uint8_t FADER_TOUCH_PIN[NUM_FADERS] = {
    /* TODO: touch-sense GPIOs per fader */ 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255,
};

// ------------------------------- PID state -------------------------------- //
struct Pid {
    float kp = 0.9f, ki = 0.0f, kd = 0.05f;
    float integ = 0.0f, prev_err = 0.0f;
    int16_t target = -1;    // -1 == released (motor off, user controls it)
    bool touched = false;
    uint16_t last_reported = 0xFFFF;

    float step(float measured, float dt) {
        float err = target - measured;
        integ += err * dt;
        float deriv = (err - prev_err) / dt;
        prev_err = err;
        return kp * err + ki * integ + kd * deriv;
    }
};
static Pid fader[NUM_FADERS];

// ------------------------------ mux + motor ------------------------------- //
static uint16_t readMux(uint8_t channel) {
    for (uint8_t i = 0; i < 4; i++) digitalWrite(MUX_S[i], (channel >> i) & 1);
    delayMicroseconds(5);               // let the mux settle
    return analogRead(MUX_ADC);         // 0..1023
}

static void driveMotor(uint8_t f, float effort) {
    // effort in [-255, 255]; sign = direction.
    int16_t pwm = constrain((int)effort, -255, 255);
    if (pwm >= 0) {
        analogWrite(MOTOR_PIN[f][0], pwm);
        analogWrite(MOTOR_PIN[f][1], 0);
    } else {
        analogWrite(MOTOR_PIN[f][0], 0);
        analogWrite(MOTOR_PIN[f][1], -pwm);
    }
}

static void motorOff(uint8_t f) {
    analogWrite(MOTOR_PIN[f][0], 0);
    analogWrite(MOTOR_PIN[f][1], 0);
}

// ----------------------------- serial protocol ---------------------------- //
static void emit(const char* type, int id, int value) {
    Serial.print("EV "); Serial.print(type); Serial.print(' ');
    Serial.print(id); Serial.print(' '); Serial.println(value);
}

static char rx[64];
static uint8_t rxlen = 0;

static void handleCommand(char* line) {
    // Pi -> MCU: "FADER <id> <pos>", "FADER_RELEASE <id>", "LED ...", "PING"
    char* verb = strtok(line, " ");
    if (!verb) return;
    if (!strcmp(verb, "PING")) {
        Serial.println("PONG");
    } else if (!strcmp(verb, "FADER")) {
        int id = atoi(strtok(nullptr, " "));
        int pos = atoi(strtok(nullptr, " "));
        if (id >= 0 && id < NUM_FADERS) fader[id].target = constrain(pos, 0, FADER_MAX);
    } else if (!strcmp(verb, "FADER_RELEASE")) {
        int id = atoi(strtok(nullptr, " "));
        if (id >= 0 && id < NUM_FADERS) fader[id].target = -1;
    } else if (!strcmp(verb, "LED")) {
        // TODO: drive WS2812 (index r g b)
    }
}

static void pollSerial() {
    while (Serial.available()) {
        char c = Serial.read();
        if (c == '\n') {
            rx[rxlen] = 0;
            handleCommand(rx);
            rxlen = 0;
        } else if (rxlen < sizeof(rx) - 1) {
            rx[rxlen++] = c;
        }
    }
}

// ----------------------------- inputs (stub) ------------------------------ //
static void scanButtonsAndEncoders() {
    // TODO: debounce buttons -> emit("BTN", id, pressed);
    // TODO: read encoders   -> emit("ENC", id, delta);
    // TODO: read touch pins -> on change, fader[id].touched = t; emit("TOUCH", id, t);
}

// --------------------------------- main ----------------------------------- //
void setup() {
    Serial.begin(SERIAL_BAUD);
    for (uint8_t i = 0; i < 4; i++) pinMode(MUX_S[i], OUTPUT);
    for (uint8_t f = 0; f < NUM_FADERS; f++) {
        pinMode(MOTOR_PIN[f][0], OUTPUT);
        pinMode(MOTOR_PIN[f][1], OUTPUT);
        motorOff(f);
    }
    analogReadResolution(10);
}

void loop() {
    static uint32_t last = 0;
    const uint32_t period_us = 1000000UL / LOOP_HZ;
    uint32_t now = micros();
    if (now - last < period_us) return;
    float dt = (now - last) / 1e6f;
    last = now;

    pollSerial();
    scanButtonsAndEncoders();

    for (uint8_t f = 0; f < NUM_FADERS; f++) {
        uint16_t pos = readMux(FADER_MUX_CH[f]);

        if (fader[f].touched || fader[f].target < 0) {
            motorOff(f);
            // Report user-driven movement (coarse threshold to avoid spam).
            if (abs((int)pos - (int)fader[f].last_reported) > 4) {
                emit("FADER", f, pos);
                fader[f].last_reported = pos;
            }
        } else {
            driveMotor(f, fader[f].step(pos, dt));
        }
    }
}
