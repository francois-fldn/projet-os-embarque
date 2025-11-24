/*
 * --------------------------------------------------------------------------------
 * "THE BEER-WARE LICENSE" (Revision 42):
 * <julien.deantoni@univ-cotedazur.fr> wrote this file.
 * As long as you retain this notice you can do whatever you want with this stuff.
 * If we meet some day, and you think this stuff is worth it,
 * you can buy me a beer in return.  Julien Deantoni
 * --------------------------------------------------------------------------------
 */

#include <avr/io.h>
#include <util/delay.h>
#include <avr/interrupt.h>


/**
 * an active delay function to illustrate but should not be used in real code 
 * (use _delay_ms/_delay_us from <util/delay.h> instead) 
 **/
unsigned char Delay (unsigned long a);

//usefull def to ease the reading
#define emitter0 _BV(PD4)
#define receiver0 _BV(PD2)
#define blueLED _BV(PD7)

extern "C" {
    ISR(PCINT1_vect)
    {
        cli();
        if (PINC & (1 << PC0)) {
            PORTD |= blueLED; // allumer led
        } else {
            PORTD &= ~blueLED; // eteindre led
        }
    }
}
    
int main(void)
{
    DDRD=0b11111011; //D2 as input, all the other as outputs 
    DDRC &= ~(1 << PC0);   // PC0 en entrée
    sei();
    
    PCICR |= (1 << PCIE1);
    PCMSK1 |= (1 << PCINT8);
    
    PORTD = 0;

    
    //this section correspond to the loop part in arduino
    while(true)
    {   
       PORTD ^= emitter0;
       _delay_ms(500);
    }
}

unsigned char Delay (unsigned long a) 
{
    unsigned long b;
    for(b=0;b<a;b++){
    };
    return 1;
}
