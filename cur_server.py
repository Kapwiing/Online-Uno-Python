# -*- coding: utf-8 -*-

######################
# Import des modules #
######################



import os
import sys
import socket
import random
import time
import pickle
from _thread import *



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
    if self.numero is None and self.malus:
      return True
    return False
    
  def passer_tour(self) -> bool:
		#Renvoie True si la carte est un "passer tour"
		#False sinon
    if self.malus and self.numero=="passer":
      return True
    return False
    
  def changement_sens(self) -> bool:
		#Renvoie True si la carte est un changement de sens
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

  def __setitem__(self, ip, nickname):
    for e in self.liste:
      if ip == e.ip:
        e.pseudo = nickname
        print(e)
        
  def __str__(self):
    string = "Voici la liste des joueurs : \n"
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
      
class Game:
  def __init__(self, tab):
    self.pioche = Pile()     #Pioche du jeu
    self.support = None      #Dernière carte sur la pile des cartes posées
    self.posees = Pile()     #Pile des cartes posées
    self.joueurs = ["_"] + tab.liste #Liste des joueurs
    self.sens = True         #Sens de départ

  def startgame(self):

    #On place le n° du prochain joueur dans self.joueurs[0]
    self.joueurs[0] = 1

    #faudra check si l'indice du player dans le tableau = (self.joueurs[0]%(len(self.joueurs)-1))+1
    #si oui il peut jouer
    for k in range(len(self.joueurs)):
      if k != 0: self.joueurs[k].nb = k

    #Génère la pioche contenant toutes les cartes du jeu
    self.pioche = creation_cartes()


    #Mélange la pioche bien comme il faut
    for _ in range(random.randint(1,5)):
      self.pioche.melanger()

    #Distribue 7 cartes à chacun des joueurs
    for a_distribuer in range(len(self.joueurs)-1):
      self.joueurs[a_distribuer +1].nb = a_distribuer +1
      for _ in range(7):      
        self.joueurs[a_distribuer +1].jeu.piocher(self.pioche)

    #Pose la première carte qui signe le début de la partie
    #En s'assurant que cette carte n'est pas un malus
    while self.posees.sommet().malus:
      self.posees.empiler(self.pioche.depiler())
    self.support = self.posees.sommet()
    self.tour()
  
  def tour(self, sameplayer = False):
    """Gère le tour"""
    global played
    
    
    played, ok = False, False
    
    if not sameplayer:
        #sendBroadcast("Carte support : \n")
            
        #Chaque joueur reçoit son jeu
		#A modifier plus tard pour le nb de cartes des autres joueurs et tout
        k=0
        for joueur in players.liste:
            if k==0:
                otherJeu=len(players.liste[1].jeu.main)
            elif k==1:
                otherJeu=len(players.liste[0].jeu.main)
            Psend(connList[joueur.ip],(self.support,joueur.jeu,otherJeu))
            k+=1
        sendBroadcast(f"C'est le tour du joueur {self.joueurs[0]}")
			
    player = self.joueurs[self.joueurs[0]]
    Psend(connList[player.ip],"Entrez le n° de la carte à jouer. Ou entrez 0 pour piocher \n")

    #On attend que le joueur aie choisit son action
    while played is False:
	    time.sleep(1)

    while not ok:

      #Si le joueur pioche
      if played == 0:

          #On lui fait piocher une carte
          #Puis on passe au  tour de la personne suivante
          player.jeu.piocher(self.pioche)
          self.prochain_tour()
          self.tour()

          #On sort de la boucle
          ok = True
      
	  #Sinon, on s'assure que la carte est bien dans le jeu du joueur
      elif played <= player.jeu.nb_cartes():

          #On récupère la carte que le joueur veut poser
          card = player.jeu.main[played-1]

      #Si la carte est jouable
      if played <= player.jeu.nb_cartes() and card.est_jouable(self.support):

          #On pose la carte
          #On applique les effets éventuels de la carte
          self.poser_carte(card, player)
          self.prochain_tour()
          self.apply_effects()

          #On vérifie si le joueur a gagné
          if not self.is_Winner():

              #Sinon on passe au joueur suivant
              self.tour()

          #On sort de la boucle
          ok = True
      
	  #Sinon, on fait savoir au joueur que 
      else:
        Psend(connList[player.ip], "La carte entrée ne peut pas être posée")
        self.tour(True)

  def apply_effects(self):
    """Check des effets eventuels de la carte posée qui devient support"""
    global _new_colour
    global connList
    global askingColor
    
    if self.support.malus:
      if self.support.passer_tour():
        #Dans le cas où la carte est un passement de tour
        self.prochain_tour()

      elif self.support.changement_sens():
        #Dans le cas où la carte est un changement de sens
        self.sens = not self.sens
        self.prochain_tour()
        self.prochain_tour()

      elif self.support.numero == "+2":
        #Dans le cas où la carte est un +2
        self.joueurs[self.joueurs[0]].jeu.piocher(self.pioche)
        self.joueurs[self.joueurs[0]].jeu.piocher(self.pioche)
        self.prochain_tour()

      elif self.support.couleur is None:
        #Dans le cas où on a un joker ou un +4
        #On cherche d'abord à recupérer la personne qui doit décider de la couleur de la carte
        if self.sens:
          decideur = self.joueurs[0] -1
          if decideur == 0: decideur = len(self.joueurs) -1
        else:
          decideur = (self.joueurs[0] % (len(self.joueurs) -1)) +1

        sendBroadcast(f"Le joueur n°{decideur} doit décider de la couleur de la carte.")

        player = self.joueurs[decideur]
        Psend(connList[player.ip],"Merci de choisir la couleur de la carte \n")
        time.sleep(0.5)
        Psend(connList[player.ip], "cheeseColor")
        
        _new_colour=None
        askingColor=True
        
        while _new_colour is None:
            time.sleep(1)
        
        while askingColor:
            if _new_colour!=None:
                askingColor=False
        
        
        sendBroadcast(f"Nouvelle couleur est : {_new_colour}.\n")
            
        self.support.change_couleur(_new_colour)
        
        #Pour le cas où la carte est un joker
        while _new_colour is None:
            time.sleep(1)
        
        print(_new_colour)       
          
        _new_colour = None
        
        if not self.support.joker():
          #Dans le cas où la carte est un +4
          for _ in range(4):
            self.joueurs[self.joueurs[0]].jeu.piocher(self.pioche)
          self.prochain_tour()

  def prochain_tour(self):

    if self.sens:
      #Si on joue dans le sens normal
      self.joueurs[0] = (self.joueurs[0] % (len(self.joueurs) -1)) +1

    else:
      #Si on est en sens inverse
      self.joueurs[0] -=1
      if self.joueurs[0] == 0:
        self.joueurs[0] = len(self.joueurs) -1

  def is_Winner(self):
    for nb in range(len(self.joueurs)-1):
      if self.joueurs[nb+1].jeu.est_vide():
        sendBroadcast(f"Félicitations, le joueur {nb+1} a gagné. \n")
        sendBroadcast("La partie est Finie, vous pouvez quitter la Salle de Jeu")
        print(f"Félicitations, le joueur {nb+1} a gagné. \n")
        return True

  def restart(self):
    #Vide les mains de deux joueurs puis lance une nouvelle partie
    self.joueurs = []
    self.startgame()
    
  def poser_carte(self, card, player):
    """Pose la carte sur la pile, ce qui en fait le nouveau support
       Et la retire de la main du joueur"""
    if card.est_jouable(self.support):
      self.posees.empiler(card)
      self.support = card
      player.jeu.retirer(card)



##############################
# Fonction(s) en lien au jeu #
##############################



def creation_cartes() -> list:
  """Crée un pile avec toutes les cartes"""
  pile_cartes = Pile()
  lst_couleurs = ["rouge","vert","bleu","jaune"]
  for couleur in lst_couleurs:
    for nb in range(10):
      pile_cartes.empiler(Carte(nb, couleur))
      if not nb == 0: pile_cartes.empiler(Carte(nb, couleur))
    for compteur in range(2):
      pile_cartes.empiler(Carte("+2",couleur,True))
      pile_cartes.empiler(Carte("sens",couleur,True))
      pile_cartes.empiler(Carte("passer",couleur,True))
  for compteur in range(4):
    pile_cartes.empiler(Carte("+4",None,True))
    pile_cartes.empiler(Carte(None, None, True))
  
  return pile_cartes



#################################
# Création/ouverture du serveur #
#################################



ip='localhost'
port=55555

#Nombre de clients maximums pour le serveur
desiredClients=2

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#server.bind(("127.0.0.1",55555))
#server.listen(2)
print("**Serveur en Démarrage...**\n")

try :
    server.bind((ip,port))
    server.listen(desiredClients)
    print("**Serveur en Ligne !!**\n")
except ConnectionError() as e:
    print(e)

players=PlayerList()
clientCount=0
runAll=True # PAS TOUCHE, Valeur qui déterminer si les threads fonctionnent
gameReady=False
played = False

connList={} #-Liste- dictionnaire des connexions utilisée pour les broadcasts



##############################
# Fonctions liées au serveur #
##############################



def askEnd():
    """commande poue éteindre le serveur A voir si utile"""
    global clientCount
    global runAll
    if clientCount==0:
        ans=input("Personne n'est connecté, voulez vous fermer le serveur ?(o/n) : ")
        if ans=="o":
            runAll=False
            sys.exit()
        else:
            print("Commande ignorée")

def Psend(c,msg):
    """Fonction pour envoyer un message via pickle
    Arguments : c = connection
                msg = message qui sera pickle.dumps et c.send"""
    c.send(pickle.dumps(msg))
    
    
#   / ! \                                                    / ! \
#  /  !  \  NE SURTOUT PAS RENOMMER LA FONCTION CI DESSOUS  /  !  \
# /   !   \      CELA DÉTRUIRAIT L'ESPACE TEMPS MARTY!!    /   !   \

def clbonjueur(connection):
    """Fonction qui renvoie True si la personne qui vient de jouer
    est bien la personne don c'est le tour"""
    global connList
    global t
    
    lbonjueur = t.joueurs[t.joueurs[0]]
    return connection == connList[lbonjueur.ip]

#   / ! \                                                    / ! \
#  /  !  \  NE SURTOUT PAS RENOMMER LA FONCTION CI DESSUS   /  !  \
# /   !   \      CELA DÉTRUIRAIT L'ESPACE TEMPS MARTY!!    /   !   \

askingColor=False
def threaded(connection, ip):
    """THREAD DE LA GESTION DE CLIENTS"""
    global clientCount
    global runAll
    global players
    global played
    global _new_colour
    global askingColor
    
    #On attribue un pseudo pour chaque joueur
    key=ip[0] #Clé dans le dictionnaire des joueurs
    key=ip[1] #Temporaire (Pour le travail en local host)
    players.add(Player(ip,"Guest"+str(ip[1])))
    print(players)
    
    clientCount+=1
    
    print("Nouveau Client en cours de connexion")
    print(f"Connecté à : {ip}")
    
    Psend(connection,f"Vous êtes le : {clientCount}eme Joueur")
    Psend(connection,f"Votre pseudo est : {players[ip]}")
    
    print(f"\nLe nombre de clients est maintenant de {clientCount}")
    while runAll:
        try:
            #print(connection.recv(4096))
            msg=pickle.loads(connection.recv(4096))
            #print("Obj Reçu")
            #msg=msg.decode('utf-8')
            print(f"Recu : {msg} de {players[ip]}")
            #connection.sendall(f"Recu : {msg}")
            
            if msg=="endconn" or not msg:
                #Si le message reçu est "endconn" la connection s'arrette
                
                print(f'**Déconneté de : {ip}**\n')
                Psend(connection,"Fermeture de la connection")
                players.remove(ip)
                clientCount-=1
                print(f"Nombre de clients : {clientCount}\n")
                
                connection.close()
                sys.exit()
                break
                return False
            
            elif msg=="plList":
                Psend(connection,"Voici la liste des joueurs : ")
                Psend(connection,players)
            
            elif msg=="help":
                Psend(connection, "Liste des commandes :\nplList : Affiche la liste des joueurs connectés\nendconn : Ferme la connection\nhelp : Affiche cette liste")
        
            #no surtout pas renommer la fonction ci dessous
            #sous peine de détruire l'espace temps marty
            if type(eval(msg)) == int:
                
                if clbonjueur(connection): played = int(msg)
                
                else: Psend(connection, "Ce n'est pas votre tour !")
            
            
            if eval(msg) == "rouge" or eval(msg)=="bleu" or eval(msg)=="vert" or eval(msg) =="jaune":
                if askingColor:
                    print(f"{str(msg)} est la nouvelle couleur")
                    msg=msg[1:len(msg)-1]
                    _new_colour=msg
                    askingColor=False
                
            else:
                pass
                #Psend(connection,f"Unkown command \"{msg}\" ")
                
        except:pass#Mettre une exception ici après
    connection.close()
    sys.exit()

#NB : Il est important de déclarer les variables en global afin d'avoir un droit
#de modification dessus et pas seulement de lecture
def handleJeu():
    global gameReady
    global players
    global broadcast
    global connList
    global clientCount
    global t
    
    oka=True
    while oka:
        if clientCount==2:
            time.sleep(1)
            t = Game(players)
            t.startgame()
                
            time.sleep(1)#On attend que le broadcast soit fini
            
            #response=pickle.loads(connList[pnum].recv(4096))
            #print(response)
            
            oka = False
    sys.exit()            

def sendBroadcast(msg):
    for c in connList.values():
        Psend(c,msg)
        
okb=True
def checkForReady():
    global clientCount
    global okb
    while okb:
        if clientCount>=2:
            sendBroadcast("Partie Prête à commencer")
            okb=False

_new_colour = None            
t = "haaaaaaaaaaaaaan"
start_new_thread(handleJeu,())


#----Main Run Loop----
while runAll:
    #On accepte en permanence les demandes de connexion au serveur
    connection,ip = server.accept()
    connList[ip] = connection
    print(connection,ip)
    #Start un nouveau "threaded" pour chaque client
    start_new_thread(threaded ,(connection, ip))