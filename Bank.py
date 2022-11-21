
# -*- coding: utf-8 -*-

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

#KIR zdefiniowany jako Singelton 
class KIR(metaclass = Singleton):
	def __init__(self):
		self._bankDic = dict()

	def dodajBank(self,bankNazwa, bank):
		self._bankDic[bankNazwa]=bank

	def przekieruj(self, przelew):
		self._bankDic[przelew._bankOdbiorcy].zaksieguj(przelew)



class IRachunek(object): #Informal interface

	def ustawOdsetki (self, ods):
		pass

	def numer(self):
		pass

	def wlasciciel(self):
		pass

	def saldo(self):
		pass

	def piszHistorie(self):
		pass

	def wplata(self, kwota):
		pass

	def wyplata(self, kwota):
		pass

	def odsetki(self):
		pass

class Rachunek(IRachunek):
	def __init__(self, numer, imie, nazwisko):
		self._historia = list()
		self._numer = numer
		self._imie = imie
		self._nazwisko = nazwisko
		self._saldo = 0
		self._odsetki=OdsetkiA()

	def ustawOdsetki (self, ods):
		self._odsetki=ods

	def numer(self):
		return self._numer

	def wlasciciel(self):
		return self._imie + " " + self._nazwisko

	def saldo(self):
		return self._saldo

	def piszHistorie(self):
		print(self._historia)

	def wplata(self, kwota):
		self._saldo += kwota
		self._historia.append("Wpłata: " + str(kwota) + ", saldo: " + str(self._saldo))
		return 0

	def wyplata(self, kwota):
		if self._saldo  >= kwota:
			self._saldo -= kwota
			self._historia.append("Wypłata: " + str(kwota) + ", saldo: " + str(self._saldo))
			return 0
		self._historia.append("Nieudana wypłata: " + str(kwota) + ", saldo: " + str(self._saldo))
		return -1

	def odsetki(self):
		return self._odsetki.oblicz(self)

class RachunekDebetowy(IRachunek):
	def __init__(self,rachunek,maxDebet):
		self._rachunek = rachunek
		self._debet = 0
		self._maxDebet = maxDebet

	def ustawOdsetki (self, ods):
		self._rachunek.ustawOdsetki(ods)

	def numer(self):
		return self._rachunek.numer()

	def wlasciciel(self):
		return self._rachunek.wlasciciel()

	def saldo(self):
		return self._rachunek.saldo()

	def piszHistorie(self):
		self._rachunek.piszHistorie()

	def wplata(self, kwota):
		self._debet -= kwota
		if self._debet < 0:
			self._rachunek.wplata(-self._debet)
			self._debet = 0
		self._rachunek._historia.append("Debet: " + str(self._debet))

	def wyplata(self,kwota):
		if (kwota < self._maxDebet - self._debet + self._rachunek.saldo()):
			if kwota <= self._rachunek.saldo():
				self._rachunek.wyplata(kwota)
			else:
				delta = kwota - self._rachunek.saldo()
				self._debet = self._debet + delta
				self._rachunek.wyplata(kwota-delta)
				self._rachunek._historia.append("Debet: " + str(self._debet))

	def odsetki(self):
		return self._rachunek.odsetki()
		

class Bank(object):
	def __init__(self,nazwa):
		self._nazwa = nazwa
		self._rachunki = dict() 
		self._kir = KIR() #KIR jest singeltonem co gwarantuje istnienie dokładnie 1 instancji tego obiektu
		self._kir.dodajBank(self._nazwa,self) #automatyczna dopisanie do subskrybcji w KIR po nazwie banku

	def zalozRachunek(self, numer, imie, nazwisko):
		rach = Rachunek(numer, imie, nazwisko)
		self._rachunki[numer] = rach

	def szukaj(self, numer):
		if numer in self._rachunki.keys():
			return self._rachunki[numer]
		return None

	def zaksieguj(self,przelew):
		if self.szukaj(przelew._odbiorca):
			self.szukaj(przelew._odbiorca).wplata(przelew._kwota)
		else:
			self._kir.przekieruj(Przelew(przelew._odbiorca,przelew._nadawca, przelew._bankOdbiorcy, przelew._bankNadawcy, przelew._kwota))


	def zleceniePrzelewu(self,nadawca,odbiorca,bankOdbiorcy,kwota):
		if self.szukaj(nadawca):
			if self.szukaj(nadawca).wyplata(kwota)==0:
				self._zleceniePrzelewu = Przelew(nadawca,odbiorca,self._nazwa,bankOdbiorcy,kwota)
				self._kir.przekieruj(self._zleceniePrzelewu)

	def przeksztalcRachunekWDebetowy(self,numer,maxDebet):
		if numer in self._rachunki.keys():
			self._rachunki[numer] = RachunekDebetowy(self._rachunki[numer],maxDebet)
			return 0
		return -1


class IOdsetki(): #Informal interface
	def oblicz(self,rachunek):
		pass
	def nazwa():
		pass
		
class OdsetkiA(IOdsetki,metaclass = Singleton):
	def oblicz(self,rachunek):
		odsetki = (0.01 * rachunek.saldo())
		return odsetki

	def nazwa(self):
		return"ROR 1%"

class OdsetkiB(IOdsetki,metaclass = Singleton):
	def oblicz(self,rachunek):
		odsetki = (0.05 * rachunek.saldo())
		return odsetki

	def nazwa(self):
		return"Lokata premium 5%"

class Przelew():
	def __init__(self,nadawca,odbiorca,bankNadawcy,bankOdbiorcy,kwota):
		self._nadawca = nadawca
		self._odbiorca = odbiorca
		self._bankNadawcy = bankNadawcy
		self._bankOdbiorcy = bankOdbiorcy
		self._kwota = kwota
		
		
def main():
	bank = Bank("Santander")
	bank2 = Bank("PKO")

	#Rachunki w Santander
	bank.zalozRachunek("20_0001", "Jan", "Kowalski")
	bank.zalozRachunek("20_0002", "Jacek", "Nowak")
	bank.szukaj("20_0001").wplata(1000)
	bank.szukaj("20_0002").wplata(1000)
	bank.szukaj("20_0002").ustawOdsetki(OdsetkiB()) #odsetki typu super lokata 5%
	bank.przeksztalcRachunekWDebetowy("20_0002",10000) #przyznana linia kredytowa 10 000

	bank.szukaj("20_0001").wplata(bank.szukaj("20_0001").odsetki()) #kapitalizacja 1%
	bank.szukaj("20_0002").wplata(bank.szukaj("20_0002").odsetki()) #kapitalizacja 5%


	#Rachunki w PKO
	bank2.zalozRachunek("55_0001", "Adrian", "Duda")

	bank2.szukaj("55_0001").wplata(500)

	#Przelew do istniejącego odbiorcy
	bank.zleceniePrzelewu("20_0001","55_0001","PKO",700)
	#Przelew do nieistniejącego odbiorcy
	bank2.zleceniePrzelewu("55_0001","20_0003","Santander",300)



	bank.szukaj("20_0001").wyplata(5000) #wypłata ponad stan -> nie udana
	bank.szukaj("20_0002").wyplata(5000) #wypłata ponad stan _> uruchomienie linii kredytowej
	bank.szukaj("20_0002").wplata(6000) #spłata kredytu w pierwszej kolejnosci


	bank.szukaj("20_0001").piszHistorie()
	bank.szukaj("20_0002").piszHistorie()
	bank2.szukaj("55_0001").piszHistorie()
	



main()
