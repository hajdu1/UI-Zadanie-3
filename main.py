from random import *            # pre generovanie nahodnych hodnot z intervalov
from numpy import *             # pre natypovanie buniek jedincov na uint8
from copy import *              # vyuzitie deepcopy()
import os.path                  # na overenie platnosti (existencie) vstupneho suboru

NUM_OF_CELLS = 64               # pocet buniek jedinca
# volitelne parametre:
POP_COUNT = 20                  # pocet jedincov generacie, predvolene 20
MUTATION_CHANCE = 2             # pravdepodobnost mutacie v percentach, predvolene 2
SURVIVE_CHANCE = 10             # pravdepodobnost prezitia jedinca v percentach, predvolene 10


# trieda pre objekt mapy na prehladavanie
class Map:
    def __init__(self):
        self.x = 0              # vyska mapy
        self.y = 0              # sirka mapy
        self.start_x = 0        # startovacia pozicia x
        self.start_y = 0        # startovacia pozicia y
        self.treasure = set()   # sem sa nacitaju suradnice vsetkych pokladov v mape


# trieda pre objekty jedneho jedinca (vstupneho kodu)
class Element:
    def __init__(self):
        self.cells = []         # zoznam pamatovych buniek
        self.path = ''          # sem sa po spracovani virtualnym strojom priradi cesta prejdena v mape
        self.found = set()      # sem bude pridany kazdy poklad, ktory dany jedinecc najde
        self.fitness = 0        # hodnota fitness pre daneho jedinca


# funkcia overuje, ci sa na pozicii [x, y] nacahdza poklad
def check_field(cx, cy, code, treasure_map):
    # ak aktualne suradnice koresponduju s niektorymi zo suradnic pokladov v mape a doposial
    # neboli pridane do najdenych pokladov jedinca, prida sa tento poklad a zvysi sa fitness
    if (cx, cy) in treasure_map.treasure and (cx, cy) not in code.found:
        code.fitness += 1
        code.found.add((cx, cy))
    return code


# funkcia na zistenie hodnoty fitness (virtualny stroj, samotne prechadzanie mapy a hladanie pokladov)
def calculate_fitness(code, treasure_map):
    steps = 500                                     # pocet krokov, ktore moze stroj vykonat
    index = 0                                       # adresa spracovavanej pamatovej bunky
    cx = treasure_map.start_x                       # aktualna pozicia X hladaca pokladov v mape
    cy = treasure_map.start_y                       # aktualna pozicia Y hladaca pokladov v mape
    code = check_field(cx, cy, code, treasure_map)  # overi sa, ci na startovacej pozicii v mape nie je poklad

    while steps > 0:
        if len(code.found) == len(treasure_map.treasure):
            break                                   # ak jedinec nasiel vsetky poklady, stroj sa ukonci
        steps -= 1
        instruction = code.cells[index] >> 6        # instrukciu reprezentuju prve dva bity bunky
        address = code.cells[index] & 63            # adresu na skok alebo hodnotu vypisu predstavuje zvysnych 6 bitov

        if instruction == 0:                        # cyklicka inkrementacia bunky na danej adrese
            if code.cells[address] == 255:
                code.cells[address] = 0
            else:
                code.cells[address] += 1

        elif instruction == 1:                      # cyklicka dekrementacia bunky na danej adrese
            if code.cells[address] == 0:
                code.cells[address] = 255
            else:
                code.cells[address] -= 1

        elif instruction == 2:                      # skok virtualneho stroja na danu adresu instrukcie
            index = address
            continue

        elif instruction == 3:                      # "vypis" kroku v mape a kontrola vyjdenia z mapy
            if address in range(0, int(NUM_OF_CELLS / 4)):
                # hore (hodnota bunky okrem instrukcie v prvej stvrtine intervalu 0-63)
                if cx - 1 >= 0:
                    cx -= 1
                    code.path += 'U, '
                    code = check_field(cx, cy, code, treasure_map)
                else:
                    break
            elif address in range(int(NUM_OF_CELLS / 4), 2 * int(NUM_OF_CELLS / 4)):
                # dole (hodnota bunky okrem instrukcie v druhej stvrtine intervalu 0-63)
                if cx + 1 < treasure_map.y:
                    cx += 1
                    code.path += 'D, '
                    code = check_field(cx, cy, code, treasure_map)
                else:
                    break
            elif address in range(2 * int(NUM_OF_CELLS / 4), 3 * int(NUM_OF_CELLS / 4)):
                # doprava (hodnota bunky okrem instrukcie v tretej stvrtine intervalu 0-63)
                if cy + 1 < treasure_map.x:
                    cy += 1
                    code.path += 'R, '
                    code = check_field(cx, cy, code, treasure_map)
                else:
                    break
            elif address in range(3 * int(NUM_OF_CELLS / 4), NUM_OF_CELLS):
                # dolava (hodnota bunky okrem instrukcie v stvrtej stvrtine intervalu 0-63)
                if cy - 1 >= 0:
                    cy -= 1
                    code.path += 'L, '
                    code = check_field(cx, cy, code, treasure_map)
                else:
                    break
        # cyklicka inkrementacia adresy instrukcie na vykonavanie
        if (index + 1) == 64:
            index = 0
        else:
            index += 1
    # vracia sa spracovany jedinec
    return code


# funkcia na vyber rodica pomocou rulety
def roulette_parent(sum_fitness):
    global population
    if sum_fitness == 0:                            # ak ma kazdy jedinec nulovy fitness, je jedno ktory sa vyberie
        return population[randrange(POP_COUNT)]     # predchadza sa vyberu z neplatneho rozsahu randrange(0, 0)
    ran = randrange(sum_fitness)                    # vyberie sa nahodna hodnota z rozsahu po sucet fitness jedincov
    partial_sum = 0
    count = -1
    for element in population:
        count += 1
        partial_sum += element.fitness              # sumujeme postupne fitness kazdeho jedinca
        if partial_sum > ran:                       # ak sme presiahli generovanu hodnotu, vyberame aktualneho jedinca
            break
    return population[count]


# funkcia na vyber rodica pomocou turnaja
def tournament():
    number_of_chosen = 3                            # pocet vyberanych jedincov do turnaja
    global population
    max_chosen = Element()
    for index in range(number_of_chosen):
        chosen = population[randrange(POP_COUNT)]
        if chosen.fitness >= max_chosen.fitness:    # hladame jedinca s najlepsim fitness spomedzi vybranych
            max_chosen = chosen
    return max_chosen


# fubkcia na analyzu populacie a tvorenie novych generacii
def analyze_population(treasure_map, selection):
    global population

    # global output_file                                    # na testovanie, ak je aktivny blok kodu TESTER
    # test_sum = 0                                          # pre TESTER

    global best
    new_generation = []                                     # pole pre novu generaciu
    sum_fitness = 0                                         # celkovy suce fitness generacie pre ruletu
    for element in population:
        result = calculate_fitness(deepcopy(element), treasure_map)     # hladanie pokladov a vypocet fitness

        # output_file.writelines(str(result.fitness) + ' ' + result.path + '\n')    # pre TESTER
        # test_sum += result.fitness                        # pre TESTER

        if result.fitness > best.fitness:                   # pokial sa nasiel novy najlepsi element, aktualizuje sa
            best = deepcopy(result)
            if best.fitness == len(treasure_map.treasure):  # ak sa nasli vsetky poklady, netvori sa dalsia generacia
                return
        element.fitness = result.fitness                    # aktualnej populacii sa priradia hodnoty fitness
        if selection == 'r':                                # ak sa bude vyberat cez ruletu, navysuje sa sucet fitness
            sum_fitness += element.fitness

    # output_file.writelines(str(test_sum / POP_COUNT) + '\n')     # pre TESTER

    for index in range(POP_COUNT):                          # tvorba novej generacie prezitim alebo krizenim
        new_generation.append(Element())

        # skopirovanie celeho obsahu jedinca do novej generacie (prezitie) pri danej pravdepodobnosti
        if randrange(int(100 / SURVIVE_CHANCE)) == 1:
            new_generation[index].cells = deepcopy(population[index].cells)
            continue

        # ruleta
        if selection == 'r':
            parent_1 = roulette_parent(sum_fitness)
            parent_2 = roulette_parent(sum_fitness)
        # turnaj
        elif selection == 't':
            parent_1 = tournament()
            parent_2 = tournament()
        else:
            print('Selection option error')
            return

        # sekcia krizenia
        middlepoint = randrange(NUM_OF_CELLS)               # bunka po ktoru sa bude kopirovat obsah prveho rodica
        # praca s prvym rodicom po middlepoint
        for cell in range(middlepoint):
            if randrange(int(100 / MUTATION_CHANCE)) == 1:  # ak nastane mutacia, hodnota bunky bude nahodna
                new_generation[index].cells.append(uint8(randrange(256)))
            else:
                new_generation[index].cells.append(deepcopy(parent_1.cells[cell]))
        # praca s druhym rodicom od middlepointu po poslednu bunku
        for cell in range(middlepoint, NUM_OF_CELLS):
            if randrange(int(100 / MUTATION_CHANCE)) == 1:  # ak nastane mutacia, hodnota bunky bude nahodna
                new_generation[index].cells.append(uint8(randrange(256)))
            else:
                new_generation[index].cells.append(deepcopy(parent_2.cells[cell]))

    population = deepcopy(new_generation)   # nova vytvorena generacia sa stane aktualnou populaciou


# inicializacia populacie nahodnymi hodnotami v bunkach
def init_population(init_cells):
    global population
    for element in range(POP_COUNT):
        new_element = Element()
        for cell in range(init_cells):
            new_element.cells.append(uint8(randrange(256)))     # zadany rozsah buniek sa naplni nahodnymi cislami
        for cell in range(init_cells, NUM_OF_CELLS):
            new_element.cells.append(uint8(0))                  # zvysok sa nainicializuje na nuly
        population.append(new_element)


def load_map(filename):
    treasure_map = Map()
    input_file = open('inputs\\' + filename + '.txt', 'r')
    data = input_file.readline().split()
    treasure_map.x = int(data[0])
    treasure_map.y = int(data[1])
    data = input_file.readline().split()
    treasure_map.start_x = int(data[0])
    treasure_map.start_y = int(data[1])
    data = input_file.readline().split()
    while data:
        treasure_map.treasure.add((int(data[0]), int(data[1])))
        data = input_file.readline().split()
    input_file.close()
    return treasure_map


# funkcia na vypis buniek jedinca, jeho fitness a cesty v mape
def print_element(element):
    bin_code = ''                                               # bunkky jedinca v binarnom tvare
    dec_code = ''                                               # bunkky jedinca v dekadickom tvare
    for cell in range(len(element.cells)):
        bin_code += format(element.cells[cell], '08b') + ', '
        dec_code += str(element.cells[cell]) + ', '
    print('najdene poklady: ' + str(element.fitness) + ', cesta: ' + element.path[:-2])
    print('bin: [' + bin_code[:-2] + ']')
    print('dec: [' + dec_code[:-2] + ']\n')


# --------------------------------------MAIN--------------------------------------
population = []
# menu pre pracu s aplikaciou
while 1:
    print('Nacitat subor: y\nUkoncit program: n')
    answer = input()
    if answer == 'n':
        break
    elif answer == 'y':
        print('Zadajte nazov suboru s mapou (bez pripony)')
        answer = input()
        if os.path.isfile('inputs\\' + answer + '.txt'):
            population.clear()
            best = Element()                                    # jedinec s najviac najvacim fitness
            grid = load_map(answer)                             # nacitanie udajov zo suboru do mapy
            init_population(NUM_OF_CELLS)                       # inicializacia populacie, argument <= NUM_OF_CELLS
            print('Zadajte sposob vyberu rodicov pre nove generacie\nRuleta = r\nTurnaj = t')
            selection_method = input()
            while selection_method not in {'r', 't'}:
                print('Nebola zadana jedna z moznosti vyberu\nRuleta = r\nTurnaj = t')
                selection_method = input()
            print('Zadajte limit poctu generacii pre prehladavanie')
            for i in range(1, int(input()) + 1):                # vytvara a prehladava sa dany pocet generacii
                analyze_population(grid, selection_method)
                if best.fitness == len(grid.treasure):          # ak sa nasli vsetky poklady, cyklus konci
                    print('Vsetky poklady najdene v generacii cislo  ' + str(i))
                    print_element(best)
                    break
            if best.fitness < len(grid.treasure):               # ak sa nenasli vsetky, vypise sa najlepsi vysledok
                print('Do maximalenj generacie neboli najdene vsetky poklady, vypisuje sa najlepsi vysledok')
                print_element(best)
        else:
            print('Zadany subor sa nenasiel')
# --------------------------------------------------------------------------------

# -------------------------------------TESTER-------------------------------------
# # je potrebne zakomentovat MAIN a odkomentovat casti analyze_population()
# # do vystupneho suboru vypisuje priemerny fitness kazdej generacie a/alebo cestu a fitness kazdeho jedinca
# answer = input()
# grid = load_map(answer)
# output_file = open('outputs\\' + answer + '_output.txt', 'w')
# population = []
#
# runs = 10                                   # pocet spusteni programu
# found = 0
# max_generation = 1000                       # limit poctu generacii
# for j in range(runs):
#     output_file.writelines('run ' + str(j + 1) + '\n')
#     population.clear()
#     init_population(NUM_OF_CELLS)
#     best = Element()
#     for i in range(1, max_generation + 1):
#         analyze_population(grid, 't')
#         if best.fitness == len(grid.treasure):
#             print('All treasures found in generation ' + str(i))
#             found += 1
#             print_element(best)
#             break
#     if best.fitness < len(grid.treasure):
#         print('Did not find all of the treasures, returning the best element so far')
#         print_element(best)
# print('All treasures found in ' + str(float(found / runs * 100)) + '% of all runs')
# output_file.close()
# --------------------------------------------------------------------------------
