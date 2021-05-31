# -*- coding: utf-8 -*-

######################
# Import des modules #
######################



import tkinter as tk
from PIL import Image, ImageTk
from cryptography.fernet import Fernet
from client import Psend


#########################################################
#####     Système de cryptage des mots de passe     #####
#########################################################



str_key = open("key.txt.txt","r").readline()
key = str.encode(str_key)
f = Fernet(key)


class ConnectionCanvas:
    """Classe représentant le canvas de la partie de connection avant le jeu"""
    
    def __init__(self, fen):
        self.fen = fen
        self.load_images(fen)
        self = tk.Canvas(self.root,height=720, width=1280)
        ButtonTransition = tk.Button(self,image = self.img[0], width=1278, height = 718, command = self.page_signin, borderwidth = 0).place(x=0, y=0)
        
    def load_images(self):
        """Charge les images de la partie de connection dès le début
           afin de rendre la suite plus fluide"""
        self.img = []
        dossier = "Images connection/"
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
        validate = tk.Button(self.next, command = lambda:self.requete_connection(identifiant.get(), motdepasse.get()), image = self.img[5], borderwidth = 0)
        validate.place(x = 565, y = 605, width = 150, height = 75)
        
        #Remplacemlent du canvas affiché
        self.destroy()
        self = self.next
        self.pack()

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
        self.destroy()
        self = self.next
        self.pack()

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
        
        #Prépare le message à envoyer au serveur pour la connection
        mdp = f.encrypt(f"{mdp}".encode())
        self.pseudo = identifiant
        Psend("signin",identifiant,mdp)
    
    def requete_signup(self, identifiant, mdp1, mdp2):
        """S'assure que les conditions de créations de compte sont vérifiées
        Envoie au serveur une requête de création de compte"""
        
        #Vérifie que l'identifiant et le mot de passe sont valides
        if len(identifiant) < 3 or len(identifiant) > 15:
            erreur = tk.messagebox.showerror(master = self.fen.root, title = "Entrée Incorrecte", message = "Votre entrée est incorrecte ! \n Votre pseudonyme doit compter entre 3 et 15 caractères.")  
        elif mdp1 != mdp2:
            erreur = tk.messagebox.showerror(master = self.fen.root, title = "Entrée Incorrecte", message = "Votre entrée est incorrecte ! \n Les deux mots de passe doivent correspondre.")   
        elif len(mdp1) < 6:
            erreur = tk.messagebox.showerror(master = self.fen.root, title = "Entrée Incorrecte", message = "Votre entrée est incorrecte ! \n Votre mot de passe doit comporter au moins 6 caractères.")  
        
        #Si oui, envoie la requête de création de comtpe
        else:
            self.pseudo = identifiant
            mdp = f.encrypt(f"{mdp1}".encode())
            Psend(("signup",identifiant,mdp))
            
    def page_accueil(self, wins, parties, elo):
        
        # Création de la page d'acceuil
        self.next = tk.Canvas(self.fen.root, height=720, width=1280, highlightthickness=0)
        self.next.create_image(640, 360, image = self.img[8])
        self.next.create_text((93,275), text = str(wins), font = "Bahnschrift 50 bold")
        self.next.create_text((93,130), text = str(parties), font = "Bahnschrift 50 bold")
        self.next.create_text((93,30), text = str(elo), font = "Bahnschrift 40 bold")
        self.next.create_text((738,55), text = str(self.pseudo), font = "Bahnschrift 50 bold")
        
        #Création des bouton pour jouer  
        self.rejoindre = tk.Button(self.next, command = lambda:Psend("ready"), image = self.img[9], borderwidth = 0)
        self.rejoindre.place(x = 500, y = 500, width = 500, height = 150)
    
        self.creer = tk.Button(self.next, command = lambda:self.page_creation(), image = self.img[10], borderwidth = 0)
        self.creer.place(x = 500, y = 300, width = 500, height = 150)
      
        #Remplace le canvas par celui de création d'une partie
        self.destroy()
        self = self.next
        self.pack()

    def page_creation(self):
        """Renvoie le  canvas correspondant à la page de création de partie"""
        
        self.rejoindre.destroy()
        self.creer.place(x = 500, y = 500, width = 500, height = 150)
        
        self.nb_joueurs = 2
        
        self.create_image(750, 250, image = self.img[11])
        self.str_nbjoueurs = self.create_text((750, 250), text = str(self.nbjoueurs), font = "Bahnschrift 50 bold")
        
        bp = tk.Button(self, command = self.plus, text = "+", borderwidth = 0)
        bm = tk.Button(self, command = self.moins, text = "-", borderwidth = 0)
        bp.place(x = 650, y = 225, width = 50, height = 50)
        bm.place(x = 800, y = 225, width = 50, height = 50)
        
    def plus(self):
        """Ajoute 1 au nombre de joueurs de la partie
        si cela ne pose pas de problème"""
        if self.nbjoueurs < 4:
            self.nbjoueurs += 1
            self.str_nbjoueurs.destroy()
            self.str_nbjoueurs = self.create_text((750, 250), text = str(self.nbjoueurs), font = "Bahnschrift 50 bold")
            
    def moins(self):  
        """Retire 1 au nombre de joueurs de la partie
        si cela ne pose pas de problème"""
        if self.nbjoueurs > 2:
            self.nbjoueurs -= 1
            self.str_nbjoueurs.destroy()
            self.str_nbjoueurs = self.create_text((750, 250), text = str(self.nbjoueurs), font = "Bahnschrift 50 bold")   
        




















