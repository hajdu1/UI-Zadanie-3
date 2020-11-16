Hľadanie pokladu
Umelá inteligencia, Zadanie č. 3b

Úloha
Majme hľadača pokladov, ktorý sa pohybuje vo svete definovanom dvojrozmernou mriežkou a zbiera poklady, 
ktoré nájde po ceste. Začína na políčku označenom písmenom S a môže sa pohybovať štyrmi rôznymi smermi: 
hore H, dole D, doprava P a doľava L. K dispozícii má konečný počet krokov. Jeho úlohou je nazbierať čo 
najviac pokladov. Za nájdenie pokladu sa považuje len pozícia, pri ktorej je hľadač aj poklad na tom 
istom políčku. Susedné políčka sa neberú do úvahy.

Zadanie
Horeuvedenú úlohu riešte prostredníctvom evolučného programovania nad virtuálnym strojom.
Tento špecifický spôsob evolučného programovania využíva spoločnú pamäť pre údaje a inštrukcie. 
Pamäť je na začiatku vynulovaná a naplnená od prvej bunky inštrukciami. Za programom alebo od určeného 
miesta sú uložené inicializačné údaje (ak sú nejaké potrebné). Po inicializácii sa začne vykonávať 
program od prvej pamäťovej bunky. (Prvou je samozrejme bunka s adresou 000000.) Inštrukcie modifikujú 
pamäťové bunky, môžu realizovať vetvenie, programové skoky, čítať nejaké údaje zo vstupu a prípadne aj 
zapisovať na výstup. Program sa končí inštrukciou na zastavenie, po stanovenom počte krokov, pri chybnej 
inštrukcii, po úplnom alebo nesprávnom výstupe. Kvalita programu sa ohodnotí na základe vyprodukovaného 
výstupu alebo, keď program nezapisuje na výstup, podľa výsledného stavu určených pamäťových buniek.

Virtuálny stroj
Náš stroj bude mať 64 pamäťových buniek o veľkosti 1 byte.
Bude poznať štyri inštrukcie: inkrementáciu hodnoty pamäťovej bunky, dekrementáciu hodnoty pamäťovej bunky, 
skok na adresu a výpis (H, D, P alebo L) podľa hodnoty pamäťovej bunky.
Inštrukcie majú tvar podľa nasledovnej tabuľky:

inkrementácia = 00XXXXXX
dekrementácia = 01XXXXXX
skok = 10XXXXXX
výpis = 11XXXXXX
Hodnota XXXXXX predstavuje 6bitovú adresu pamäťovej bunky s ktorou inštrukcia pracuje (adresovať je teda 
možné každú). Prvé tri inštrukcie by mali byť jasné, pri poslednej je potrebné si dodefinovať, čo sa 
vypíše pri akej hodnote bunky. Napríklad ak bude obsahovať maximálne dve jednotky, tak to bude H, pre 
tri a štyri to bude D, pre päť a šesť to bude P a pre sedem a osem jednotiek v pamäťovej bunke to bude L.

Program sa zastaví, akonáhle bude splnená niektorá z nasledovných podmienok:

- program našiel všetky poklady
- postupnosť, generovaná programom, vybočila zo stanovenej mriežky
- program vykonal 500 krokov (inštrukcií)

Či sa program zastaví, keď príde na poslednú bunku alebo pokračuje znovu od začiatku, si môžete zvoliť sami. 
(Môžete to nechať aj na voľbu používateľovi.) Je možné navrhnúť aj komplikovanejší virtuálny stroj s 
rozšírenými inštrukciami a veľkosťou pamäťovej bunky viac ako osem bitov, ale musí sa dodržať podmienka 
maximálneho počtu pamäťových buniek 64 a limit 500 krokov programu. Rozšírenie inštrukcií sa využíva nielen 
na zadefinovanie nových typov inštrukcií, ale hlavne na vytvorenie inštrukcií s podmieneným vykonávaním.

Zaujímavou (a fungujúcou) obmenou je aj použitie nepriamej adresácie. Vtedy predstavuje hodnota XXXXXX adresu 
bunky, kde je (v posledných šiestich bitoch) uložená adresa bunky ktorá sa má modifikovať alebo ktorá sa číta. 
Pri inštrukcii skoku je to adresa bunky kde je uložená adresa skoku. Nepriama adresácia sa dá využiť na 
oddelenie programu a údajov (napríklad keď z nejakého dôvodu nechceme vytvoriť samomodifikujúce sa programy). 
To je však pri tomto spôsobe tvorby programov len málokedy výhodné.
