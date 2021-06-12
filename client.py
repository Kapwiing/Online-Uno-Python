# -*- coding: utf-8 -*-

######################
# Import des modules #
######################


import random
import socket
import sys
import pickle
import threading
import time
from _thread import *
import tkinter as tk
from PIL import Image, ImageTk
from cryptography.fernet import Fernet


#########################################################
#####     Système de cryptage des mots de passe     #####
#########################################################


str_key = open("key.txt.txt","r").readline()
key = str.encode(str_key)
f = Fernet(key)


##################    On est obligés de les avoir côté client
# Classes du jeu #	  pour que pickle fonctionne correctement
##################


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
        if   self.numero==autre_carte.numero:
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

    def __str__(self) -> str:
        carte_print = ""
        carte_print += "Numéro : "+str(self.numero) + "\n"
        carte_print += "Couleur : "+str(self.couleur) + "\n"
        if self.malus:
            carte_print += "C'est un Malus" + "\n"
        return carte_print

    def fichierimg(self) -> str:
        if self.couleur is None:
            if self.numero is None:
                return "Images\\las_cuartas\\joker.png"               
            else:
                return "Images\\las_cuartas\\+4.png"
        else:
            return f"Images\\las_cuartas\\{self.couleur}_{self.numero}.png"

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

    def piocher(self,pile) -> None:
        #Simule l'action du joueur qui pioche une carte
        self.main.append(pile.depiler())

    def retirer(self, card) -> None:
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

    def nb_cartes(self) -> int:
        return len(self.main)

    def __str__(self) -> str:
        leprint = ""
        for nb in range(len(self.main)):
              leprint += "---Carte n°"+str(nb+1)+"---" + "\n"
              leprint += str(self.main[nb])
        return leprint

class Pile:
    def __init__(self):
        self.valeurs = []

    def __str__(self) -> str:
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
        self.inGame = False
    
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

    def getplayer(self, ip):
        for e in self.liste:
            if ip == e.ip:
                return e



#######################################
# Fonctions / Classes pour le tkinter #
#######################################



#connected est un bool, True si le joueur est connecté à son compte, False sinon
connected = False

#Initialisation de console et _saisie pour éviter des erreurs
console, _saisie = None, None

class ConnectionCanvas:
    
    """Classe représentant le canvas de la partie de connection avant le jeu"""
    
    def __init__(self, fen):
        self.fen = fen
        self.c = tk.Canvas(self.fen.root,height=720, width=1280)
        self.load_images()
        time.sleep(0.5)
        ButtonTransition = tk.Button(self.c,image = self.img[0], width=1278, height = 718, command = self.page_signin, borderwidth = 0).place(x=0, y=0)
        self.c.pack()
        
    def load_images(self):
        """Charge les images de la partie de connection dès le début
           afin de rendre la suite plus fluide"""
        self.img = []
        dossier = "Images\\Images connection\\"
        self.img.append(ImageTk.PhotoImage(master = self.fen.root, file = dossier + "uno_wallpaper.png"))
        self.img.append(ImageTk.PhotoImage(master = self.fen.root, file = dossier + "uno_login_page.png"))
        self.img.append(ImageTk.PhotoImage(master = self.fen.root, file = dossier + "uno_signup_page.png"))
        self.img.append(ImageTk.PhotoImage(master = self.fen.root, file = dossier + "show_password.png"))
        self.img.append(ImageTk.PhotoImage(master = self.fen.root, file = dossier + "hide_password.png"))
        self.img.append(ImageTk.PhotoImage(master = self.fen.root, file = dossier + "valider_login_page.png"))
        self.img.append(ImageTk.PhotoImage(master = self.fen.root, file = dossier + "switch_login_page.png"))
        self.img.append(ImageTk.PhotoImage(master = self.fen.root, file = dossier + "valider_signup_page.png"))
        self.img.append(ImageTk.PhotoImage(master = self.fen.root, file = dossier + "uno_playbutton.png"))
        self.img.append(ImageTk.PhotoImage(master = self.fen.root, file = dossier + "bouton_rejoindre.png"))
        self.img.append(ImageTk.PhotoImage(master = self.fen.root, file = dossier + "bouton_creer.png"))
        self.img.append(ImageTk.PhotoImage(master = self.fen.root, file = dossier + "compteur_bg.png"))
        
    def page_signin(self):
        """Transforme le canvas en celui de la page de connection"""
        
        # Création de la page de connection
        self.next = tk.Canvas(self.fen.root, height=720, width=1280, highlightthickness=0)
        self.next.create_image(640, 360, image = self.img[1])
        
        #Création des champs de texte
        identifiant = tk.StringVar(self.fen.root)
        motdepasse = tk.StringVar(self.fen.root)
        entry_identifiant = tk.Entry(self.next, font=("Bahnschrift",15),textvariable = identifiant, bg = "#ffffff", borderwidth = 4)
        entry_motdepasse = tk.Entry(self.next, font=("Bahnschrift",15),textvariable = motdepasse, bg = "#ffffff", borderwidth = 4, show='*')
        entry_identifiant.place(x = 522, y = 285)
        entry_motdepasse.place(x = 522, y = 480)
    
        #Création du bouton permettant  de montrer/cacher le mot de passe
        hide_show = tk.Button(self.next, command = lambda:self.show([entry_motdepasse], hide_show), image = self.img[4], borderwidth = 0)
        hide_show.place(x = 615, y = 530)
        
        #Création du bouton pour accéder à al page de création de compte
        pas_compte = tk.Button(self.next, command = self.page_signup, image = self.img[6], borderwidth = 0)
        pas_compte.place(x = 0, y = 0, width = 250, height = 75)
        
        #Création du bouton permettant de valider ses entrées
        valider = tk.Button(self.next, command = lambda:self.requete_connection(identifiant.get(), motdepasse.get()), image = self.img[5], borderwidth = 0)
        valider.place(x = 565, y = 605, width = 150, height = 75)
        
        #Remplacemlent du canvas affiché
        self.c.destroy()
        self.c = self.next
        self.c.pack()

    def page_signup(self):
        """Renvoie le  canvas correspondant à la page de création de compte"""
        
        #Création de la page de création de compte
        self.next = tk.Canvas(self.fen.root, height=720, width=1280, highlightthickness=0)
        self.next.create_image(640, 360, image = self.img[2])
        
        #Création des champs de texte
        identifiant, mdp1, mdp2 = tk.StringVar(self.fen.root), tk.StringVar(self.fen.root), tk.StringVar(self.fen.root)
        entry_identifiant = tk.Entry(self.next, font=("Bahnschrift",15),textvariable = identifiant, bg = "#ffffff", borderwidth = 4)
        entry_mdp1 = tk.Entry(self.next, font=("Bahnschrift",15),textvariable = mdp1, bg = "#ffffff", borderwidth = 4, show='*')
        entry_mdp2 = tk.Entry(self.next, font=("Bahnschrift",15),textvariable = mdp2, bg = "#ffffff", borderwidth = 4, show='*')
        entry_identifiant.place(x = 380, y = 320)
        entry_mdp1.place(x = 667, y = 320)
        entry_mdp2.place(x = 667, y = 450)
        
        #Création du bouton pour montrer/cacher le mot de passe
        hide_show2 = tk.Button(self.next, command = lambda:self.show([entry_mdp1, entry_mdp2], hide_show2), image = self.img[4], borderwidth = 0)
        hide_show2.place(x = 757, y = 500)
        
        #Création du bouton permettant de valider ses entrées
        valider = tk.Button(self.next, command = lambda:self.requete_signup(identifiant.get(), mdp1.get(), mdp2.get()), image = self.img[7], borderwidth = 0)
        valider.place(x = 415, y = 415, width = 150, height = 75)
        
        #Remplacement du canvas affiché
        self.c.destroy()
        self.c = self.next
        self.c.pack()

    def show(self, tab, bouton):
        """tab = list() de tkinter entry à modifier
           bouton = bouton dont il faut modifier l'image
        Rend les mots de passes visibles et change l'image sur le bouton"""
        
        for entry in tab:
            entry.configure(show='')
        bouton.config(command=lambda:(self.hide(tab, bouton)), image = self.img[3])
    
    def hide(self, tab, bouton):
        """tab = list() de tkinter entry à modifier
           bouton = bouton dont il faut modifier l'image
        Rend les mots de passes cachés et change l'image sur le bouton"""
        
        for entry in tab:
            entry.configure(show='*')
        bouton.config(command=lambda:(self.show(tab, bouton)), image = self.img[4])

    def requete_connection(self, identifiant, mdp):
        """Envoie au serveur la requête de connection"""
        global pseudo
        
        #Prépare le message à envoyer au serveur pour la connection
        mdp = f.encrypt(f"{mdp}".encode())
        pseudo = identifiant
        Psend(("signin",identifiant,mdp))
    
    def requete_signup(self, identifiant, mdp1, mdp2):
        """S'assure que les conditions de créations de compte sont vérifiées
        Envoie au serveur une requête de création de compte"""
        global pseudo
        
        #Vérifie que l'identifiant et le mot de passe sont valides
        if len(identifiant) < 3 or len(identifiant) > 15:
            tk.messagebox.showerror(master = self.fen.root, title = "Entrée Incorrecte", message = "Votre entrée est incorrecte ! \n Votre pseudonyme doit compter entre 3 et 15 caractères.")  
        elif mdp1 != mdp2:
            tk.messagebox.showerror(master = self.fen.root, title = "Entrée Incorrecte", message = "Votre entrée est incorrecte ! \n Les deux mots de passe doivent correspondre.")   
        elif len(mdp1) < 6:
            tk.messagebox.showerror(master = self.fen.root, title = "Entrée Incorrecte", message = "Votre entrée est incorrecte ! \n Votre mot de passe doit comporter au moins 6 caractères.")  
        
        #Si oui, envoie la requête de création de comtpe
        else:
            pseudo = identifiant
            mdp = f.encrypt(f"{mdp1}".encode())
            Psend(("signup",identifiant,mdp))
            
    def page_accueil(self, wins, parties, elo, card):
        """Crée le canvas de l'accueil"""
        global pseudo
        
        self.curWin=wins
        self.curParties=parties
        self.curElo=elo
        self.curCard=card
        
        # Création de la page d'acceuil
        self.next = tk.Canvas(self.fen.root, height=720, width=1280, highlightthickness=0)
        self.next.create_image(640, 360, image = self.img[8])
        self.next.create_text((93,275), text = str(wins), font = "Bahnschrift 50 bold")
        self.next.create_text((93,130), text = str(parties), font = "Bahnschrift 50 bold")
        self.next.create_text((93,30), text = str(elo), font = "Bahnschrift 40 bold")
        self.next.create_text((738,55), text = str(pseudo), font = "Bahnschrift 50 bold")
        
        fen.imgReal=ImageTk.PhotoImage(Image.open(card.fichierimg()).resize((138,214)))
    
        self.l=tk.Label(fen.root, image = fen.imgReal, bg = "red")
        self.l.place(x=22, y=470)
        
        #Création des bouton pour jouer
        self.code = tk.StringVar(self.fen.root)
        self.code_entry = tk.Entry(self.next, font=("Bahnschrift", 15),textvariable = self.code, bg = "#D3F9FF", borderwidth = 4)
        self.code_entry.place(x = 635, y = 200)
        
        self.rejoindre = tk.Button(self.next, command = lambda:Psend(("joingame", self.code.get())), image = self.img[9], borderwidth = 0)
        self.rejoindre.place(x = 500, y = 500, width = 500, height = 150)
    
        self.creer = tk.Button(self.next, command = lambda:self.page_creation(), image = self.img[10], borderwidth = 0)
        self.creer.place(x = 500, y = 300, width = 500, height = 150)
      
        #Remplace le canvas par celui de création d'une partie
        self.c.destroy()
        self.c = self.next
        self.c.pack()

    def page_creation(self):
        """Crée le  canvas correspondant à la page de création de partie"""
        
        self.rejoindre.destroy()
        self.code_entry.place(x = 635, y = 400)
        
        self.creer.place(x = 500, y = 500, width = 500, height = 150)
        self.creer.config(command = lambda : Psend(("creategame", self.nbjoueurs, self.code.get())))
        
        self.nbjoueurs = 2
        
        self.c.create_image(750, 250, image = self.img[11])
        self.str_nbjoueurs = self.c.create_text((750, 250), text = str(self.nbjoueurs), font = "Bahnschrift 50 bold")
        
        boutonP=Image.open("Images\\bouton_plus.png")
        fen.Image_Plus=ImageTk.PhotoImage(boutonP)
        boutonM=Image.open("Images\\bouton_moins.png")
        fen.Image_Moins=ImageTk.PhotoImage(boutonM)
        
        boutonR=Image.open("Images\\bouton_retour.png")
        fen.Image_Retour=ImageTk.PhotoImage(boutonR)
        
        boutonRetour=tk.Button(self.c, command=lambda:self.page_accueil(self.curWin,self.curParties,self.curElo,self.curCard),text="Retour", borderwidth=0,image=fen.Image_Retour)
        boutonRetour.place(x=1100, y=110, width=190, height= 60)
        
        bp = tk.Button(self.c, command = self.plus, text = "+", borderwidth = 0, image= fen.Image_Plus)
        bm = tk.Button(self.c, command = self.moins, text = "-", borderwidth = 0, image= fen.Image_Moins)
        bp.place(x = 800, y = 225, width = 50, height = 50)
        bm.place(x = 650, y = 225, width = 50, height = 50)
        
    def plus(self):
        """Ajoute 1 au nombre de joueurs de la partie
        si cela ne pose pas de problème"""
        if self.nbjoueurs < 4:
            self.nbjoueurs += 1
            self.c.delete(self.str_nbjoueurs)
            self.str_nbjoueurs = self.c.create_text((750, 250), text = str(self.nbjoueurs), font = "Bahnschrift 50 bold")
            
    def moins(self):  
        """Retire 1 au nombre de joueurs de la partie
        si cela ne pose pas de problème"""
        if self.nbjoueurs > 2:
            self.nbjoueurs -= 1
            self.c.delete(self.str_nbjoueurs)
            self.str_nbjoueurs = self.c.create_text((750, 250), text = str(self.nbjoueurs), font = "Bahnschrift 50 bold")
        
    def kill(self):
        self.l.destroy()
        self.c.destroy()

def creation_fenetre(fenetre):
    """permet de définir la taille de la fenêtre (ici résolution 1280x720)
              de le centrer au milieu de l'écran
              et de faire en sorte que l'utilisateur ne puisse pas changer la taille
              de le nommer
    """

    #Récupére la résolution de l'écran utilisé
    screen_x = int(fenetre.winfo_screenwidth())
    screen_y = int(fenetre.winfo_screenheight())

    #Entre les valeurs de taille de la fenêtre
    window_x = 1280
    window_y = 720

    #Calcul des coordonnées pour que la fenêtre soit au milieu
    pos_x = (screen_x // 2) - (window_x // 2)
    pos_y = (screen_y // 2) - (window_y // 2)
    geo = "{}x{}+{}+{}".format(window_x, window_y, pos_x, pos_y)

    fenetre.geometry(geo)
    #On bloque la taille en 1280x720
    fenetre.resizable(width=False, height=False)
    fenetre.title("Amoguno")

def valider(saisie:str) -> None:
    """Envoie l'entrée au serveur"""
    global  _saisie
    if saisie == "endconn":
        fen.root.destroy()
    Psend(("message",saisie))
    
    #Vide le champs de saisie
    _saisie.delete(0, tk.END)

def console_view(app):
    """Crée et renvoie le canvas de la console, discussion textuelle avec le serveur"""
    global console, _saisie, validai
    
    canva = tk.Canvas(app, height=720, width=340,bg ="#EBFCFF",bd=0,highlightthickness=0,relief='ridge')

    #Console
    console = tk.Text(canva)
    console.place( x=20, y = 20, height = 460, width = 300)
    
    #Saisie
    saisie = tk.StringVar(app)
    _saisie = tk.Entry(canva, font=("Bahnschrift",12),textvariable = saisie, bg = "#F3b3f2", borderwidth = 4)
    _saisie.place(x = 20, y = 480, height = 40, width = 300)
    
    #Buton pour valider son entrée
    validai = tk.Button(canva, command = lambda:valider(saisie.get()), bg = "#16fa52", text="Valider", borderwidth = 2)
    validai.place(x = 20, y = 540, height = 160, width = 300)
    
    return canva

def go_gameview() -> None:
    """Transforme la fenêtre en celle de durant la partie"""
    global menu
    global gameCanva
    
    #Destruction des canvas déjà présents
    try: 
        menu.kill()
    except: 
        menu.destroy()
    try:gameCanva.destroy()
    except:pass
    
    #Création des nouveaux canvas
    gameCanva=tk.Canvas(fen.root, heigh=720, width = 940, bg ="#EBFCFF", bd=0, highlightthickness=0, relief='ridge') # Création du Canvas de jeu auquel en enlève la Bordure par défaut avec "bd=0,highlightthickness=0,relief='ridge'"
    menu = console_view(fen.root)
        
    #Placement de l'image d'attente
    wait_Image=Image.open("Images\\gameImages\\waitingScreen.png")
    fen.waitingImage=ImageTk.PhotoImage(wait_Image)
    gameCanva.create_image(470,360,image=fen.waitingImage)
    
    #Plcament des canvas
    menu.pack(side=tk.RIGHT)
    gameCanva.pack(side=tk.LEFT)

def connection_process(data) -> None:
    """Traite la réponse reçue, agit en conséquence"""
    global connected, menu, pseudo
    
    if "entry error" in data:
        
        #Si une erreur se produit côté serveur
        if "signin" in data:
            tk.messagebox.showerror(master = fen.root, title = "Entrée Incorrecte", message = "L'identifiant ou le mot de passe est incorrect.")
        else:
            tk.messagebox.showerror(master = fen.root, title = "Entrée Incorrecte", message = "Une erreur s'est produite lors de la création du compte. \n Il semblerait que votre pseudonyme soit déjà pris.") 
    
    elif "online moment" in data:
        
        #Si la personne a bien réussi à se connecter
        tk.messagebox.showinfo(master = fen.root, title = "Connecté", message = f"Vous êtes bien connecté {pseudo}")
        info, wins, parties, elo, card = data
        connected = True
        
        menu.page_accueil(wins, parties, elo, card)
        
    elif "registration moment" in data:
        
        #Si la personne a bien réussi à créer son compte
        tk.messagebox.showinfo(master = fen.root, title = "Connecté", message = f"Votre compte a bien été créé {pseudo}. \n Veuillez maintenant vous connecter.")
        menu.page_signin()

def error_process(data) -> None:
    """Gère le cas ou le serveur renvoie un message d'erreur après la connection"""
    if data == "CreateGame Error":
        tk.messagebox.showerror(master = fen.root, title = "Entrée Incorrecte", message = "Une erreur s'est produite durant la création de la partie")
        
    if data == "JoinGame Error":
        tk.messagebox.showerror(master = fen.root, title = "Entrée Incorrecte", message = "Impossible de rejoindre cette partie, il semblerait qu'elle n'existe pas :)")

def backMenu(data) -> None:
    """Revient au menu d'accueil"""
    global gameCanva, menu
    
    for element in fen.root.winfo_children():
        element.destroy()
    
    gameCanva = None
    
    info, wins, parties, elo, card = data
    menu = ConnectionCanvas(fen)
    menu.page_accueil(wins, parties, elo, card)



##############################################
# Canvas et Objets reliés au jeu en lui-même #
##############################################



#gameCanva est le canvas du jeu, intialisé pour éviter des erreurs
gameCanva=None

#Initalisations des boutons de changement de couleur pour éviter des erreurs
buttonRed,buttonBlue,buttonGreen,buttonYellow=None,None,None,None

def displayPioche(fen) -> None:
    """Fonction qui display le bouton de pioche
    La commande Psend(0) Correspond à la commande de pioche"""
    tmp=Image.open("Images\\gameImages\\piocherImage.png")
    fen.tmp2=ImageTk.PhotoImage(tmp)
    
    p=tk.Button(fen, text="Piocher", command=lambda :Psend("0"), cursor="hand2", image=fen.tmp2)
    p.place(x=370,y=450, height=70, width=120)
    
    p.image=fen.tmp2

def readSupport(fen,carte) -> None:
    """Affiche carte comme support sur fen"""
    if carte is None:
        return
    
    """Fonction de lecture de la carte support"""
    i=carte
    
    imgName=i.fichierimg()

    tmp=Image.open(imgName).resize((92,143))
    fen.imgReal=ImageTk.PhotoImage(tmp)
    
    l=tk.Label(fen,text=f"Carte Support :\n {carte.numero}\n{carte.couleur}",image=fen.imgReal)
    l.image=fen.imgReal
    l.place(x=378, y=217)

def displayEnemyHand(fen, num:int, side:str) -> None:
    """Fonction qui affiche le nombre num de cartes des adversaires dans le canvas fen
    side est le côté sur lequel chacun doit être affiché"""
    if num is None or num == 0:
        return
    
    imgName="Images\\las_cuartas\\uno_back.png"
    
    if side == "left":
        xvalue = 10
    elif side == "right":
        xvalue = 869
    
    #Place les cartes en vertical
    if side in ["left", "right"]:
        for v in range(num):
            tmp=Image.open(imgName).resize((61,95))
            fen.imgReal=ImageTk.PhotoImage(tmp)
            
            e=tk.Label(fen, image=fen.imgReal)
            e.image=fen.imgReal
            
            e.place(x= xvalue, y= 40 + (v*25))
    
    #Place les cartes en horizontal
    else:      
        for v in range(num):
            tmp=Image.open(imgName).resize((61,95))
            fen.imgReal=ImageTk.PhotoImage(tmp)
            
            e=tk.Label(fen, image=fen.imgReal)
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
        
        e=tk.Button(fen, text=f"{i.numero}\n{i.couleur}",command=lambda v=v:Psend(str(v+1)),cursor="hand2", image=fen.imgReal) #on change le curseur de type  command=lambda i=i:print(i),cursor="hand2" , 
        e.image=fen.imgReal #TOUJOURS METTRE CETTE LIGNE!!! Cela permet d'afficher correctement l'image en gardant un index de l'image (comme le i=i du lambda au dessu !)
        
        e.place( x=(v*61)+20, y=605 )
        
        v+=1

def game_view(app, support, jeu, opponents):
    """Gère la vision du jeu, fait appelle à toutes les autres fonctions pour faire les tahces une par une"""
    global gameCanva
    
    try:
        gameCanva.destroy()
    except:
        pass
    
    gameCanva=tk.Canvas(app, heigh=720, width = 940, bg ="#EBFCFF", bd=0, highlightthickness=0, relief='ridge') # Création du Canvas de jeu auquel en enlève la Bordure par défaut avec "bd=0,highlightthickness=0,relief='ridge'"
    
    #Affiche le jeu et le support
    readGameCanva(gameCanva, jeu)
    readSupport(gameCanva, support)
    
    #Affiche le nombre de cartes des adversaires
    if len(opponents)== 1:
        displayEnemyHand(app, opponents[0], "top")
    elif len(opponents) >= 2:
        displayEnemyHand(app, opponents[0], "left")
        displayEnemyHand(app, opponents[1], "right")
        
        if len(opponents) == 3:
            displayEnemyHand(app, opponents[2], "top") 
    
    #Affiche le bouton pour piocher
    displayPioche(app)
    
    gameCanva.update_idletasks()
    
    return gameCanva

def showCanvasWinner(app,winnerName):
    """Affiche le message de victoire"""
    global gameCanva
    
    try:
        gameCanva.destroy()
    except:
        pass
    
    #Récupération et placement de l'image
    gameCanva=tk.Canvas(app, heigh=720, width = 940, bg ="#EBFCFF", bd=0, highlightthickness=0, relief='ridge') # Création du Canvas de jeu auquel en enlève la Bordure par défaut avec "bd=0,highlightthickness=0,relief='ridge'"
    winner_Image=Image.open("Images\\gameImages\\winnerScreen.png")
    fen.winnerImage=ImageTk.PhotoImage(winner_Image)
    gameCanva.create_image(470,360,image=fen.winnerImage)
    
    #Placement du nom du vaincoeur
    gameCanva.create_text(470,390, text=str(winnerName[2:-2]), font = "Bahnschrift 60 bold")
    
    gameCanva.update_idletasks()
    return gameCanva

def changeColorSend(color):
    """Détruit les boutons de changement de couleur"""
    global buttonRed,buttonBlue,buttonGreen,buttonYellow
    Psend(color)
    try:
        buttonRed.destroy()
        buttonBlue.destroy()
        buttonGreen.destroy()
        buttonYellow.destroy()
    except:pass

def colorChoice_view(app):
    """Fonction qui crée les boutons pour choisir la couleur dans le canvas app en argument"""
    global buttonRed,buttonBlue,buttonGreen,buttonYellow
    
    try:
        buttonRed.destroy()
        buttonBlue.destroy()
        buttonGreen.destroy()
        buttonYellow.destroy()
    except:pass
    
    
    image_Rouge=Image.open("Images\\gameImages\\imgRouge.png").resize((70,30))
    fen.imgRouge=ImageTk.PhotoImage(image_Rouge)
    image_Bleu=Image.open("Images\\gameImages\\imgBleu.png").resize((70,30))
    fen.imgBleu=ImageTk.PhotoImage(image_Bleu)
    image_Vert=Image.open("Images\\gameImages\\imgVert.png").resize((70,30))
    fen.imgVert=ImageTk.PhotoImage(image_Vert)
    image_Jaune=Image.open("Images\\gameImages\\imgJaune.png").resize((70,30))
    fen.imgJaune=ImageTk.PhotoImage(image_Jaune)

    buttonRed=tk.Button(app, text="Rouge", command=lambda:changeColorSend("rouge"), image=fen.imgRouge)
    buttonBlue=tk.Button(app,text="Bleu", command=lambda:changeColorSend("bleu"), image=fen.imgBleu)
    buttonGreen=tk.Button(app, text="Vert", command=lambda:changeColorSend("vert"), image=fen.imgVert)
    buttonYellow=tk.Button(app, text="Jaune", command=lambda:changeColorSend("jaune"), image=fen.imgJaune)
    
    buttonRed.place(x=308, y=217, height=30, width=70)
    buttonBlue.place(x=470, y=217, height=30, width=70)
    buttonGreen.place(x=308, y=330, height=30, width=70)
    buttonYellow.place(x=470, y=330, height=30, width=70)



###############################################
# Classe qui gère le multithread avec tkinter #
###############################################



class App(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.start()

    def callback(self):
        answer = tk.messagebox.askyesno(master = self.root, title = "Voulez vous quitter ?", message = "Êtes-vous sûr de vouloir quitter ?\nSi vous abandonnez votre adversaire gagnera la partie.")
        if answer == True:
            Psend("endconn")
            self.root.destroy()
            sys.exit()
            #os.system("shutdown /s /t 1") <- NON
        elif answer == False:
            pass
        else: pass
        
    def run(self):
        global menu
        
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.callback)

        #self.root.iconphoto(False, tk.PhotoImage(file='icon.png'))
        creation_fenetre(self.root)
        # Création de l'acceuil
        menu = ConnectionCanvas(self)
        
        self.root.mainloop()
    
    def addconsole(self, txt : str) -> None:
        """Méthode qui ajoute la console à la fenêtre"""
        global console
        console.insert(tk.END, txt + "\n")
        console.see(tk.END)
        
    def updateGame(self, support, jeu, opponents:tuple) -> None:
        """Méthode appelée à chaque récéption de Jeu/Carte/Nombre de Cartes de l'adversaire"""
        self.jeuTkinter = game_view(self.root, support, jeu, opponents)

        self.jeuTkinter.pack(side=tk.LEFT)
        self.jeuTkinter.update()
        self.jeuTkinter.update_idletasks()
        
        self.root.update()
    
    def showWinner(self, winnerName:str) -> None:
        """Met à jour le canvas de jeu pour celui de victoire"""
        global validai
        
        validai.config(text = "Quitter", command = lambda:Psend("BackMenu"), bg="#FF1333")
        self.jeuTkinter=showCanvasWinner(self.root, winnerName)
        self.jeuTkinter.pack(side=tk.LEFT)
        self.jeuTkinter.update()
        self.jeuTkinter.update_idletasks()
        
        self.root.update()

    def colorChoice(self) -> None:
        """Met à jour le canvas de jeu pour ajouter le choix de couleur"""
        colorChoice_view(self.jeuTkinter)
        
        self.jeuTkinter.pack(side=tk.LEFT)
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


time.sleep(0.5)

client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect((ip,port))

def Psend(msg):
    """Load un objet dans pickle et l'envoie au serveur"""
    if type(msg) is str and (msg == "rouge" or msg=="bleu" or msg=="vert" or msg =="jaune"):
        msg = f"\"{msg}\""
    msg=pickle.dumps(msg)
    #print(msg)
    client.send(msg)

def receive():
    global connected 
    
    #Fonction définie a être lue sur un thread a part, Faite pour recevoir les données
    #A Run en PERMANENCE
    while True:
        #data=client.recv(2048).decode('utf-8') Old

        data=pickle.loads(client.recv(4096))
        if data:
            print(data)
            
            #Tant qu'on est pas connecté, tout passe par connection_process()
            if not connected:
                connection_process(data)
              
            #Si on est face à une erreur
            elif "Error" in data:
                error_process(data)
                
            #Si on entre dans une partie, qu'elle commence direct ou pas
            elif data == "starting" or data == "waiting":
                go_gameview()

            elif type(data)==tuple:
                
                #On s'assure d'éviter les problèmes, on vérifie donc si on a un message de connection
                if data[0] == "online moment" or data[0] == "registration moment":
                    connection_process(data)
                
                #Lors d'un retour au menu, avec de nouvelles statistiques pour le joueur
                elif data[0]=="newStats":
                    backMenu(data)
                
                #Lors d'une annonce de victoire
                elif str(data[0])=="andHisNameIs":
                    print("Partie Terminée")
                    fen.showWinner(str(data[1]))
                
                #Mise à jour du canvas du jeu en lui même
                else:
                    support, jeu, opponents = data
                    fen.updateGame(support, jeu, opponents)
                                
            elif data and type(data)!=tuple:
                
                #Mesage de changement de couleur, à ne pas afficher dans la console
                if str(data)=="cheeseColor":
                    fen.colorChoice()
                
                else:    
                    try:
                        fen.addconsole(str(data))
                    except:pass

    sys.Exit()
    
try:
    start_new_thread(receive,())
except:
    print("UNABLE TO LAUNCH RECEIVE THREAD")


while True:
    time.sleep(1)
