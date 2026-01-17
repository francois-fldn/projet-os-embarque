INCLUDES=-I.
# ... (Vos includes existants) ...
INCLUDES+= -Iextra_libs
INCLUDES+= -IarduinoLibsAndCore/cores/arduino
INCLUDES+= -IarduinoLibsAndCore/libraries/Wire/src
INCLUDES+= -IarduinoLibsAndCore/libraries/Wire/src/utility
INCLUDES+= -IarduinoLibsAndCore/variants/standard
INCLUDES+= -IFreeRTOS-Kernel/include
INCLUDES+= -IFreeRTOS-Kernel/portable/GCC/ATMega328/

# Correction des vpath
vpath %.cpp arduinoLibsAndCore/libraries/Wire/src
vpath %.c arduinoLibsAndCore/libraries/Wire/src/utility
vpath %.c FreeRTOS-Kernel/
vpath %.c FreeRTOS-Kernel/portable/MemMang
vpath %.c FreeRTOS-Kernel/portable/GCC/ATMega328/
# ### AJOUT : Chemin vers le fichier assembleur (.S) du core Arduino
vpath %.S arduinoLibsAndCore/cores/arduino
BUILD_DIR=Build

CC=avr-gcc
CPP=avr-g++

MMCU=-mmcu=atmega328p

CFLAGS= -g -Os -w -std=gnu11 -ffunction-sections -fdata-sections -MMD -flto -fno-fat-lto-objects ${MMCU} -DF_CPU=16000000L -DARDUINO=10812 -DARDUINO_AVR_UNO -DARDUINO_ARCH_AVR
CPPFLAGS= -g -Os -w -std=gnu++11 -fpermissive -fno-exceptions -ffunction-sections -fdata-sections -fno-threadsafe-statics -Wno-error=narrowing -MMD -flto -w -x c++ -CC ${MMCU} -DF_CPU=16000000L -DARDUINO=10812 -DARDUINO_AVR_UNO -DARDUINO_ARCH_AVR

PROGRAM=RoomControl

# Ajout de Wire.o (C++) et twi.o (C) à la liste des objets
# Liste des objets
OBJS = $(BUILD_DIR)/timers.o \
       $(BUILD_DIR)/tasks.o \
       $(BUILD_DIR)/queue.o \
       $(BUILD_DIR)/list.o \
       $(BUILD_DIR)/croutine.o \
       $(BUILD_DIR)/heap_1.o \
       $(BUILD_DIR)/port.o \
       $(BUILD_DIR)/twi.o \
       $(BUILD_DIR)/Wire.o \
			 $(BUILD_DIR)/wiring_pulse_asm.o \
       $(BUILD_DIR)/main.o
# ^^^ AJOUT : wiring_pulse.o ajouté ci-dessus ^^^

all: ${PROGRAM}.elf ${PROGRAM}.hex 
	rm -f *.d

# Utilisation de la variable OBJS pour plus de clarté
${PROGRAM}.elf: $(OBJS)
	${CPP} -w -Os -g -flto -fuse-linker-plugin -Wl,--gc-sections ${INCLUDES} ${MMCU} $^ -o ${BUILD_DIR}/$@ -static -L./arduinoLibsAndCore -lres

arduinoLibsAndCore/libres.a:
	${MAKE} -C arduinoLibsAndCore

# Règle de compilation pour les fichiers C
${BUILD_DIR}/%.o: %.c
	@mkdir -p ${BUILD_DIR}/
	${CC} -c ${CFLAGS} ${INCLUDES} $< -o $@

# Règle de compilation pour les fichiers C++
${BUILD_DIR}/%.o: %.cpp
	@mkdir -p ${BUILD_DIR}/
	${CPP} -c ${CPPFLAGS} ${INCLUDES} $< -o $@

${BUILD_DIR}/%_asm.o: %.S
	@mkdir -p ${BUILD_DIR}/
	${CC} -c ${CFLAGS} ${INCLUDES} $< -o $@

OBJCOPY=avr-objcopy
 
${PROGRAM}.hex: ${BUILD_DIR}/${PROGRAM}.elf
	${OBJCOPY} -O ihex -R .eeprom  ${BUILD_DIR}/${PROGRAM}.elf ${BUILD_DIR}/$@

PORT=/dev/ttyACM0
 
upload: ${BUILD_DIR}/${PROGRAM}.hex
	avrdude -F -V -c arduino -p ATMEGA328P -P ${PORT} -b 115200 -U flash:w:${BUILD_DIR}/${PROGRAM}.hex;

clean:
	rm -Rf ${BUILD_DIR}

monitorSerial:
	screen -S arduinoMonitor ${PORT} 9600
killMonitor:
	screen -XS arduino quit