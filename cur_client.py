# -*- coding: utf-8 -*-

######################
# Import des modules #
######################



import random
import socket
import os
import sys
import pickle
import threading
import time
from _thread import *
from tkinter import *
from PIL import Image, ImageTk
from tkinter_maquette import *


###################     On est obligés de les avoir côté client
# Classes de mort #			pour que pickle fonctionne correctement
###################



class Carte:
  #La Classe Carte est la classe qui gère toutes les Cartes avec leurs attributs
  # ----------------------
  # |Numéro|Couleur|Malus|
  # ----------------------
  def __init__(self,num,couleur,malus=False):
      self.numero=num
      self.couleur=couleur
      self.malus=malus #Malus est un bool
      #Si Malus est True, le Numéro (self.numero) est le nombre de cartes à piocher.
    
  def change_couleur(self,nouv_couleur : str) -> None:
      #Uniquement pour les +4 et les changement de couleur
      self.couleur=nouv_couleur
    
  def est_jouable(self,autre_carte) -> bool:
      #On regarde si la carte est jouable sur une autre carte
      #autre_carte est une Carte
      if self.numero==autre_carte.numero:
          return True
      elif self.couleur==autre_carte.couleur:
          return True
      elif self.couleur is None or self.numero is None:
          return True
        
      return False
    
  def joker(self) -> bool:
		#Renvoie True si la carte est un joker
		#False sinon
    if self.numero is None and self.malus ==True:
      return True
    return False
    
  def passer_tour(self) -> bool:
		#Renvoie True si la carte est un "passer tour"
		#False sinon
    if self.malus and self.numero=="passer":
      return True
    return False
    
  def changement_sens(self) -> bool:
		#Renvoie True si la cartes est un changement de sens
		#False sinon
    if self.malus and self.numero=="sens":
      return True
    return False

  def __str__(self):
    carte_print = ""
    carte_print += "Numéro : "+str(self.numero) + "\n"
    carte_print += "Couleur : "+str(self.couleur) + "\n"
    if self.malus:
      carte_print += "C'est un Malus" + "\n"
    return carte_print

class Jeu:
  #Classe d'un jeu de la main d'un joueur
  def __init__(self):
    self.main=[]
  
  def main_vide(self) -> None:
    #Génère la main vide d'un joueur
    self.main==[]
  
  def est_vide(self) -> bool:
    #Renvoie True la main d'un joueur est vide, False sinon
    return self.main==[]

  def piocher(self,pile):
    #Simule l'action du joueur qui pioche une carte
    self.main.append(pile.depiler())

  def retirer(self, card):
    #Retire une carte de la main du joueur
    tmp = []
    compteur = 0
    #Transfère toutes ses cartes sauf une dans un tableau temporaire
    for k in range(len(self.main)):
      if self.main[k] != card or compteur == 1:
        tmp.append(self.main[k])
      else:
        compteur += 1
    #Remplace sa main par sa nouvelle main
    self.main = tmp.copy()

  def nb_cartes(self):
    return len(self.main)

  def __str__(self):
    leprint = ""
    for nb in range(len(self.main)):
      leprint += "---Carte n°"+str(nb+1)+"---" + "\n"
      leprint += str(self.main[nb])
    return leprint

class Pile:
    def __init__(self):
        self.valeurs = []

    def __str__(self):
        """Print une version visible de la Pile"""
        return str(self.valeurs)

    def empiler(self, valeur : Carte) -> None:
    #Empile valeur dans la pile
        self.valeurs.append(valeur)

    def depiler(self):
    #Si la pile n'est pas vide
        if not self.pilevide():
      #Retire l'élément au sommet de la pile et le renvoie
            return self.valeurs.pop()

    def pilevide(self) -> bool:
    #Renvoie True si la pile est vide, False sinon
        return self.valeurs == []

    def nb_elements(self) -> int:
    #Renvoie le nombre d'éléments de la pile
        return len(self.valeurs)

    def sommet(self):
    #Renvoie l'élément au sommet de la pile 
        if self.pilevide(): 
            return Carte(None, None, True)
        return self.valeurs[-1]

    def melanger(self) -> None:
    #Mélange la pile
        random.shuffle(self.valeurs)

class Player:
  def __init__(self, co, pseudo:str):
    self.nb = 0
    self.jeu = Jeu()
    self.pseudo = pseudo
    self.ip = co
    
  def __str__(self):
    return str(self.pseudo) + ":" + str(self.ip[0])
   
class PlayerList:
  def __init__(self):
    self.liste = list()
    
  def __getitem__(self, ip):
    for e in self.liste:
      if ip == e.ip:
        return e.pseudo
    print("Aucun joueur correspondant")

  def __setitem__(self, ip, nickname):
    for e in self.liste:
      if ip == e.ip:
        e.pseudo = nickname
        print(e)
        
  def __str__(self):
    string = ""
    for e in self.liste:
        string += str(e) + "\n"
    return string
        
  def add(self, player):
    self.liste.append(player)
    
  def remove(self, ip):
    for e in self.liste:
      if ip == e.ip:
        self.liste.remove(e)
        
  def getname(self, n):
    for e in self.liste:
      if n == e.nb:
        return e.pseudo

testJeu=Jeu()
testCard=Carte(0,"bleu")

#############################
# Fonctions pour le tkinter #
#############################



def creation_fenetre(fenetre):
    """permet de définir la taille de la fenêtre (ici résolution 1280x720)
              de le centrer au milieu de l'écran
              et de faire en sorte que l'utilisateur ne puisse pas changer la taille
              de le nommer
    """

    #Récupérer la résolution de l'écran utilisé
    screen_x = int(fenetre.winfo_screenwidth())
    screen_y = int(fenetre.winfo_screenheight())

    #Entrer les valeurs de taille de la fenêtre
    window_x = 1280
    window_y = 720

    #Calcul des coordonnées pour que la fenêtre soit au milieu
    pos_x = (screen_x // 2) - (window_x // 2)
    pos_y = (screen_y // 2) - (window_y // 2)
    geo = "{}x{}+{}+{}".format(window_x, window_y, pos_x, pos_y)

    fenetre.geometry(geo)
    #On bloque la taille en 500x500
    fenetre.resizable(width=False, height=False)
    fenetre.title("Amoguno")


def valider(saisie:str):
    global  _saisie
    if saisie == "endconn":
        fen.root.destroy()
    Psend(saisie)
    _saisie.delete(0, END)

def console_view(app):
    global console, _saisie
    
    canva = Canvas(app, height=720, width=340)

    #Console
    console = Text(canva)
    console.place( x=20, y = 20, height = 460, width = 300)
    
    #Saisie
    saisie = StringVar(app)
    _saisie = Entry(canva, font=("Bahnschrift",12),textvariable = saisie, bg = "#F3b3f2", borderwidth = 4)
    _saisie.place(x = 20, y = 480, height = 40, width = 300)
    
    """
    #Historique
    historique = Text(canva)
    historique.place(x=960, y = 20, height = 460, width = 300)
    """
    
    #Buton Validai
    validai = Button(canva, command = lambda:valider(saisie.get()), bg = "#16fa52", text="Valider", borderwidth = 2)
    validai.place(x = 20, y = 540, height = 160, width = 300)
    
    return canva

console, _saisie = None, None

##############################################
# Canvas et Objets reliés au jeu en lui-même #
##############################################

gameCanva=None

def displayPioche(fen):
    """Fonction qui display le bouton de pioche
    La commande Psend(0) Correspond à la commande de pioche"""
    p=Button(fen, text="Piocher", command=lambda :Psend("0"), cursor="hand2")
    p.place(x=120,y=575)

def readSupport(fen,carte):
    
    if carte is None:
        return
    
    """Fonction de lecture de la carte support"""
    i=carte
    if i.couleur=="rouge":
        imgColor="red"
        imgNum=i.numero
        imgName=f"las_cuartas\\{imgColor}_{imgNum}.png"
    elif i.couleur=="vert":
        imgColor="green"
        imgNum=i.numero
        imgName=f"las_cuartas\\{imgColor}_{imgNum}.png"
    elif i.couleur=="jaune":
        imgColor="yellow"
        imgNum=i.numero
        imgName=f"las_cuartas\\{imgColor}_{imgNum}.png"
    elif i.couleur=="bleu":
        imgColor="blue"
        imgNum=i.numero
        imgName=f"las_cuartas\\{imgColor}_{imgNum}.png"
    
    elif i.couleur is None:
        if i.numero is None:
            imgName="las_cuartas\\joker.png"
        else:
            imgName="las_cuartas\\+4.png"
    
    tmp=Image.open(imgName).resize((61,95))
    fen.imgReal=ImageTk.PhotoImage(tmp)
    
    l=Label(fen,text=f"Carte Support :\n {carte.numero}\n{carte.couleur}",image=fen.imgReal)
    l.image=fen.imgReal
    l.place(x=120, y=420)

def readGameCanva(fen, hand):
    """Fonction de lecture du jeu (argument hand) et affichage dynamique en Tkinter
    Pour plus de fun, on mettre cete fonction dans le code client, dans le thread de
    récéption afin qu'elle soit continuellement mise à jour"""
    
    if hand is None:
        return

    v=0    
    for i in hand.main:
        #NOTE IMPORTANTE : Lors de l'utilisation d'une lambda, il faut RÉASSIGNER la variable à elle même AVANT !
        if i.couleur=="rouge":
            imgColor="red"
            imgNum=i.numero
            imgName=f"las_cuartas\\{imgColor}_{imgNum}.png"
            
        elif i.couleur=="vert":
            imgColor="green"
            imgNum=i.numero
            imgName=f"las_cuartas\\{imgColor}_{imgNum}.png"
            
        elif i.couleur=="jaune":
            imgColor="yellow"
            imgNum=i.numero
            imgName=f"las_cuartas\\{imgColor}_{imgNum}.png"
            
        elif i.couleur=="bleu":
            imgColor="blue"
            imgNum=i.numero
            imgName=f"las_cuartas\\{imgColor}_{imgNum}.png"
            
        elif i.couleur is None:
            if i.numero is None:
                imgName="las_cuartas\\joker.png"
                
            else:
                imgName="las_cuartas\\+4.png"
        
        tmp=Image.open(imgName).resize((61,95))
        fen.imgReal=ImageTk.PhotoImage(tmp)
        
        e=Button(fen, text=f"{i.numero}\n{i.couleur}",command=lambda v=v:Psend(str(v+1)),cursor="hand2", image=fen.imgReal) #on change le curseur de type  command=lambda i=i:print(i),cursor="hand2" , 
        e.image=fen.imgReal #TOUJOURS METTRE CETTE LIGNE!!! Cela permet d'afficher correctement l'image en gardant un index de l'image (comme le i=i du lambda au dessu !)
        
        e.place( x=(v*61)+20, y=605 )
        
        v+=1


def game_view(app, handToDisplay, cardToDisplay):
    global gameCanva
    
    try:
        gameCanva.destroy()
    except:
        pass
    
    gameCanva=Canvas(app, heigh=720, width = 940, bg ="#FCEEFA")

    test=Button(gameCanva, text="Test Test Test", command=lambda : fen.updateGame(handToDisplay))
    test.place(x=20,y=20,height=80, width = 120)
    
    readGameCanva(gameCanva,handToDisplay)
    readSupport(gameCanva, cardToDisplay)
        
    displayPioche(app)
    
    gameCanva.update_idletasks()
    
    return gameCanva

###############################################
# Classe qui gère le multithread avec tkinter #
###############################################

a=Carte(7,"rouge")
b=Carte(None, None, True)
c=Carte("+2","vert",True)
pileTest=Pile()
pileTest.empiler(a)
pileTest.empiler(b)
pileTest.empiler(c)
handTestTemp=Jeu()

d=Carte(3,"rouge")

for _ in range(3):
    handTestTemp.piocher(pileTest)

class App(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.start()

    def callback(self):
        try:
            Psend("endconn")
        except:
            pass
        self.root.quit()
        
    def run(self):
        
        self.root = Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.callback)

        creation_fenetre(self.root)
        # Création de l'acceuil
        menu = console_view(self.root)
        menu.pack(side=RIGHT)
        
        jeuTkinter = game_view(self.root, handTestTemp,d)
        jeuTkinter.pack(side=LEFT)
        
        self.root.mainloop()
    
    def addconsole(self, txt : str):
        global console
        console.insert(END, txt + "\n")
        
    def updateGame(self, newGame, newCard):

        jeuTkinter = game_view(self.root,newGame, newCard)

        jeuTkinter.pack(side=LEFT)
        jeuTkinter.update()
        jeuTkinter.update_idletasks()
        
        self.root.update()


fen = App()

###########################################
# Gestion de la discussion avec le server #
###########################################

#91.160.34.220
ip="localhost"
port=55555

client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect((ip,port))

def Psend(msg):
    """Load un objet dans pickle et l'envoie au serveur"""
    msg=pickle.dumps(msg)
    #print(msg)
    client.send(msg)

def receive():
    recvCompte=0
    #Fonction définie a être lue sur un thread a part, Faite pour recevoir les données
    #A Run en PERMANENCE
    while True:
        #data=client.recv(2048).decode('utf-8') Old
        data=pickle.loads(client.recv(4096))
        if type(data)==tuple:
            recvDeck=data[1]
            recvCard=data[0]
            fen.updateGame(recvDeck, recvCard)

        if data:
            #data_var=pickle.loads(data)
            fen.addconsole(str(data))
            #print(data.decode('utf-8'))
    sys.Exit()
    
try:
    start_new_thread(receive,())
except:
    print("UNABLE TO LAUNCH RECEIVE THREAD")


    
