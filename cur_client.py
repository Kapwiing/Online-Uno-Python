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
      """
      if self.couleur is not None and self.couleur.startswith('"'):
          self.couleur=self.couleur[1:len(self.couleur)-1]
      """
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
  
  def fichierimg(self):
      """Renvoie le chemin d'accès à l'image de la carte"""
      
      if self.couleur is None:
          if self.numero is None:
              return "las_cuartas\\joker.png"               
          elif self.numero=="+4":
              return "las_cuartas\\+4.png"
      else:
        return f"las_cuartas\\{self.couleur}_{self.numero}.png"

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
    
    canva = Canvas(app, height=720, width=340,bg ="#EBFCFF",bd=0,highlightthickness=0,relief='ridge')

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
    p.place(x=370,y=450, height=70, width=120)

def readSupport(fen,carte):
    
    if carte is None:
        return
    
    """Fonction de lecture de la carte support"""
    i=carte
    
    imgName=i.fichierimg()

    tmp=Image.open(imgName).resize((92,143))
    fen.imgReal=ImageTk.PhotoImage(tmp)
    
    l=Label(fen,text=f"Carte Support :\n {carte.numero}\n{carte.couleur}",image=fen.imgReal)
    l.image=fen.imgReal
    l.place(x=378, y=217)

def displayEnemyHand(fen, num):
    """Fonction qui affiche le nombre num de cartes de l'adversaire dans le canvas fen"""
    if num is None or num ==0:
        return
    imgName="las_cuartas\\uno_back.png"
    for v in range(num):
        tmp=Image.open(imgName).resize((61,95))
        fen.imgReal=ImageTk.PhotoImage(tmp)
        
        e=Label(fen, image=fen.imgReal)
        e.image=fen.imgReal
        
        e.place(x=(v*61)+20, y=10)
    

def readGameCanva(fen, hand):
    """Fonction de lecture du jeu (argument hand) et affichage dynamique en Tkinter
    Pour plus de fun, on mettre cete fonction dans le code client, dans le thread de
    récéption afin qu'elle soit continuellement mise à jour"""
    
    if hand is None:
        return

    v=0    
    for i in hand.main:
        #NOTE IMPORTANTE : Lors de l'utilisation d'une lambda, il faut RÉASSIGNER la variable à elle même AVANT !
        imgName=i.fichierimg()
        
        tmp=Image.open(imgName).resize((61,95))
        fen.imgReal=ImageTk.PhotoImage(tmp)
        
        e=Button(fen, text=f"{i.numero}\n{i.couleur}",command=lambda v=v:Psend(str(v+1)),cursor="hand2", image=fen.imgReal) #on change le curseur de type  command=lambda i=i:print(i),cursor="hand2" , 
        e.image=fen.imgReal #TOUJOURS METTRE CETTE LIGNE!!! Cela permet d'afficher correctement l'image en gardant un index de l'image (comme le i=i du lambda au dessu !)
        
        e.place( x=(v*61)+20, y=605 )
        
        v+=1

def game_view(app, handToDisplay, cardToDisplay, enemyNumToDisplay):
    global gameCanva
    
    try:
        gameCanva.destroy()
    except:
        pass
    
    gameCanva=Canvas(app, heigh=720, width = 940, bg ="#EBFCFF", bd=0, highlightthickness=0, relief='ridge') # Création du Canvas de jeu auquel en enlève la Bordure par défaut avec "bd=0,highlightthickness=0,relief='ridge'"
    
    readGameCanva(gameCanva,handToDisplay)
    readSupport(gameCanva, cardToDisplay)
    displayEnemyHand(app, enemyNumToDisplay)
    
    displayPioche(app)
    
    
    gameCanva.update_idletasks()
    
    return gameCanva

def changeColorSend(color):
    global buttonRed,buttonBlue,buttonGreen,buttonYellow
    Psend(color)
    try:
        buttonRed.destroy()
        buttonBlue.destroy()
        buttonGreen.destroy()
        buttonYellow.destroy()
    except:pass

buttonRed,buttonBlue,buttonGreen,buttonYellow=None,None,None,None

def colorChoice_view(app):
    """Fonction qui crée les boutons pour choisir la couleur dans le canvas app en argument"""
    global buttonRed,buttonBlue,buttonGreen,buttonYellow
    
    try:
        buttonRed.destroy()
        buttonBlue.destroy()
        buttonGreen.destroy()
        buttonYellow.destroy()
    except:pass

    buttonRed=Button(app, text="Rouge", command=lambda:changeColorSend("rouge"))
    buttonBlue=Button(app,text="Bleu", command=lambda:changeColorSend("bleu"))
    buttonGreen=Button(app, text="Vert", command=lambda:changeColorSend("vert"))
    buttonYellow=Button(app, text="Jaune", command=lambda:changeColorSend("jaune"))
    
    buttonRed.place(x=5, y=120, height=20, width=90)
    buttonBlue.place(x=95, y=120, height=20, width=90)
    buttonGreen.place(x=185, y=120, height=20, width=90)
    buttonYellow.place(x=275, y=120, height=20, width=90)


###############################################
# Classe qui gère le multithread avec tkinter #
###############################################

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

        self.root.iconphoto(False, PhotoImage(file='icon.png'))
        creation_fenetre(self.root)
        # Création de l'acceuil
        menu = console_view(self.root)
        menu.pack(side=RIGHT)
        
        self.root.mainloop()
    
    def addconsole(self, txt : str):
        """Méthode qui ajoute la console à la fenêtre"""
        global console
        console.insert(END, txt + "\n")
        
    def updateGame(self, newGame, newCard, newEnemyNum):
        """Méthode appelée à chaque récéption de Jeu/Carte/Nombre de Cartes de l'adversaire"""
        self.jeuTkinter = game_view(self.root,newGame, newCard, newEnemyNum)

        self.jeuTkinter.pack(side=LEFT)
        self.jeuTkinter.update()
        self.jeuTkinter.update_idletasks()
        
        self.root.update()

    def colorChoice(self):
        
        colorChoice_view(self.jeuTkinter)
        
        self.jeuTkinter.pack(side=LEFT)
        self.jeuTkinter.update()
        self.jeuTkinter.update_idletasks()
        
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
    if msg=="testBalls":
        fen.colorChoice()
    if msg=="rouge" or msg=="vert" or msg=="jaune" or msg=="bleu":
        msg=f"\"{msg}\""
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
            recvCard, recvDeck,recvOtherNum = data
            fen.updateGame(recvDeck, recvCard, recvOtherNum)
            
        elif data and type(data)!=tuple:
            if str(data)=="cheeseColor":
                fen.colorChoice()
                
            #data_var=pickle.loads(data)
            fen.addconsole(str(data))
            #print(data.decode('utf-8'))
    sys.Exit()
    
try:
    start_new_thread(receive,())
except:
    print("UNABLE TO LAUNCH RECEIVE THREAD")
