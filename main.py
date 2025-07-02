from psychopy import visual, event, core, sound
import psychtoolbox as ptb
from random import shuffle, choice
from config import BLOCK_LENGTH, NUMBER_OF_BLOCKS


def test(table, fixed_cards):
    """Funkcja odpowiada za zrealizowanie sekwencji testowej na podstawie
    dostarczonej listy prób i listy kart stałych."""
    errors = 0 # w tej zmiennej zliczana jest liczba wszystkich błędów
    n_p_errors = 0 # w tej zmiennej zliczana jest liczba błędów nieperseweratywnych
    for trial in table: # iteracja po każdym elemencie listy prób
        stimulus_img = f"bitmaps/{trial[0]}.png" # ścieżka do pliku graficznego reprezentującego kartę
        target = int(trial[1])  # numer poprawnej karty
        previous = int(trial[2]) # numer poprawnej karty dla poprzedniego kryterium

        target_card = visual.ImageStim(win, image=stimulus_img, pos=(-300,-100)) # tworzenie obiektu karty
        
        core.wait(1.0) # sekundowa przerwa na przygotowanie

        for fc in fixed_cards:
            fc.draw() # narysowanie kart stałych
        target_card.draw() # narysowanie karty do przyporządkowania
        """
        poprzednie metody narysowały obiekty w buforze,
        aby wyświetlić narysowane w buforze obiekty należy odświeżyć okno
        """
        win.flip()

        mouse.clickReset() # wyczyszczenie informacji o kliknięciach
        response = None # wyczyszczenie zmiennej na odpowiedź
        timer = core.Clock() # rozpoczęcie odliczania
        timeout = False # przyporządkowanie zmiennej timeout wartości domyślnej False
        
        while timer.getTime() < 10: # czekamy 10 sekund na odpowiedź
            buttons = mouse.getPressed() # pobieramy listę informującą, które przyciski na myszce są naciśnięte w danym momencie
            if buttons[0]: # jeśli lewy przycisk myszki jest wciśnięty:
                x,y = mouse.getPos() # pobieramy koordynaty kliknięcia
                # sprawdzamy, którą kartę kliknięto
                for i, fc in enumerate(fixed_cards): # sposób iteracji, przy którym otrzymujemy indeks elementu i obiekt
                    if fc.contains(mouse):
                        response = i+1  # numer karty 1..4
                        break
                """
                Jeśli zmienna response ewaluuje się do fałszu, to znaczy, że kliknięcie nastąpiło poza kartami
                Jeśli ewaluuje się do prawdy, to wybrano odpowiedź i można przejść do sprawdzenia jej poprawności
                """
                if response:
                    break
            if 'escape' in event.getKeys(): # sprawdzenie, czy użytkownik nacisnął escape
                core.quit() # jeśli tak, to opuszczenie eksperymentu
        else: # konstrukcja pozwalająca wywołanie kodu, jeśli warunek pętli uzyska wartość False
            timeout = True # skończył się czas na odpowiedź, zmienna timeout ma wartość True
            
        # informacja zwrotna
        if timeout: # jeśli przekroczono czas
            timeout_sound.play(when=ptb.GetSecs()) # odtworzenie dźwięku timeoutu w momencie wywołania metody
            timeout_img.draw() # narysowanie obrazka
            win.flip() # odświeżenie okna
            core.wait(2.0) # odczekanie 2 sekund, aby uczestnik się przygotował na kolejną próbę
        elif response == target: # poprawna odpowiedź
            correct_sound.play(when=ptb.GetSecs()) # odtworzenie dźwięku poprawnej odpowiedzi
            correct_img.draw()
            win.flip()
            core.wait(2.0)
        else: # niepoprawna odpowiedź
            wrong_sound.play(when=ptb.GetSecs()) # odtworzenie dźwięku niepoprawnej odpowiedzi
            wrong_img.draw()
            errors += 1 # dodajemy 1 do liczby wszystkich błędów
            if response != previous: # jeśli błąd nie wynikał z przywiązania do poprzedniej reguły
                n_p_errors += 1 # liczba błędów nieperseweratywnych zwiększa się o 1
            win.flip() 
            core.wait(2.0)
    return errors, n_p_errors # zwrócenie zmiennych informujących o błędach

def create_new_table():
    # wszystkie możliwości kształtów, liczb i kolorów na kartach
    shapes = ["circle", "triangle", "cross", "star"] 
    numbers = list(range(1, 5)) # lista od 1 do 4 - 'range' nie uwzględnia ostatniego elementu
    colors = ["red", "green", "blue", "yellow"]

    all_cards = [] # tu przechowywane będą wszystkie nazwy kart poza stałymi

    for shape in shapes:
        for number in numbers:
            for color in colors:
                # format z '/' pomoże w doborze poprawnej odpowiedzi według poprzedniego kryterium
                all_cards.append(f"{shape}/{str(number)}/{color}")

    fixed_cards = ["circle/1/red", "triangle/2/green", "cross/3/blue", "star/4/yellow"]
    for card in fixed_cards:
        all_cards.remove(card) # usuwamy stałe
    
    shuffle(all_cards) # tasujemy karty
    criteria = ["shape", "number", "color"] # lista możliwych kryteriów
    old_criterion = "" # na początku nie istnieje poprzednie kryterium
    
    card_sequence = [] # lista zawierająca sekwencję prób
    
    for i in range(NUMBER_OF_BLOCKS): # dzielimy listę kart na bloki
        criterion = choice(criteria) # wybieramy losowe kryterium
        while criterion == old_criterion: # jeśli zostało powtórzone względem poprzedniego to wybieramy do skutku
            criterion = choice(criteria)
        for j in range(BLOCK_LENGTH): # iterujemy po każdym elemencie bloku
            card = all_cards[i * BLOCK_LENGTH + j] # w ten sposób wybieramy kolejne indeksy z listy
            name = card.replace('/', '') # musimy pozbyć się znaków '/' aby uzyskać poprawną nazwę pliku
            
            if criterion == "shape": # jeśli wybrane kryterium to kształt
                card_feature_new = card.split("/")[0] # ekstraktujemy kształt z nazwy karty
            elif criterion == "number": # analogicznie dla numeru
                card_feature_new = card.split("/")[1]
            else: # analogicznie dla koloru
                card_feature_new = card.split("/")[2]
            
            if old_criterion == "shape": # jeśli poprzednim kryterium był kształt
                card_feature_old = card.split("/")[0] # ekstraktujemy kształt z nazwy karty
            elif old_criterion == "number": # analogicznie dla numeru
                card_feature_old = card.split("/")[1]
            elif old_criterion == "color": # analogicznie dla koloru
                card_feature_old = card.split("/")[2]
            else: # poprzednie kryterium nie istnieje
                card_feature_old = "none" # potrzebujemy dowolnej wartości, żeby nie wystąpił błąd
                old_choice = "0"
                
            for k in range(4):
                if card_feature_new in fixed_cards[k]: # sprawdzamy występowanie kryterium wśród stałych
                    new_choice = str(k+1) 
                if card_feature_old in fixed_cards[k]:
                    old_choice = str(k+1)
            
            card_element = (name, new_choice, old_choice) # tworzymy krotkę z danymi próby
            card_sequence.append(card_element) # dodajemy krotkę do listy prób
        old_criterion = criterion # zmiana kryterium po przejściu przez wszystkie karty w bloku

    return card_sequence # po zakończeniu pętli zwracamy listę

if __name__ == "__main__":
    win = visual.Window(size=(1600,1200), color='grey', units='pix') # utworzenie obiektu okna
    mouse = event.Mouse(win=win) # utworzenie obiektu myszki

    # utworzenie dźwięków
    correct_sound = sound.Sound('sounds/correct_answer.wav')
    wrong_sound = sound.Sound('sounds/wrong_answer.wav')
    timeout_sound = sound.Sound('sounds/timeout.wav')
    cheer_sound = sound.Sound('sounds/cheer.wav')
    


    # utworzenie obrazów informacyjnych
    correct_img = visual.ImageStim(win, image='bitmaps/correct.png', pos=(250,-100))
    wrong_img = visual.ImageStim(win, image='bitmaps/wrong.png', pos=(250,-100))
    timeout_img = visual.ImageStim(win, image='bitmaps/timeout_bitmap.png', pos=(250,-100))

    # utworzenie kart stałych
    card_positions = [(-175,200), (-25,200), (125,200), (275,200)]
    card_images = [
        'bitmaps/circle1red.png',
        'bitmaps/triangle2green.png',
        'bitmaps/cross3blue.png',
        'bitmaps/star4yellow.png'
    ]
    fixed_cards = [visual.ImageStim(win, image=img, pos=pos) for img, pos in zip(card_images, card_positions)]

    # utworzenie stron instrukcji
    instruction_stim = visual.ImageStim(win, pos=(0,150))
    instruction_pages = [
        'bitmaps/instruction1.png',
        'bitmaps/instruction2.png',
        'bitmaps/instruction3.png'
    ]

    # realizacja instrukcji
    for instruction_file in instruction_pages:
        instruction_stim.image = instruction_file
        instruction_stim.draw()
        win.flip()

        # czekamy aż ktoś naciśnie spację
        keys = event.waitKeys(keyList=['space', 'escape'])
        if 'escape' in keys: # opuszczamy eksperyment jeśli naciśnięto escape
            core.quit()

    # wczytanie tabeli treningowej - jest stała dla każdego uruchomienia eksperymentu
    with open('table_training.txt') as f:
        training_table = f.readlines() # wczytanie listy linii w pliku
        for i in range(len(training_table)): # iteracja po liście
            """
            Metoda readlines() zostawia znak końca linii w każdym elemencie - musimy się go pozbyć.
            Dane o próbie oddzielone są od siebie znakiem ';' - funkcja split tworzy listę tych danych
            """
            training_table[i] = training_table[i].replace('\n', '').split(';')
    """
    Rozpoczynamy treningową sesję na podstawie wczytanej listy treningowej oraz stałych kart.
    Ponieważ w trakcie treningu nie interesują nas informacje o błędach, wartości
    zwracane przez funkcję są ignorowane.
    """
    test(training_table, fixed_cards)
    
    # wyświetlamy informację o zakończeniu sesji treningowej
    end_of_training_text = visual.TextStim(
        win,
        text="To była sesja treningowa,\n\nnaciśnij spację by przejść do sesji eksperymentalnej",
        color='yellow',
        pos=(0,-50)
    )
    end_of_training_text.draw()
    win.flip()
    event.waitKeys(keyList=['space'])

    # tworzymy nową listę prób, którą wykorzystamy w części eksperymentalnej
    experiment_table = create_new_table()
    
    """
    Rozpoczynamy część eksperymentalną.
    Tym razem informacje o błędach są nam potrzebne, aby wyświetlić je po zakończeniu eksperymentu.
    """
    errors, non_perseveration_errors = test(experiment_table, fixed_cards)
    
    # tworzymy i wyświetlamy tekst zawierający informację zwrotną
    text = f"""
Liczba błędów: {str(errors)},
w tym:
   błędy perseweratywne: {str(errors-non_perseveration_errors)}
   błędy nieperseweratywne: {str(non_perseveration_errors)}
Procent poprawnych odpowiedzi: {'%.2f' % (100*(60-errors)/60)}%
Dziękuję za udział.
"""
    
    feedback_text = visual.TextStim(
        win,
        text=text,
        color='yellow',
        pos=(0,-50)
    )
    # odtworzenie dźwięku symbolizującego zakończenie eksperymentu
    cheer_sound.play(when=ptb.GetSecs())
    feedback_text.draw()
    win.flip()
    event.waitKeys(keyList=['space'])

    win.close()
    core.quit()
