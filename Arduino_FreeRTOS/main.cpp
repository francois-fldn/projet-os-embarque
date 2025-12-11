//Arduino uno with base shield extension using FreeRTOS
/*  FreeRTOS V202112.00 */

#include <avr/io.h>
#include "FreeRTOS-Kernel/include/FreeRTOS.h" /* RTOS kernel functions. */
#include "task.h" /* RTOS task related API prototypes. */
#include "semphr.h" /* Semaphore related API prototypes. */


#include <util/delay.h>

#define Idle_Priority   (tskIDLE_PRIORITY)


//tasks handler defined after the main
//wait for an RFIFD card to be presented
static void WaitingTask( void *pvParameters );

//read the RFID card and send it so the master device

// static void RFIDTask( void *pvParameters );
// //blink an led every second to show the system is alive
// static void LEDTask( void *pvParameters );
// //open the door(led) for 5 seconds when a valid card is presented
// //and activate the ultrasound sensor
// static void DoorTask( void *pvParameters );
// //monitor the ultrasound sensor and close the door after 5 seconds, only 1 person allowed
// //in the doorway at a time
// static void UltrasoundTask( void *pvParameters );
// static void CounterTask( void *pvParameters );

//constant to ease the reading....
// const uint8_t doorLed = _BV(PD2);
// const uint8_t greenLed = _BV(PD4);
// const uint8_t ultrasoundSensor = _BV(PD6);
// // UNO D8 is PB0
// const uint8_t RFIDReader = _BV(PB0);
// // UNO D10 is PB2 (typically SPI SS)
// const uint8_t MasterDevice = _BV(PB2);

// --- Configuration ---
#define F_CPU 16000000UL // Fréquence d'horloge de 16MHz (Arduino Uno)
#define BAUD_RATE 9600

// Calcul du UBRR pour l'UART matériel (9600 bauds)
#define UBRR_VALUE ((F_CPU / 16 / BAUD_RATE) - 1)

// Définitions des broches SoftSerial
#define SOFTSERIAL_RX_PIN PIND6 // Arduino D2 (Broche PD2)
#define SOFTSERIAL_TX_PIN PIND7 // Arduino D3 (Broche PD3)

// Définitions de la LED (Ajouté)
#define LED_PIN _BV(PD4) // Broche D13 de l'Arduino Uno (Port B, bit 5)

// Période d'un bit pour 9600 bauds ≈ 104.16 µs
#define BIT_PERIOD_US 104

// Buffer
#define BUFFER_SIZE 64
unsigned char buffer[BUFFER_SIZE];
int count = 0;

#define UID_SIZE 16
unsigned char current_uid[UID_SIZE] = {0}; // Initialisé à zéro

// --- 1. Fonctions d'UART Matériel (Liaison PC) ---
void uart_init(unsigned int ubrr)
{
    UBRR0H = (unsigned char)(ubrr >> 8);
    UBRR0L = (unsigned char)ubrr;
    UCSR0B = (1 << RXEN0) | (1 << TXEN0);
    UCSR0C = (1 << UCSZ01) | (1 << UCSZ00);
}

void uart_tx(unsigned char data)
{
    while (!(UCSR0A & (1 << UDRE0)))
        ;
    UDR0 = data;
}

void uart_write_buffer(unsigned char *data, int len)
{
    for (int i = 0; i < len; i++)
        uart_tx(data[i]);
}

int uart_available() { return (UCSR0A & (1 << RXC0)); }

unsigned char uart_rx() { return UDR0; }

void softserial_init()
{
    DDRD &= ~(1 << SOFTSERIAL_RX_PIN);
    DDRD |= (1 << SOFTSERIAL_TX_PIN);
    PORTD |= (1 << SOFTSERIAL_TX_PIN);
}

int softserial_available() { return !(PIND & (1 << SOFTSERIAL_RX_PIN)); }

unsigned char softserial_read()
{
    unsigned char data = 0;
    while (PIND & (1 << SOFTSERIAL_RX_PIN))
        ;
    _delay_us(BIT_PERIOD_US / 2);

    for (int i = 0; i < 8; i++)
    {
        _delay_us(BIT_PERIOD_US);
        if (PIND & (1 << SOFTSERIAL_RX_PIN))
            data |= (1 << i);
    }
    _delay_us(BIT_PERIOD_US);
    return data;
}

void clearBufferArray()
{
    for (int i = 0; i < BUFFER_SIZE; i++)
        buffer[i] = 0;
}

int main(void){
    // DDRD |= (doorLed | greenLed); // PD2 and PD4 as outputs
    // DDRD &= ~ultrasoundSensor;    // PD6 as input
    // DDRB &= ~(RFIDReader | MasterDevice); // PB0 (D8) and PB2 (D10) as inputs

    // Create tasks
    xTaskCreate(
        WaitingTask,
        "WaitingTask",
        128,
        NULL,
        tskIDLE_PRIORITY + 1,
        NULL
    );

    // Start scheduler.
    vTaskStartScheduler();

    return 0;
}

// Minimal implementation so the project links
static void WaitingTask( void *pvParameters ){
    (void)pvParameters;
    while (1)
    {
        // ======tache 1======
        // reception infos carte
        if (softserial_available())
        {
            // Lecture des données SoftSerial (l'UID de la carte)
            while (softserial_available() && (count < BUFFER_SIZE))
                buffer[count++] = softserial_read();
            if (count > 0)
            {
                int uid_len = (count < UID_SIZE) ? count : UID_SIZE;
                // Copie manuelle de l'UID (équivalent à memcpy(current_uid, buffer, uid_len))
                for (int i = 0; i < uid_len; i++)
                    current_uid[i] = buffer[i];
                // S'assurer que la chaîne de caractères est terminée par un NULL (si le format est ASCII)
                if (uid_len < UID_SIZE)
                    current_uid[uid_len] = 0;
                PORTD ^= LED_PIN;
                clearBufferArray();
                count = 0;
            }
        }
        // ======tache 1======
    }
    // for(;;){
    //     // Simple heartbeat: toggle green LED every 500ms
    //     PORTD ^= greenLed;
    //     vTaskDelay(pdMS_TO_TICKS(500));
    // }
}
