import sys
import matplotlib
matplotlib.use('Qt5Agg') 
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, QMessageBox)
from PyQt5.QtGui import (QPainter, QColor, QPen, QBrush, QFont, QPainterPath)
from PyQt5.QtCore import QTimer, Qt, QPointF

RefreshRate=30
######Definiowanie klas######

class OknoWykresu(QMainWindow):
    def __init__(self, tytul, max_y):
        super().__init__()
        self.setWindowTitle(tytul)
        self.setGeometry(100, 100, 300, 200)
        
        # Ustawienia Matplotlib
        self.figura = Figure(figsize=(3, 2), dpi=80)
        self.wykres = FigureCanvasQTAgg(self.figura)
        self.setCentralWidget(self.wykres)
        
        self.os = self.figura.add_subplot(111)
        self.linia, = self.os.plot([], [])
        
        self.os.set_ylim(0, max_y * 1.1) # Skala pionowa
        self.os.set_xlim(0, 200)         # Skala pozioma (historia)
        self.os.grid(True)

    def odswiez_wykres(self, dane):
        self.linia.set_ydata(dane)
        self.linia.set_xdata(range(len(dane)))
        self.wykres.draw()


class Zbiornik:

    ### Definiowanie parametrów startowych zbiorników###
    def __init__(self, x, y, szerokosc, wysokosc, pojemnosc, poziomStart, nazwa):
        self.x = x
        self.y = y
        self.szerokosc = szerokosc
        self.wysokosc = wysokosc
        self.pojemnosc = pojemnosc
        self.nazwa = nazwa
        self.aktualny_poziom = float(poziomStart)
        self.historia = [self.aktualny_poziom] * 200

    ###funkcja dolewania###
    def dolej(self, ilosc):
        miejsce = self.pojemnosc - self.aktualny_poziom
        ilosc_teraz = min(miejsce, ilosc)
        self.aktualny_poziom +=ilosc_teraz

        return ilosc_teraz
    
    ###funkcja wylewania###
    def wylej(self, ilosc):
        ilosc_teraz = min(self.aktualny_poziom, ilosc)
        self.aktualny_poziom -= ilosc_teraz

        return ilosc_teraz

    ###rysowanie zbiorników i wody###
    def narysuj(self, draw):

        ###rysiowanie konturów###
        draw.setBrush(QBrush(QColor(160, 160, 160)))
        draw.setPen(QPen(Qt.black, 3))
        draw.drawRect(self.x, self.y, self.szerokosc, self.wysokosc)

        ###rysowanie wody###
        if self.aktualny_poziom >0:
            procent = self.aktualny_poziom/ self.pojemnosc
            wys_wody = procent*self.wysokosc
            dol_zbiornika = self.y + self.wysokosc
            gora_zbiornika = dol_zbiornika -wys_wody

            kolor_wody = QColor(Qt.blue)
            draw.setBrush(QBrush(kolor_wody))
            draw.setPen(Qt.NoPen)
            draw.drawRect(self.x+3, int(gora_zbiornika), self.szerokosc-6, int(wys_wody))
         

        draw.setPen(Qt.white)
        draw.setFont(QFont('Arial', 9, QFont.Bold))
        text = f"{self.nazwa}: {int(self.aktualny_poziom)}/{int(self.pojemnosc)}"
        draw.drawText(self.x, self.y - 10, text)

class Pompa:
    def __init__(self, x, y, szybkosc):
        self.x = x
        self.y = y
        self.szybkosc = szybkosc
        self.stan = False
        self.zbiornik_docelowy = None

    def wlacz_pompe(self):
        if self.stan == False:
            if self.zbiornik_docelowy is not None:
                if self.zbiornik_docelowy.aktualny_poziom >= self.zbiornik_docelowy.pojemnosc:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setWindowTitle("Blad pompy")
                    msg.setText(f"Nie mozna wlaczyc pompy \n Zbiornik {self.zbiornik_docelowy.nazwa} jest zapelniony")
                    msg.exec_()
                    return
        self.stan = not self.stan

    def awaria(self):
        if self.stan:
            self.stan=False
            msg=QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Zbiornik przepelniony")
            text = f"Uwazaj! Zbiornik {self.zbiornik_docelowy.nazwa} jest pelny! \n Pompa nie moze zostac wlaczona"
            msg.setText(text)
            msg.exec_()

    def narysuj(self, draw):
        ###obudowa###
        draw.setBrush(QBrush(Qt.black))
        draw.setPen(QPen(Qt.black))
        draw.drawRect(self.x-20, self.y-20, 40, 40)

        if self.stan:
            kolor = Qt.green
        else:
            kolor = Qt.red 

        draw.setBrush(QBrush(kolor))
        draw.setPen(Qt.NoPen)
        draw.drawEllipse(self.x-6, self.y-6, 12, 12)


    

class Rura:
    def __init__(self, zrodlo, cel, punkty, pompa=None):
        self.zrodlo = zrodlo
        self.cel = cel
        self.punkty = punkty
        self.pompa = pompa
        self.przeplyw = False

        if self.pompa:
            self.pompa.zbiornik_docelowy = self.cel

    def wlacz(self):
        self.przeplyw = False

        if self.pompa and self.pompa.stan:
            if self.cel.aktualny_poziom >= self.cel.pojemnosc:
                self.pompa.awaria()
                return
            
        i = 0

        if self.pompa and self.pompa.stan:
            if self.zrodlo.aktualny_poziom > 0:
                i = self.pompa.szybkosc

        if i>0:
            pobrano = self.zrodlo.wylej(i)
            wlano = self.cel.dolej(pobrano)
            if wlano > 0:
                self.przeplyw = True


        elif self.pompa is None:
            if self.zrodlo.aktualny_poziom > 0:
                i = 1.5

    def narysuj(self, draw):
        pen = QPen(Qt.black, 8)

        if self.przeplyw:
            pen.setColor(QColor(Qt.blue))
            pen.setWidth(6)

        draw.setPen(pen)
        draw.setBrush(Qt.NoBrush)

        punkty_rury = []
        for p in self.punkty:
            punkty_rury.append(QPointF(p[0], p[1]))

        draw.drawPolyline(*punkty_rury)

        
class Projekt(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Projekt")
        self.setGeometry(100, 100, 1200, 750)

        self.czy_dolewac = False
        self.licznik = 0

        ###rysowanie obiektów###

            ###zbiorniki###
        self.zbiornik1 = Zbiornik(100, 100, 100, 250, 1000, 0, "Zbiornik 1")
        self.zbiornik2 = Zbiornik(400, 350, 100, 200, 500, 0, "Zbiornik 2")
        self.zbiornik3 = Zbiornik(700, 350, 100, 200, 500, 0, "Zbiornik 3")
        self.zbiornik4 = Zbiornik(1000, 500, 80, 120, 300, 0, "Zbiornik odpływowy")

        self.zbiorniki = [self.zbiornik1, self.zbiornik2, self.zbiornik3, self.zbiornik4]

            ###pąpy###
        self.pompa1 = Pompa(300,300,1.0)
        self.pompa2 = Pompa(600,400,3.0)
        self.pompa3 = Pompa(900,450,2.0)

        self.pompy =(self.pompa1, self.pompa2, self.pompa3)

            ###rysowanie rur###
        trasa1 = [(200,300),(250,300),(300,300),(350,300),(350,400),(400, 400)]
        self.rura1 = Rura(self.zbiornik1, self.zbiornik2, trasa1, self.pompa1)
        
        trasa2 = [(500,450),(550,450),(550, 400),(600,400),(650,400),(650,450),(700,450)]
        self.rura2 = Rura(self.zbiornik2, self.zbiornik3, trasa2, self.pompa2)

        trasa3 = [(800,450),(900,450),(950,450),(950,600),(1000,600)]
        self.rura3 = Rura(self.zbiornik3, self.zbiornik4, trasa3, self.pompa3)

        self.rury = [self.rura1, self.rura2, self.rura3]

        self.interfejs()
        self.wykresy()

        self.timer = QTimer()
        self.timer.timeout.connect(self.petlaGlowna)
        self.timer.start(RefreshRate)

    ###funkcja wykresow###
    def wykresy(self):
        self.lista_okien = []

        pos_x = 1220 
        pos_y = 50
        
        for z in self.zbiorniki:
            okno = OknoWykresu(f"Wykres {z.nazwa}", z.pojemnosc)
            okno.move(pos_x, pos_y)
            okno.show()
            self.lista_okien.append(okno)
            pos_y += 230 # Przesuniecie kolejnego okna w dol


    ###definiowanie interfejsu####
    def interfejs(self):
    

        self.przycisk_dolej = QPushButton("Dolej wody", self)
        self.przycisk_dolej.setGeometry(50, 20, 200, 40)
        self.przycisk_dolej.setCheckable(True)
        self.przycisk_dolej.clicked.connect(self.dolewanie)
        self.przycisk_dolej.setStyleSheet("background-color: lightblue;")
       

        self.pp1 = QPushButton("pompa1", self)
        self.pp1.setGeometry(250, 650, 100, 40)
        self.pp1.clicked.connect(self.pompa1.wlacz_pompe)

        self.pp2 = QPushButton("pompa2", self)
        self.pp2.setGeometry(550, 650, 100, 40)
        self.pp2.clicked.connect(self.pompa2.wlacz_pompe)

        self.pp3 = QPushButton("pompa3", self)
        self.pp3.setGeometry(850, 650, 100, 40)
        self.pp3.clicked.connect(self.pompa3.wlacz_pompe)

    def dolewanie(self):
        if self.przycisk_dolej.isChecked():
            self.czy_dolewac = True
            self.przycisk_dolej.setText("zamknij zawor")
            self.przycisk_dolej.setStyleSheet("background-color: pink;")
        else:
            self.czy_dolewac = False
            self.przycisk_dolej.setText("otworz zawor")
            self.przycisk_dolej.setStyleSheet("background-color: lightblue;")


         ####glowna petla aplikacji###
    def petlaGlowna(self):
        if self.czy_dolewac:
            self.zbiornik1.dolej(4.0)

        if self.zbiornik4.aktualny_poziom > 0:
            self.zbiornik4.wylej(1.0)

        for rura in self.rury:
            rura.wlacz()

        ### aktualizacja wykresow
        self.licznik += 1
        if self.licznik % 10 == 0:
            for i, z in enumerate(self.zbiorniki):
                z.historia.append(z.aktualny_poziom)
                z.historia.pop(0)
                self.lista_okien[i].odswiez_wykres(z.historia)

        self.update()


    def paintEvent(self, event):
        draw = QPainter(self)

        draw.fillRect(self.rect(), QColor(50, 50, 50))

        if self.czy_dolewac:
            pen = QPen(QColor(0,150,255), 6)
            draw.setPen(pen)
            draw.drawLine(150,0,150,100)

        for zbiornik in self.zbiorniki:
            zbiornik.narysuj(draw)
        
        for rura in self.rury:
            rura.narysuj(draw)

        for pompa in self.pompy:
            pompa.narysuj(draw)

    def closeEvent(self, event):
        for okno in self.lista_okien:
            okno.close()
        event.accept()


if __name__ == "__main__":
    app=QApplication(sys.argv)
    okno = Projekt()
    okno.show()
    sys.exit(app.exec_())