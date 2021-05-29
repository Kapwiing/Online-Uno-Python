# -*- coding: utf-8 -*-
"""
Created on Fri May 21 10:54:01 2021

@author: clementg
"""

from uno_class import *
from tkinter import *
from PIL import Image, ImageTk

def creation_fenetre_game(fenetre):
    """permet de définir la taille de la fenêtre (ici résolution 600x600)
              de le centrer au milieu de l'écran
              et de faire en sorte que l'utilisateur ne puisse pas changer la taille
              de le nommer
    """

    #Récupérer la résolution de l'écran utilisé
    screen_x = int(fenetre.winfo_screenwidth())
    screen_y = int(fenetre.winfo_screenheight())

    #Entrer les valeurs de taille de la fenêtre
    window_x = 800
    window_y = 700

    #Calcul des coordonnées pour que la fenêtre soit au milieu
    pos_x = (screen_x // 2) - (window_x // 2)
    pos_y = (screen_y // 2) - (window_y // 2)
    geo = "{}x{}+{}+{}".format(window_x, window_y, pos_x, pos_y)

    fenetre.geometry(geo)
    #On bloque la taille en 500x500
    #fenetre.resizable(width=False, height=False)
    fenetre.title("Amoguno-Game")

def PsendLIAR(msg):
    """Fonction temporaire de test en attendnat de mettre le vrai Psend"""
    print(msg)

def piocherLIAR():
    print("Pioched !")

handList=[]


def enemyHand(fen,count):
    """Fonction d'affichage du nombre de cartes du joueur adverse"""
    v=0
    for i in range(count):
        tmp=Image.open("las_cuartas\\uno_back.png").resize((61,95))
        fen.imgReal=ImageTk.PhotoImage(tmp)
        
        k=Button(fen, text="Carte UNO Retournée",cursor="pirate", image=fen.imgReal)
        k.image=fen.imgReal
        k.grid(row=0,column=v)
        v+=1

def readSupport(fen,carte):
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
    l.grid(row=1, column=3)
    

dummyCard=Carte(0,"rouge")

def readGameCanva(fen, hand):
    """Fonction de lecture du jeu (argument hand) et affichage dynamique en Tkinter
    Pour plus de fun, on mettre cete fonction dans le code client, dans le thread de
    récéption afin qu'elle soit continuellement mise à jour"""

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
        
        e=Button(fen, text=f"{i.numero}\n{i.couleur}",command=lambda i=i:print(i+1),cursor="hand2", image=fen.imgReal) #on change le curseur de type  command=lambda i=i:print(i),cursor="hand2" , 
        e.image=fen.imgReal #TOUJOURS METTRE CETTE LIGNE!!! Cela permet d'afficher correctement l'image en gardant un index de l'image (comme le i=i du lambda au dessu !)
        
        e.place( x=(v*61)+20, y=605 )
        
        v+=1

"""
fen=Tk()

a=Carte(7,"rouge")
b=Carte(None, None, True)
c=Carte("+2","vert",True)
d=Carte("+4",None, True)
e=Carte(3,"vert")
    
pile=Pile()
pile.empiler(a)
pile.empiler(b)
pile.empiler(c)
pile.empiler(d)
    
hand=Jeu()
    
for _ in range(4):
    hand.piocher(pile)
#print(hand)
    
creation_fenetre_game(fen)
#print(handList)
    
readGame(fen,hand)
enemyHand(fen,6)
readSupport(fen,e)
displayPioche(fen)
    
fen.mainloop()
"""