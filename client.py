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
from cryptography.fernet import Fernet
from PIL import Image, ImageTk



#########################################################
#####     Système de cryptage des mots de passe     #####
#########################################################



key = b'eMaBW7X0joEX54iVNzqNmJXyV_vc67oIaGBB1DGkLdE='
f = Fernet(key)



###################     On est obligés de les avoir côté client
# Classes de mort #		pour que pickle fonctionne correctement
###################



class Carte:
  #La Classe Carte est la classe qui gère toutes les Cartes avec leurs attributs
  # ----------------------
  # |Numéro|Couleur|Malus|
  # ----------------------
  def __init__(self,num,couleur,malus=False):
      """num est le numéro de la carte, ou son effet
         couleur est la couleur de la carte [bleu,rouge,jaune,vert] ou None pour les jokers et +4
         Malus est un bool, si malus est True, la carte a un effet"""
      self.numero=num
      self.couleur=couleur
      self.malus=malus
    
  def change_couleur(self,nouv_couleur : str) -> None:
      """nouv_couleur est  la nouvelle couleur de la carte
         Change la couleur de la carte pour nouv_couleur"""
      #Uniquement pour les +4 et les changement de couleur
      self.couleur=nouv_couleur
    
  def est_jouable(self,autre_carte) -> bool:
      """On regarde si la carte est jouable sur une autre carte
         autre_carte est une Carte"""
      if self.numero==autre_carte.numero:
          return True
      elif self.couleur==autre_carte.couleur:
          return True
      elif self.couleur is None or self.numero is None:
          return True
        
      return False
    
  def joker(self) -> bool:
      """Renvoie True si la carte est un joker
         False sinon"""
      if self.numero is None and self.malus ==True:
          return True
      return False
    
  def passer_tour(self) -> bool:
      """Renvoie True si la carte est un "passer tour"
          False sinon"""
      if self.malus and self.numero=="passer":
          return True
      return False
    
  def changement_sens(self) -> bool:
      """Renvoie True si la cartes est un changement de sens
	     False sinon"""
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
          else:
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
    """Classe Pile vue en cours"""
    def __init__(self):
        self.valeurs = []

    def __str__(self) -> str:
        """Print une version visible de la Pile"""
        return str(self.valeurs)

    def empiler(self, valeur : Carte) -> None:
        """Empile valeur dans la pile"""
        self.valeurs.append(valeur)

    def depiler(self):
        """Si la pile n'est pas vide,
        Retire l'élément au sommet de la pile et le renvoie"""
        if not self.pilevide():
            return self.valeurs.pop()

    def pilevide(self) -> bool:
        """Renvoie True si la pile est vide, False sinon"""
        return self.valeurs == []

    def nb_elements(self) -> int:
        """Renvoie le nombre d'éléments de la pile"""
        return len(self.valeurs)

    def sommet(self):
        """Renvoie l'élément au sommet de la pile"""
        if self.pilevide(): 
            return Carte(None, None, True)
        return self.valeurs[-1]

    def melanger(self) -> None:
        """Mélange la pile"""
        random.shuffle(self.valeurs)

class Player:
    """Classe représentant un joueur"""
    def __init__(self, co, pseudo:str):
        self.nb = 0
        self.jeu = Jeu()
        self.pseudo = pseudo
        self.ip = co
    
    def __str__(self):
        return str(self.pseudo) + ":" + str(self.ip[0])
   
class PlayerList:
    """Classe représentant une liste de joueurs"""
    def __init__(self):
        self.liste = list()
    
    def __getitem__(self, ip):
        """Méthode permettant de récupérer le pseudo d'un joueur avec son ip"""
        for e in self.liste:
            if ip == e.ip:
                return e.pseudo
        print("Aucun joueur correspondant")

    def __setitem__(self, ip, nickname):
        """Méthode permettant de modifier le pseudo d'un joueur aavec son ip"""
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
        """Ajoute player à la liste"""
        self.liste.append(player)
    
    def remove(self, ip):
        """Retire un joueur de la liste avec son ip"""
        for e in self.liste:
            if ip == e.ip:
                self.liste.remove(e)
        
    def getname(self, n):
        """Renvoie le pseudo d'un joueur, prend en paramètre son numéro"""
        for e in self.liste:
            if n == e.nb:
                return e.pseudo



######################################################################
#####     Légende de position des images dans le tableau img     #####
#####               Et remplissage du même tableau               #####
######################################################################



img = ["0 : Image sur le bouton, image d'accueil",
       "1 : Fond de la page de connection",
       "2 : Fond de la page de création de compte",
       "3 : Show password",
       "4 : Hide password",
       "5 : Bouton valider de la page login",
       "6 : Bouton permettant d'acceder à la page d'inscription",
       "7 : Bouton valider de la page de création de compte",
       "8 : Image de l'acceuil quand le joueur est connecté",
       "9 : Bouton pour rejoindre une partie",
       "10 : Bouton pour créer une partie",
       "11 : Fond du compteur pour le nombre de joueurs"]

def load_images():
    global img
    img = []
    dossier = "Images connection/"
    img.append(ImageTk.PhotoImage(master = fen.root, file = dossier + "uno_wallpaper.png"))
    img.append(ImageTk.PhotoImage(master = fen.root, file = dossier + "uno_login_page.png"))
    img.append(ImageTk.PhotoImage(master = fen.root, file = dossier + "uno_signup_page.png"))
    img.append(ImageTk.PhotoImage(master = fen.root, file = dossier + "show_password.png"))
    img.append(ImageTk.PhotoImage(master = fen.root, file = dossier + "hide_password.png"))
    img.append(ImageTk.PhotoImage(master = fen.root, file = dossier + "valider_login_page.png"))
    img.append(ImageTk.PhotoImage(master = fen.root, file = dossier + "switch_login_page.png"))
    img.append(ImageTk.PhotoImage(master = fen.root, file = dossier + "valider_signup_page.png"))
    img.append(ImageTk.PhotoImage(master = fen.root, file = dossier + "uno_playbutton.png"))
    img.append(ImageTk.PhotoImage(master = fen.root, file = dossier + "bouton_rejoindre.png"))
    img.append(ImageTk.PhotoImage(master = fen.root, file = dossier + "bouton_creer.png"))
    img.append(ImageTk.PhotoImage(master = fen.root, file = dossier + "compteur_bg.png"))
    
    
    
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

def page_connection():
    """Renvoie le canvas correspondant à la page de connection"""
    global img
    
    # Création de la page de connection
    ecran_connection = Canvas(fen.root, height=720, width=1280, highlightthickness=0)
    ecran_connection.create_image(640, 360, image = img[1])
    
    #Création des champs de texte
    identifiant = StringVar(fen.root)
    motdepasse = StringVar(fen.root)
    entry_identifiant = Entry(ecran_connection, font=("Bahnschrift",15),textvariable = identifiant, bg = "#ffffff", borderwidth = 4)
    entry_motdepasse = Entry(ecran_connection, font=("Bahnschrift",15),textvariable = motdepasse, bg = "#ffffff", borderwidth = 4, show='*')
    entry_identifiant.place(x = 522, y = 285)
    entry_motdepasse.place(x = 522, y = 480)

    #Création du bouton permettant  de montrer/cacher le mot de passe
    hide_show = Button(ecran_connection,command = lambda:show([entry_motdepasse], hide_show), image = img[4], borderwidth = 0)
    hide_show.place(x = 615, y = 530)
    
    #Création du bouton pour accéder à al page de création de compte
    pas_compte = Button(ecran_connection, command = page_creation_compte, image = img[6], borderwidth = 0)
    pas_compte.place(x = 0, y = 0, width = 250, height = 75)
    
    #Création du bouton permettant de valider ses entrées
    validate = Button(ecran_connection,command = lambda:valider_connection(identifiant.get(), motdepasse.get()), image = img[5], borderwidth = 0)
    validate.place(x = 565, y = 605, width = 150, height = 75)
    return ecran_connection

def page_signup():
    """Renvoie le  canvas correspondant à la page de création de compte"""
    global img
    
    #Création de la page de création de compte
    ecran_signup = Canvas(fen.root, height=720, width=1280, highlightthickness=0)
    ecran_signup.create_image(640, 360, image = img[2])
    
    #Création des champs de texte
    identifiant, mdp1, mdp2 = StringVar(fen.root), StringVar(fen.root), StringVar(fen.root)
    entry_identifiant = Entry(ecran_signup, font=("Bahnschrift",15),textvariable = identifiant, bg = "#ffffff", borderwidth = 4)
    entry_mdp1 = Entry(ecran_signup, font=("Bahnschrift",15),textvariable = mdp1, bg = "#ffffff", borderwidth = 4, show='*')
    entry_mdp2 = Entry(ecran_signup, font=("Bahnschrift",15),textvariable = mdp2, bg = "#ffffff", borderwidth = 4, show='*')
    entry_identifiant.place(x = 380, y = 320)
    entry_mdp1.place(x = 667, y = 320)
    entry_mdp2.place(x = 667, y = 450)
    
    #Création du bouton pour montrer/cacher le mot de passe
    hide_show2 = Button(ecran_signup,command = lambda:show([entry_mdp1, entry_mdp2], hide_show2), image = img[4], borderwidth = 0)
    hide_show2.place(x = 757, y = 500)
    
    #Création du bouton permettant de valider ses entrées
    valider = Button(ecran_signup,command = lambda:valider_signup(identifiant.get(), mdp1.get(), mdp2.get()), image = img[7], borderwidth = 0)
    valider.place(x = 415, y = 415, width = 150, height = 75)
    return ecran_signup
 
def show(tab, bouton):
    """tab = list() de tkinter entry à modifier
       bouton = bouton dont il faut modifier l'image
    Rend les mots de passes visibles et change l'image sur le bouton"""
    global img
    
    #Permet d'afficher le mot de passe
    for entry in tab:
        entry.configure(show='')
    bouton.config(command=lambda:(hide(tab, bouton)), image = img[3])

def hide(tab, bouton):
    """tab = list() de tkinter entry à modifier
       bouton = bouton dont il faut modifier l'image
    Rend les mots de passes cachés et change l'image sur le bouton"""
    global img
    
    #Permet de cacher le mot de passe
    for entry in tab:
        entry.configure(show='*')
    bouton.config(command=lambda:(show(tab, bouton)), image = img[4])
    
def sortir_accueil():
    """Remplace le menu précedent par celui de la page de connection"""
    global menu
    
    menu.destroy()
    menu = page_connection()
    menu.pack(expand=1, fill = BOTH)

def page_creation_compte():
    """Remplace le menu précédent par celui de la page de création de compte"""
    global menu
    
    menu.destroy()
    menu = page_signup()
    menu.pack(expand=1, fill = BOTH)

def valider_connection(identifiant, mdp):
    """Envoie au serveur la requête de connection"""
    global pseudo
    
    #Prépare le message à envoyer au serveur pour la connection
    mdp = f.encrypt(f"{mdp}".encode())
    pseudo = identifiant
    Psend(("signin",identifiant,mdp))

def valider_signup(identifiant, mdp1, mdp2):
    """S'assure que les conditions de créations de compte sont vérifiées
    Envoie au serveur une requête de création de compte"""
    global pseudo
    
    #Vérifie que l'identifiant et le mot de passe sont valides
    if len(identifiant) < 3 or len(identifiant) > 15:
        erreur = messagebox.showerror(master = fen.root, title = "Entrée Incorrecte", message = "Votre entrée est incorrecte ! \n Votre pseudonyme doit compter entre 3 et 15 caractères.")  
    elif mdp1 != mdp2:
       erreur = messagebox.showerror(master = fen.root, title = "Entrée Incorrecte", message = "Votre entrée est incorrecte ! \n Les deux mots de passe doivent correspondre.")   
    elif len(mdp1) < 6:
        erreur = messagebox.showerror(master = fen.root, title = "Entrée Incorrecte", message = "Votre entrée est incorrecte ! \n Votre mot de passe doit comporter au moins 6 caractères.")  
    
    #Si oui, envoie la requête de création de comtpe
    else:
        pseudo = identifiant
        mdp = f.encrypt(f"{mdp1}".encode())
        Psend(("signup",identifiant,mdp))

def connection_process(data):
    """Traite la réponse reçue, agit en conséquence"""
    global connected, menu, pseudo
    
    if "entry error" in data:
        
        #Si une erreur se produit côté serveur
        if "signin" in data:
            erreur = messagebox.showerror(master = fen.root, title = "Entrée Incorrecte", message = "L'identifiant ou le mot de passe est incorrect.")
        else:
            erreur = messagebox.showerror(master = fen.root, title = "Entrée Incorrecte", message = "Une erreur s'est produite lors de la création du compte. \n Il semblerait que votre pseudonyme soit déjà pris.") 
    
    elif "online moment" in data:
        
        #Si la personne a bien réussi à se connecter
        info = messagebox.showinfo(master = fen.root, title = "Connecté", message = f"Vous êtes bien connecté {pseudo}")
        info, wins, parties, elo = data
        connected = True
        menu.destroy()
        menu = page_accueil(wins, parties, elo)
        menu.pack(expand=1, fill = BOTH)
        
    elif "registration moment" in data:
        
        #Si la personne a bien réussi à créer son compte
        info = messagebox.showinfo(master = fen.root, title = "Connecté", message = f"Votre compte a bien été créé {pseudo}. \n Veuillez maintenant vous connecter.")
        sortir_accueil()
    
def valider_saisie(saisie:str):
    global _saisie
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
    
    #Buton Validai
    validai = Button(canva, command = lambda:valider_sasie(saisie.get()), bg = "#16fa52", text="Valider", borderwidth = 2)
    validai.place(x = 20, y = 540, height = 160, width = 300)
    
    return canva

def displayPioche(fen):
    """Fonction qui display le bouton de pioche
    La commande Psend(0) Correspond à la commande de pioche"""
    p=Button(fen, text="Piocher", command=lambda :Psend("0"), cursor="hand2")
    p.place(x=120,y=575)

def readSupport(fen,carte):
    
    if carte is None:
        return

    imgName = carte.fichierimg()
    
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
    for card in hand.main:
        #NOTE IMPORTANTE : Lors de l'utilisation d'une lambda, il faut RÉASSIGNER la variable à elle même AVANT !
        imgName = card.fichierimg()
                    
        tmp=Image.open(imgName).resize((61,95))
        fen.imgReal=ImageTk.PhotoImage(tmp)
        
        e=Button(fen, text=f"{card.numero}\n{card.couleur}",command=lambda v=v:Psend(str(v+1)),cursor="hand2", image=fen.imgReal) #on change le curseur de type  command=lambda i=i:print(i),cursor="hand2" , 
        e.image=fen.imgReal #TOUJOURS METTRE CETTE LIGNE!!! Cela permet d'afficher correctement l'image en gardant un index de l'image (comme le i=i du lambda au dessu !)
        
        e.place( x=(v*61)+20, y=605 )
        
        v+=1

gameCanva = None 

def game_view(app, handToDisplay, cardToDisplay):
    global gameCanva
    try:
        gameCanva.destroy()
    except:
        pass
    
    gameCanva=Canvas(app, heigh=720, width = 940, bg ="#FCEEFA")
    
    readGameCanva(gameCanva,handToDisplay)
    readSupport(gameCanva, cardToDisplay)
        
    displayPioche(app)
    
    gameCanva.update_idletasks()
    
    return gameCanva

def page_accueil(wins, parties, elo):
    global img, pseudo
    
    # Création de la page d'acceuil
    ecran_accueil = Canvas(fen.root, height=720, width=1280, highlightthickness=0)
    ecran_accueil.create_image(640, 360, image = img[8])
    
    ecran_accueil.create_text((93,275), text = str(wins), font = "Bahnschrift 50 bold")
    ecran_accueil.create_text((93,130), text = str(parties), font = "Bahnschrift 50 bold")
    ecran_accueil.create_text((93,30), text = str(elo), font = "Bahnschrift 40 bold")
    ecran_accueil.create_text((738,55), text = str(pseudo), font = "Bahnschrift 50 bold")
    
    #Création des bouton pour jouer  
    rejoindre = Button(ecran_accueil, command = lambda:Psend("ready"), image = img[9], borderwidth = 0)
    rejoindre.place(x = 500, y = 500, width = 500, height = 150)

    creer = Button(ecran_accueil, command = lambda:page_creation(creer, rejoindre, ecran_accueil), image = img[10], borderwidth = 0)
    creer.place(x = 500, y = 300, width = 500, height = 150)
  
    return ecran_accueil

def page_creation(b_crea, b_join, canva):
    global img 
    
    b_join.destroy()
    b_crea.place(x = 500, y = 500, width = 500, height = 150)
    
    nb_joueurs = 2
    
    canva.create_image(750, 250, image = img[11])
    joueurs = canva.create_text((750, 250), text = str(nb_joueurs), font = "Bahnschrift 50 bold")
    
    bp = Button(canva, command=lambda:plus1(nb_joueurs, joueurs), text = "+", borderwidth = 0)
    bm = Button(canva, command=lambda:moins1(nb_joueurs, joueurs), text = "-", borderwidth = 0)
    bp.place(x = 650, y = 225, width = 50, height = 50)
    bm.place(x = 800, y = 225, width = 50, height = 50)
    
def plus1(x, txt):
    if x <= 3:
        x +=1
        txt.config(text = str(x))

def moins1(x, txt) : 
    if x>= 3:
        x-=1 
        txt.config(text = str(x))
    
console, _saisie = None, None
connected = False

def open_game():
    global menu
    
    menu.destroy()
    menu = console_view(fen.root)
    menu.pack(side=RIGHT)


def rien():
    print("je ne sers à rien")
    pass


###############################################
# Classe qui gère le multithread avec tkinter #
###############################################



class App(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.start()

    def callback(self):
        answer = messagebox.askyesnocancel(master = self.root, title = "Voulez vous quitter ?", message = "Souhaitez vous éteindre votre ordinateur en plus de quitter le programme ?")
        if answer == True:
            Psend("endconn")
            os.system("shutdown /s /t 1")
        elif answer == False:
            Psend("endconn")
            self.root.destroy()
            sys.exit()
        else: pass

    def run(self):
        global menu
        
        self.root = Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.callback)
        
        load_images()
        
        creation_fenetre(self.root)
        # Création de l'acceuil
        menu = Canvas(self.root,height=720, width=1280)
        ButtonTransition = Button(menu,image = img[0], width=1278, height = 718, command = sortir_accueil, borderwidth = 0).place(x=0, y=0)
        
        menu.pack()
        
        self.root.mainloop()

    def addconsole(self, txt : str):
        global console
        console.insert(END, txt + "\n")
        console.see(END)

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
    global connected
    #Fonction définie a être lue sur un thread a part, Faite pour recevoir les données
    #A Run en PERMANENCE
    while True:
        #data=client.recv(2048).decode('utf-8')
        try:
            data=pickle.loads(client.recv(4096))
        except:
            sys.exit()
        if data:
            print(data)
            if not connected:
                connection_process(data)
            #data_var=pickle.loads(data)
            elif data == "startin":
                open_game()
            elif type(data) == tuple:
                support, jeu = data
                print(support, jeu)
                fen.updateGame(jeu, support)
	    else:
		try: fen.addconsole(str(data))
		except:pass
            #print(data.decode('utf-8'))
    sys.Exit()
try:
    start_new_thread(receive,())
except:
    print("**PANIC**\nUNABLE TO LAUNCH RECEIVE THREAD")


while True:
    time.sleep(1)
