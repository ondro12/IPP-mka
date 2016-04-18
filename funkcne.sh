#!/usr/bin/env bash

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# IPP - mka - veřejné testy - 2012/2013
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Činnost: 
# - vytvoří výstupy studentovy úlohy v daném interpretu na základě sady testů
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

TASK=mka
#INTERPRETER=perl
#EXTENSION=pl
INTERPRETER=python3
EXTENSION=py

# cesta pro ukládání chybového výstupu studentského skriptu
LOCAL_OUT_PATH="."  
LOG_PATH="."


# test01: velmi jednoducha minimalizace; Expected output: test01.out; Expected return code: 0
$INTERPRETER $TASK.$EXTENSION --input=test01.in --output=$LOCAL_OUT_PATH/test01.out --minimize 2> $LOG_PATH/test01.err
echo -n $? > test01.!!!

# test02: slozitejsi minimalizace; Expected output: test02.out; Expected return code: 0
$INTERPRETER $TASK.$EXTENSION --input=test02.in --output=$LOCAL_OUT_PATH/test02.out -m 2> $LOG_PATH/test02.err
echo -n $? > test02.!!!

# test03: slozitejsi formatovani vstupniho automatu (dia); Expected output: test03.out; Expected return code: 0
$INTERPRETER $TASK.$EXTENSION --input=test03.in > $LOCAL_OUT_PATH/test03.out 2> $LOG_PATH/test03.err
echo -n $? > test03.!!!

# test04: hledani neukoncujiciho stavu (past, trap); Expected output: test04.out; Expected return code: 0
$INTERPRETER $TASK.$EXTENSION --output=$LOCAL_OUT_PATH/test04.out --find-non-finishing < test04.in 2> $LOG_PATH/test04.err
echo -n $? > test04.!!!

# test05: kontrola dobre specifikovanosti vstupniho automatu; Expected output: test05.out; Expected return code: 62
$INTERPRETER $TASK.$EXTENSION --input=test05.in --output=$LOCAL_OUT_PATH/test05.out 2> $LOG_PATH/test05.err
echo -n $? > test05.!!!

# test06: příklad konečného automatu ve vstupním formátu úlohy MKA (není dobře specifikovaný); Expected output: test06.out; Expected return code: 62
$INTERPRETER $TASK.$EXTENSION --input=test06.in --output=$LOCAL_OUT_PATH/test06.out 2> $LOG_PATH/test06.err
echo -n $? > test06.!!!

# test07: ukazka case-insensitive; Expected output: test07.out; Expected return code: 0
$INTERPRETER $TASK.$EXTENSION --input=test07.in --case-insensitive -m > $LOCAL_OUT_PATH/test07.out 2> $LOG_PATH/test07.err
echo -n $? > test07.!!!

# test08: chybna kombinace parametru -m a -f; Expected output: test08.out; Expected return code: 1
$INTERPRETER $TASK.$EXTENSION --input=test08.in --output=$LOCAL_OUT_PATH/test08.out --minimize -f 2> $LOG_PATH/test08.err
echo -n $? > test08.!!!

# test09: syntakticka chyba vstupniho formatu; Expected output: test09.out; Expected return code: 60
$INTERPRETER $TASK.$EXTENSION --input=test09.in --output=$LOCAL_OUT_PATH/test09.out --minimize 2> $LOG_PATH/test09.err
echo -n $? > test09.!!!

# test10: semanticka chyba vstupniho formatu (stav neni v mnozine stavu); Expected output: test10.out; Expected return code: 61
$INTERPRETER $TASK.$EXTENSION --input=test10.in --output=$LOCAL_OUT_PATH/test10.out 2> $LOG_PATH/test10.err
echo -n $? > test10.!!!

# test90: Bonus RLO - na vstupu pouze pravidla (bez rozsireni vraci chybu 1); Expected output: test90.out; Expected return code: 0
$INTERPRETER $TASK.$EXTENSION --input=test90.in --output=$LOCAL_OUT_PATH/test90.out --rules-only 2> $LOG_PATH/test90.err
echo -n $? > test90.!!!

# test91: Bonus WHT - oddeleni elementu nejen carkami, ale i bilymi znaky (bez rozsireni vraci chybu 1); Expected output: test91.out; Expected return code: 0
$INTERPRETER $TASK.$EXTENSION --input=test91.in --output=$LOCAL_OUT_PATH/test91.out -w 2> $LOG_PATH/test91.err
echo -n $? > test91.!!!

# test92: Bonus RLO - konecny automat neni dobre specifikovany (bez rozsireni vraci chybu 1); Expected output: test92.out; Expected return code: 62
$INTERPRETER $TASK.$EXTENSION --input=test92.in --output=$LOCAL_OUT_PATH/test92.out -r 2> $LOG_PATH/test92.err
echo -n $? > test92.!!!

# test93: Bonus WHT a RLO - kombinace parametru (bez rozsireni vraci chybu 1); Expected output: test93.out; Expected return code: 0
$INTERPRETER $TASK.$EXTENSION -r -m --white-char --input=test93.in --output=$LOCAL_OUT_PATH/test93.out 2> $LOG_PATH/test93.err
echo -n $? > test93.!!!

