# -*- coding: utf-8 -*-

######################
# Import des modules #
######################



import sys
import socket
import random
import time
import pickle
import sqlite3
from _thread import *
from cryptography.fernet import Fernet
import datetime



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



def getStats(pseudo) -> tuple:
    cur.execute("SELECT Wins FROM Joueurs WHERE Pseudo = ?",(pseudo,))
    nb_wins = cur.fetchall()[0][0]

    cur.execute("SELECT Parties FROM Joueurs WHERE Pseudo = ?",(pseudo,))
    nb_parties = cur.fetchall()[0][0]

    cur.execute("SELECT Elo FROM Joueurs WHERE Pseudo = ?",(pseudo,))
    elo = cur.fetchall()[0][0]
    
    return (nb_wins, nb_parties, elo, dateToCard())
    
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
                stats = getStats(ide)
                
                Psend(connection, ("online moment",) + stats)
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

def dateToCard():
    dateToday=datetime.datetime.today()
    dateToday=str(dateToday)[:10]
    year,month,day = int(dateToday[:4]) ,int(dateToday[5:7]),int(dateToday[8:10])
    
    k=0
    for j in list(str(year)):
        k+=int(j)
    
    for i in range(1,day):
        k=k*i
        
    if int(str(k)[:2])<=5:k=None
    elif int(str(k)[:2])<=10:k="+4"
    elif int(str(k)[:2])<=30:k="+2"
    elif int(str(k)[:2])<=40:k=0
    else:
        k=str(k)
        k=int(k[:1])
    
    color=''
    if month*day<30:
        color="rouge"
    elif month*day<60:
        color="bleu"
    elif month*day<90:
        color="vert"
    else:color="jaune"
    
    if k is None:return Carte(None,None,True)
    if k =="+4":return Carte("+4", None, True)
    if k=="+2":return Carte("+2",color,True)
    else:return Carte(k,color)



###################         On est obligés de les avoir ici
# Classes de mort #         pour que pickle fonctionne correctement
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
            return "Images\\las_cuartas\\joker.png"               
        else:
            return "Images\\las_cuartas\\+4.png"
    else:
        if self.numero in None:
            return f"Images\\las_cuartas\\{self.couleur}_joker.png"
        return f"Images\\las_cuartas\\{self.couleur}_{self.numero}.png"

class Jeu:
  #Classe d'un jeu de la main d'un joueur
  def __init__(self):
    self.main=[]
  
  def main_vide(self) -> None:
    #Génère la main vide d'un joueur
    self.main=[]
  
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
        
    def renverser(self):
    #Renverse la pile
        return self.valeurs.reverse()

class Player:
  def __init__(self, co, pseudo:str):
    self.nb = 0
    self.jeu = Jeu()
    self.pseudo = pseudo
    self.ip = co
    self.inGame = False
    
  def __str__(self):
    return str(self.pseudo) + ":" + str(self.ip[0])
  
  def addGame(self):
    #On récupère le nombre actuel de parties
    cur.execute("SELECT Parties FROM Joueurs WHERE Pseudo = ?", (self.pseudo,))
    nb_parties = cur.fetchall()[0][0]

    cur.execute("UPDATE Joueurs SET Parties = ? WHERE Pseudo = ?", (nb_parties+1, self.pseudo))
    base.commit()

  def updateElo(self, win = False):
    change = random.randint(5, 20)
    if not win: change = -change

    cur.execute("SELECT Elo FROM Joueurs WHERE Pseudo = ?", (self.pseudo,))
    elo = cur.fetchall()[0][0]

    cur.execute("UPDATE Joueurs SET Elo = ? WHERE Pseudo = ?", (elo+change, self.pseudo))
    base.commit()

  def addWin(self):
    cur.execute("SELECT Wins FROM Joueurs WHERE Pseudo = ?", (self.pseudo,))
    wins = cur.fetchall()[0][0]
    
    cur.execute("UPDATE Joueurs SET Wins = ? WHERE Pseudo = ?", (wins+1, self.pseudo))
    base.commit()   
    
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

  def getplayer(self, ip):
    for e in self.liste:
      if ip == e.ip:
        return e
    
class Game:
    """Représente une partie de Uno"""
    def __init__(self, nb_players, code):
        self.support = None             #Dernière carte sur la pile des cartes posées
        self.posees = Pile()            #Pile des cartes posées
        self.lobby = PlayerList()       #Liste des joueurs 
        self.sens = True                #Sens de départ
        self.code = code                #Code de la partie
        self.nb_players = nb_players    #Nombre de joueurs souhaités dans la partie
        self.ongoing = False            #Indique si la partie a commencé ou pas

    def startgame(self):
        """Démarre la partie"""
        self.ongoing = True      #Indique que la partie a commencé
    
        #On place le n° du prochain joueur dans self.joueurs[0]
        #self.joueurs est une liste python telle que :
        #            [0] est le numero du joueur dont c'est le tour
        #            le reste sont des objets de type Player()
        self.joueurs = list()
        self.joueurs.append(1)
        self.joueurs += self.lobby.liste
    
        #On modifie chaque joueur pour l'insérer dans la partie
        for k in range(1, len(self.joueurs)):
            self.joueurs[k].nb = k
            self.joueurs[k].addGame()
            self.joueurs[k].inGame = self.code

        #Génère la pioche contenant toutes les cartes du jeu
        self.pioche = creation_cartes()

        #Mélange la pioche bien comme il faut
        for _ in range(random.randint(1,5)):
            self.pioche.melanger()

        #Distribue 7 cartes à chacun des joueurs
        for a_distribuer in range(len(self.joueurs)-1):
            self.joueurs[a_distribuer +1].nb = a_distribuer +1
            self.joueurs[a_distribuer +1].jeu = Jeu()
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
    
        #Initialisation des variables
        played, ok = False, False
        
        #On s'assure que la pioche ne soit pas vide
        if self.pioche.pilevide():
            self.pioche = self.posees.renverser()
            self.posees=Pile()
        
		#Chaque joueur reçoit le support, son jeu et le nb de cartes des adversaires
        for joueur in self.joueurs[1:]:
            opponents = tuple()
            for opponent in self.joueurs[1:]:
                if not joueur.ip == opponent.ip:    
                    opponents = opponents + (opponent.jeu.nb_cartes(),)
                    
            Psend(connList[joueur.ip],(self.support, joueur.jeu, opponents))
        
        #Annonce de qui doit jouer
        sendBroadcast(self, f"C'est le tour de {self.joueurs[self.joueurs[0]].pseudo}")
        
        #On récupère le joueur dont c'est le tour
        player = self.joueurs[self.joueurs[0]]

        #On attend que le joueur aie choisit son action
        while played is False:
            time.sleep(1)

        #Tant que le joueur n'a pas choisit une option possible
        while not ok:
            
            #Carte par défaut, histoire d'éviter les erreurs
            card = Carte(10, "blaune")
            
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
        """Applique les effets eventuels de la carte posée qui devient support"""
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
    
                sendBroadcast(self, f"{self.joueurs[decideur].pseudo} doit décider de la couleur de la carte.")
                
                #On informe le joueur qu'il doit choisir la couleur de la carte
                player = self.joueurs[decideur]
                Psend(connList[player.ip],"cheeseColor")
            
                #Initialisation des variables
                _new_colour = None
                askingColor = True
            
                #Pour le cas où la carte est un joker
                while _new_colour is None:
                    time.sleep(1)
                    
                #On attend que le joueur aie choisit la couleur
                while askingColor:
                    
                    #Quand le joueur a finalement chosit sa couleur
                    if _new_colour is not None:
                        
                        #On envoie à chaque joueur, le nouveau support pour mettre à jour l'interface
                        for joueur in self.joueurs[1:]:
                            opponents = tuple()
                        
                            for opponent in self.joueurs[1:]:
                                if not joueur.ip == opponent.ip:
                                    opponents = opponents + (opponent.jeu.nb_cartes(),)
                                
                                Psend(connList[joueur.ip],(self.support, joueur.jeu, opponents))
                    
                    #On sort de la boucle    
                    askingColor = False       
              
                #Annonce à tous les joueurs de la nouvelle couleur
                sendBroadcast(self, f"La nouvelle couleur est : {_new_colour}.\n")
                
                #Mise à jour du support côté serveur
                self.support.change_couleur(_new_colour)
              
                #On réinitialise les variables
                _new_colour = None
            
                if not self.support.joker():
                    #Dans le cas où la carte est un +4, on fait piocher le joueur
                    for _ in range(4):
                        self.joueurs[self.joueurs[0]].jeu.piocher(self.pioche)
                    self.prochain_tour()

    def prochain_tour(self):
        """Pour passer au prochain tour de la partie"""
        if self.sens:
            #Si on joue dans le sens normal
            self.joueurs[0] = (self.joueurs[0] % (len(self.joueurs) -1)) +1

        else:
            #Si on est en sens inverse
            self.joueurs[0] -=1
            if self.joueurs[0] == 0:
                self.joueurs[0] = len(self.joueurs) -1

    def is_Winner(self):
        """Vérifie si quelqu'un a gagné, 
        si oui met à jour la base de donnéesenvoie l'annonce de victoire à chaque joueurs et renvoie True,
        sinon, laisse le jeu continuer son cours."""
        
        #S'il ne reste plus qu'un seul joueur, il gagne par forfait
        if len(self.joueurs) == 2:
            sendBroadcast(self, f"Victoire par forfait de {self.joueurs[1].pseudo}")
            sendBroadcast(self, ("andHisNameIs",{self.joueurs[1].pseudo}))
            
            #Mise à jour de la base de données
            self.joueurs[1].addWin()
            self.joueurs[1].updateELo(True)
            
            #Met fin à la partie
            self.kill()
            return True
    
        for nb in range(len(self.joueurs)-1):
            
            #Si un joueur n'a plus de cartes, il a gagné
            if self.joueurs[nb+1].jeu.est_vide():
                sendBroadcast(self, ("andHisNameIs",{self.joueurs[nb+1].pseudo}))
                sendBroadcast(self, "La partie est Finie, vous pouvez quitter la Salle de Jeu")
                print(f"Félicitations, le joueur {self.joueurs[nb+1].pseudo} a gagné. \n")
                
                #Mise à jour de la base de données
                self.joueurs[nb+1].addWin()
                self.joueurs[nb+1].updateElo(True)
                
                #On met aussi à jour l'elo des perdants
                for nb2 in range(len(self.joueurs)-1):
                    if nb2+1 != nb+1: self.joueurs[nb2+1].updateElo()
                    
                self.kill()
                return True

    def restart(self):
        """Vide les mains de deux joueurs puis lance une nouvelle partie"""
        #Inutile dans la version actuelle
        #Utile par le passé
        self.joueurs = []
        self.startgame()
    
    def poser_carte(self, card, player):
        """Pose la carte sur la pile, ce qui en fait le nouveau support
        Et la retire de la main du joueur
        
        card est un objet de la classe Card()
        player est un objet de la classe Player()"""
        if card.est_jouable(self.support):
            self.posees.empiler(card)
            self.support = card
            player.jeu.retirer(card)

    def isReady(self):
        """"Renvoie True si la partie est prête à démarrer, si elle contient le nombre de joueurs recherché
        False sinon"""
        
        #On s'interesse seulement aux parties qui  n'ont pas encore commencé
        if not self.ongoing:
            return self.lobby.members() == self.nb_players
        return False

    def announcePlayers(self):
        """Annonce le nombre de joueurs, pour avoir une idée de quand la partie va commencer"""
        sendBroadcast(self, f"{self.lobby.members()} joueurs sur {self.nb_players} pour le début de la partie" )
      
    def kill(self):
        """Met fin à la partie"""
        global gamelist
        
        for player in self.joueurs[1:]:
            player.inGame = False
            player.jeu.main_vide()
         
        #La sort de la liste des parties
        #La transforme en NoneType
        gamelist.remove(self.code)
        self = None

class GameList:
    """Liste de parties"""
    def __init__(self):
        self.liste = list()
        
    def add(self, nb, code):
        """Ajoute la partie de code:code à la liste"""
        self.liste.append(Game(nb, code))
        
    def remove(self, code):
        """Retire la partie de code:code de la liste"""
        for game in self.liste:
            if game.code == code:
                self.liste.remove(game)
                
    def exists(self, code):
        """Renvoie True si la partie de code:code existe, False sinon"""
        for game in self.liste:
            if game.code == code:        
                    return True
        return False
    
    def rejoindre(self, player, code):
        """player est un objet de type Player()
        fait rejoindre la partie de code:code à player"""
        global connList
        
        for game in self.liste:
            if game.code == code:
                #On ne peut pas rejoindre une partiequi a déjà commencé
                if game.ongoing:
                    Psend(connList[player.ip], "JoinGame Error")
                else:
                    game.lobby.add(player)
    
    def quitgame(self, player, code):
        """Fait quitter la partie à player"""
        self[code].lobby.remove(player.ip)
        self[code].joueurs.remove(player)
        
        #On baisse l'elo du joueur, il a déclaré forfait
        player.updateElo()
        
        #On vérifie si la situation devient une victoire par forfait
        self[code].is_Winner()
    
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



def creation_cartes():
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

def create_game(connection, player, msg : tuple) -> None:
    global gamelist
    
    request, nb, code = msg

    if not gamelist.exists(code):
        
        gamelist.add(nb, code)
        time.sleep(0.5)
        gamelist.rejoindre(player, code)
        Psend(connection, "waiting")
        time.sleep(0.5)
        gamelist[code].announcePlayers()
        player.onGame = code
        
    else: Psend(connection, "CreateGame Error")

def joingame(connection, player, msg : tuple) -> None:
    global gamelist
    
    request, code = msg
                
    if gamelist.exists(code):
        
        gamelist.rejoindre(player, code)
        Psend(connection, "waiting")
        time.sleep(0.5)
        gamelist[code].announcePlayers()
        player.onGame = code        
            
    else: Psend(connection, "JoinGame Error")
    
    
    
#################################
# Création/ouverture du serveur #
#################################



ip='192.168.0.33'
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

def askEnd() -> None:
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

def Psend(c,msg) -> None:
    """Fonction pour envoyer un message via pickle
    Arguments : c = connection
                msg = message qui sera pickle.dumps et c.send"""
    c.send(pickle.dumps(msg))

#   / ! \                                                    / ! \
#  /  !  \  NE SURTOUT PAS RENOMMER LA FONCTION CI DESSOUS  /  !  \
# /   !   \      CELA DÉTRUIRAIT L'ESPACE TEMPS MARTY!!    /   !   \

def clbonjueur(connection, player) -> bool:
    """Fonction qui renvoie True si la personne qui vient de jouer
    est bien la personne don c'est le tour"""
    global connList, gamelist
    
    cur_game = gamelist[player.onGame]
    lbonjueur = cur_game.joueurs[cur_game.joueurs[0]]
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
    global askingColor
    
    #On attribue un pseudo pour chaque joueur
    players.add(Player(ip,"Guest"+str(ip[1])))
    print(players)
    
    clientCount+=1
    
    print("Nouveau Client en cours de connexion")
    print(f"Connecté à : {ip}")
    
    Psend(connection,f"Vous êtes le : {clientCount}eme Joueur")
    Psend(connection,f"Votre pseudo est : {players[ip]}")
    
    print(f"\nLe nombre de clients est maintenant de {clientCount}")
    cur_player = players.getplayer(ip)
    while runAll:
        try:

            msg=pickle.loads(connection.recv(4096))
            print(f"Recu : {msg} de {players[ip]}")
            
            if msg=="endconn" or not msg:
                #Si le message reçu est "endconn" la connection s'arrette
                
                print(f'**Déconneté de : {ip}**\n')
                Psend(connection,"Fermeture de la connection")
                clientCount-=1
                if cur_player.inGame is not False:
                    gamelist.quitgame(cur_player, cur_player.inGame)
                players.remove(ip)
                print(f"Nombre de clients : {clientCount}\n")
                
                connection.close()
                break
                return False
            
            #Dans le cas d'une requête de la list des joueurs connectés
            elif msg=="plList":
                Psend(connection,"Voici la liste des joueurs : ")
                Psend(connection,players)
            
            #Pour avoir la liste des commandes
            elif msg=="help":
                Psend(connection, "Liste des commandes :\nplList : Affiche la liste des joueurs connectés\nendconn : Ferme la connection\nhelp : Affiche cette liste")
            
            #Si c'est une requête de retour à l'accueil
            elif msg=="BackMenu":
                Psend(connection, ("newStats",) + getStats(cur_player.pseudo))
            
            #Si c'est pour créer une partie
            elif type(msg) is tuple and msg[0] == "creategame":                
                create_game(connection, cur_player, msg)
                print("La partie a bel et bien étée crée")
            
            #Si c'est pour envoyer un message dans le chat
            elif type(msg) is tuple and msg[0] == "message":
                sendBroadcast(gamelist[cur_player.inGame], f"{cur_player.pseudo} : {msg}")
                
            #Si c'est pour rejoindre une partie
            elif type(msg) is tuple and msg[0] == "joingame":
                joingame(connection, cur_player, msg)
            
            #Si c'est pour jouer une carte
            elif (type(msg) is str and type(eval(msg)) is int) or type(msg) is int:
                
                #On s'assure que c'est le bon joueur qui veut jouer
                if clbonjueur(connection, cur_player): played = int(msg)
                
                else: Psend(connection, "Ce n'est pas votre tour !")
            
            #Si c'est pour changer la couleur dans le cas d'un joker ou d'un +4
            elif type(msg) is str and (eval(msg) == "rouge" or eval(msg)=="bleu" or eval(msg)=="vert" or eval(msg) =="jaune"):
                if askingColor:
                    print(f"{msg} est la nouvelle couleur")
                    msg = msg[1:-1]
                    _new_colour=msg
                    askingColor=False
            
            #Si c'est une requête de connection
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

            if game.isReady():
                sendBroadcast(game, "starting")
                time.sleep(0.5)
                start_new_thread(game.startgame,())

                
            time.sleep(1)#S'agirait de pas casser le serv
            
            #response=pickle.loads(connList[pnum].recv(4096))
            #print(response)
            
    sys.exit()            

def sendBroadcast(game, msg):
    global connList

    for player in game.lobby.liste:
        Psend(connList[player.ip],msg)



_new_colour = None            
start_new_thread(handleJeu,())
askingColor = False

#----Main Run Loop----
while runAll:
    #On accepte en permanence les demandes de connexion au serveur
    connection,ip = server.accept()
    connList[ip] = connection
    print(connection,ip)
    #Start un nouveau "threaded" pour chaque client
    start_new_thread(threaded ,(connection, ip))
    
