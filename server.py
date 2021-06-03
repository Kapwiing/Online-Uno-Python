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
import sqlite3
from _thread import *
from cryptography.fernet import Fernet



#########################################################
#####     Système de cryptage des mots de passe     #####
#########################################################



str_key = open("key.txt.txt","r").readline()
key = str.encode(str_key)
f = Fernet(key)



###################################
# Connection à la base de données #
###################################



base = sqlite3.connect("player_list.db", check_same_thread=False)
cur = base.cursor()



#############################################
# Fonctions en lien avec la base de données #
#############################################


def signin_signup(connection, ip, msg):
    global players
    #Si le message est une requête de connection
    if msg[0] == "signin":

        #On récupère les infos entrées
        e, ide, mdp = msg
        
        #On tente ensuite de récupérer les infos du joueur
        try:
            cur.execute("SELECT mdp FROM Joueurs WHERE Pseudo = ?", (ide,))
            vraimdp = cur.fetchall()[0][0]
            
            #On vérifie si les mdp correspondent
            if f.decrypt(vraimdp) == f.decrypt(mdp):
                
                #On récupère les stats du joueur
                cur.execute("SELECT Wins FROM Joueurs WHERE Pseudo = ?",(ide,))
                nb_wins = cur.fetchall()[0][0]

                cur.execute("SELECT Parties FROM Joueurs WHERE Pseudo = ?",(ide,))
                nb_parties = cur.fetchall()[0][0]

                cur.execute("SELECT Elo FROM Joueurs WHERE Pseudo = ?",(ide,))
                elo = cur.fetchall()[0][0]
                
                Psend(connection, ("online moment", nb_wins, nb_parties, elo))
                players[ip] = ide

            else:
                print("mové mdp")
                Psend(connection, "signin entry error")
        
        except:
            print("je sui kacé")
            Psend(connection, "signin entry error")
                        

    elif msg[0] == "signup":
        
        e, ide, mdp = msg
        try:
            
            #On entre les infos de la personne dans la base de données
            cur.execute('INSERT INTO Joueurs VALUES(?,?,0,0,800)',(ide,mdp))
            base.commit()
            
            #On confirme l'inscription
            Psend(connection, "registration moment")
            
            #Si un problème se produit lors de l'inscription
        except:
            Psend(connection, "signup entry error")


###################         On est obligés de les avoir ici
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

  def fichierimg(self):
    if self.couleur is None:
        if self.numero is None:
            return "las_cuartas\\joker.png"               
        else:
            return "las_cuartas\\+4.png"
    else:
        if self.numero in None:
            return f"las_cuartas\\{self.couleur}_joker.png"
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

  def members(self):
    return len(self.liste)
      
class Game:
  def __init__(self, nb_players, code):
    self.pioche = Pile()     #Pioche du jeu
    self.support = None      #Dernière carte sur la pile des cartes posées
    self.posees = Pile()     #Pile des cartes posées
    self.lobby = PlayerList()  #Liste des joueurs 
    self.sens = True         #Sens de départ
    self.code = code         #Code de la partie
    self.nb_players = nb_players   #Nombre de joueurs dans la partie
    self.ongoing = False     #Indique si la partie a commencé ou pas

  def startgame(self):
    print("#312 c'est parti pour la rigolade")
    self.ongoing = True      #Indique que la partie a commencé
    
    #On place le n° du prochain joueur dans self.joueurs[0]
    self.joueurs = list()
    self.joueurs.append(1)
    self.joueurs += self.lobby.liste
    
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
  
  def tour(self):
    """Gère le tour"""
    global played
    
    played, ok = False, False
    print("#350")	
		#Chaque joueur reçoit son jeu
		#A modifier plus tard pour le nb de cartes des autres joueurs et tout
    for joueur in self.joueurs[1:]:
        opponents = set()
        for opponent in self.joueurs[1:]:
            if not joueur.pseudo == opponent.pseudo:
                print("#357o zebi un  méchan")
                opponents.add(opponent.jeu.nb_cartes())
        Psend(connList[joueur.ip],(self.support, joueur.jeu, opponents))

    sendBroadcast(self, f"C'est le tour de {self.joueurs[self.joueurs[0]].pseudo}")
			
    player = self.joueurs[self.joueurs[0]]

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

  def apply_effects(self):
    """Check des effets eventuels de la carte posée qui devient support"""
    global _new_colour
    global connList
    
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

        sendBroadcast(self, f"{self.joueurs[decideur].pseudo} doit décider de la couleur de la carte.")

        player = self.joueurs[self.joueurs[0]]
        Psend(connList[player.ip],"Merci de choisir la couleur de la carte \n")
        
        _new_colour = None

        #Pour le cas où la carte est un joker
        while _new_colour is None:
            time.sleep(1)
        
        assert _new_colour in ["bleu","jaune","vert","rouge"]
          
        sendBroadcast(self, f"La nouvelle couleur est : {_new_coulour}.\n")
        self.support.change_couleur(_new_coulour)
          
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
        sendBroadcast(self, f"Félicitations, {self.joueurs[nb+1].pseudo} a gagné. \n")
        sendBroadcast(self, "La partie est Finie, vous pouvez quitter la Salle de Jeu")
        print(f"Félicitations, le joueur {self.joueurs[nb+1].pseudo} a gagné. \n")
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

  def isReady(self):
    if not self.ongoing:
        print("#494" + str(self.lobby.members()) + str(self.nb_players))
        return self.lobby.members() == self.nb_players
    return False

  def announcePlayers(self):
      sendBroadcast(self, f"{self.lobby.members()} joueurs sur {self.nb_players} pour le début de la partie" )

class GameList():
    def __init__(self):
        self.liste = list()
        
    def add(self, nb, code):
        self.liste.append(Game(nb, code))
        
    def remove(self, code):
        for game in self.liste:
            if game.code == code:
                self.liste.remove(game)
                
    def exists(self, code):
        for game in self.liste:
            if game.code == code:        
                    return True
        return False
    
    def rejoindre(self, player, code):
        for game in self.liste:
            if game.code == code:
                game.lobby.add(player)
                
    def __str__(self):
        var = ""
        for game in self.liste:
            var += f"{game.lobby.members()}/{game.nb_players} : {game.code}"
        return var

    def __getitem__(self, code):
        for game in self.liste:
            if game.code == code:  
                return game
    
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

def create_game(connection, ip, msg : tuple) -> None:
    global gamelist
    global players
    
    request, nb, code = msg

    if not gamelist.exists(code):
        
        gamelist.add(nb, code)
        time.sleep(0.5)
        gamelist.rejoindre(Player(ip, players[ip]), code)
        Psend(connection, "waiting")
        time.sleep(0.5)
        gamelist[code].announcePlayers()
                    
    else: Psend(connection, "CreateGame Error")

def joingame(connection, ip, msg : tuple) -> None:
    global gamelist
    global players
    
    request, code = msg
                
    if gamelist.exists(code):

        gamelist.rejoindre(Player(ip, players[ip]), code)
        Psend(connection, "waiting")
        time.sleep(0.5)
        gamelist[code].announcePlayers()
                    
    else: Psend(connection, "JoinGame Error")
    
    
    
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


gamelist = GameList()

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

def getip(c):
    """c = connection, renvoie l'ip"""
    global connList
    
    for k in connList.keys():
        if connList[k] == c: return k

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

def threaded(connection, ip):
    """THREAD DE LA GESTION DE CLIENTS"""
    global clientCount
    global runAll
    global players
    global played
    global _new_colour
    global gamelist
    
    #On attribue un pseudo pour chaque joueur
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
                break
                return False
            
            elif msg=="plList":
                Psend(connection,"Voici la liste des joueurs : ")
                Psend(connection,players)
            
            elif msg=="help":
                Psend(connection, "Liste des commandes :\nplList : Affiche la liste des joueurs connectés\nendconn : Ferme la connection\nhelp : Affiche cette liste")
                
            elif type(msg) is tuple and msg[0] == "creategame":                
                create_game(connection, ip, msg)
            
            elif type(msg) is tuple and msg[0] == "joingame":
                joingame(connection, ip, msg)
                
            elif type(msg) is str and type(eval(msg)) is int:
                
                if clbonjueur(connection): played = int(msg)
                
                else: Psend(connection, "c pas ton tour")
                
            elif msg in ["bleu", "vert", "rouge", "jaune"]:
                _new_colour = msg
            
            elif type(msg) is tuple and msg[0] in ["signin", "signup"]:
                signin_signup(connection, ip, msg)
                
            else:
                Psend(connection,f"Unkown command \"{msg}\" ")
                
        except:pass#Mettre une exception ici après
    connection.close()
    sys.exit()


#NB : Il est important de déclarer les variables en global afin d'avoir un droit
#de modification dessus et pas seulement de lecture
def handleJeu():
    global gamelist
    
    while True:
        for game in gamelist.liste:
            print(game.isReady())
            if game.isReady():
                sendBroadcast(game, "starting")
                time.sleep(0.5)
                game.startgame()
                
            time.sleep(1)#S'agirait de pas casser le serv
            
            #response=pickle.loads(connList[pnum].recv(4096))
            #print(response)
            
    sys.exit()            

def sendBroadcast(game, msg):
    global connList

    for player in game.lobby.liste:
        Psend(connList[player.ip],msg)
        
okb=True
def checkForReady():
    global clientCount
    global okb
    
    while okb:
        if clientCount>=2:
            sendBroadcast("Partie Prête à commencer")
            okb=False

_new_colour = None            
start_new_thread(handleJeu,())


#----Main Run Loop----
while runAll:
    #On accepte en permanence les demandes de connexion au serveur
    connection,ip = server.accept()
    connList[ip] = connection
    print(connection,ip)
    #Start un nouveau "threaded" pour chaque client
    start_new_thread(threaded ,(connection, ip))
    