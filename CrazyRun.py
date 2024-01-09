import pygame
import time
from random import choice,randint

pautogui = False #Adaptation de la fenêtre à l'écran
if pautogui:
    import pyautogui

accelerometre = False
if accelerometre:
    import smbus

import sqlite3
import csv
conn = sqlite3.connect('CrazyBase.db')
C = conn.cursor()

import matplotlib.pyplot as plt
from math import ceil,floor

pygame.init()

#Paramètres spaciaux du jeu
plein_ecran = False
ncolonnes = 5
nlignes = 10
ybase = 8
hmax = 1 #Hauteur du saut
if pautogui:
    ecranx, ecrany = pyautogui.size()
    if plein_ecran:
        taille = int(ecrany/(nlignes)) #Taille d'une case
        margegauche = int((ecranx - ncolonnes*taille)/(2*taille))+1
        margedroite = margegauche
        dx = ecranx - (margegauche + ncolonnes + margedroite)*taille #Decalage de l'abcisse de tous les elements du jeu
    else:
        taille = int(ecrany/(nlignes*2)) #Taille d'une case
        margegauche = int((ecranx - ncolonnes*taille)/(4*taille))
        margedroite = margegauche
        dx = 0
else:
    taille = 100 #Taille d'une case
    margegauche = 2
    margedroite = 2
    dx = 0 #Decalage de l'abcisse de tous les elements du jeu
fenx = taille*(margegauche + ncolonnes + margedroite)
feny = taille*nlignes

#Autres paramètres
vitesse = 0.05 #Vitesse des obstacles
vvisu = 0.25 #Vitesse du singe et du perroquet
vvisuh = 0.1 #Vitesse d'ascension du perroquet
dureesaut = 41 #Duree d'un saut du singe
dureechute = 82 #Duree d'une chute du perroquet
dureeimage = 10 #Duree d'une image de l'animation du singe
delai_struct = 6 #Distance entre deux structures
presence_perroquet = True #Le perroquet est-il present ?

#if pautogui and plein_ecran:
#    screen = pygame.display.set_mode([fenx, feny], pygame.FULLSCREEN)
#else:
#    screen = pygame.display.set_mode([fenx, feny])

if pautogui:
    if plein_ecran:
        taille = int(ecrany/(nlignes)) #Taille d'une case
        margegauche = int((ecranx - ncolonnes*taille)/(2*taille))+1
        margedroite = margegauche
        dx = ecranx - (margegauche + ncolonnes + margedroite)*taille #Decalage de l'abcisse de tous les elements du jeu
        fenx = taille*(margegauche + ncolonnes + margedroite)
        feny = taille*nlignes
        screen = pygame.display.set_mode([fenx, feny], pygame.FULLSCREEN)

    else:
        taille = int(ecrany/(nlignes*2)) #Taille d'une case
        margegauche = int((ecranx - ncolonnes*taille)/(4*taille))
        margedroite = margegauche
        dx = 0
        fenx = taille*(margegauche + ncolonnes + margedroite)
        feny = taille*nlignes
        screen = pygame.display.set_mode([fenx, feny], 0)
else:
    taille = 100 #Taille d'une case
    margegauche = 4
    margedroite = margegauche
    dx = 0
    fenx = taille*(margegauche + ncolonnes + margedroite)
    feny = taille*nlignes
    screen = pygame.display.set_mode([fenx, feny], 0)

#Fonctions pour le jeu

def chargeImages():#Chargement des images
    global img_herbe,img_feuillage,img_feuillage_gauche,img_feuillage_droite,img_singe,img_singe_court1,img_singe_court2,img_singe_saut,img_singe_accroche,img_ombre,img_perroquet1,img_perroquet2,img_trou,img_pilier,chiffres_img

    img_herbe = pygame.transform.scale(pygame.image.load("images/herbe.png").convert_alpha(), (taille, taille))
    img_feuillage = pygame.transform.scale(pygame.image.load("images/feuillage.png").convert_alpha(), (taille, taille))
    img_feuillage_gauche = pygame.transform.scale(pygame.image.load("images/feuillage_gauche.png").convert_alpha(), (taille, taille))
    img_feuillage_droite = pygame.transform.scale(pygame.image.load("images/feuillage_droite.png").convert_alpha(), (taille, taille))

    img_singe = pygame.transform.scale(pygame.image.load("images/singe.png").convert_alpha(), (taille, taille))
    img_singe_court1 = pygame.transform.scale(pygame.image.load("images/singe_course1.png").convert_alpha(), (taille, taille))
    img_singe_court2 = pygame.transform.scale(pygame.image.load("images/singe_course2.png").convert_alpha(), (taille, taille))
    img_singe_saut = pygame.transform.scale(pygame.image.load("images/singe_saut.png").convert_alpha(), (taille, taille))
    img_singe_accroche = pygame.transform.scale(pygame.image.load("images/singe_accroche.png").convert_alpha(), (taille, taille))
    img_ombre = pygame.transform.scale(pygame.image.load("images/ombre.png").convert_alpha(), (taille, taille*2))

    img_perroquet1 = pygame.transform.scale(pygame.image.load("images/perroquet1.png").convert_alpha(), (taille, taille))
    img_perroquet2 = pygame.transform.scale(pygame.image.load("images/perroquet2.png").convert_alpha(), (taille, taille))

    img_trou = pygame.transform.scale(pygame.image.load("images/trou.png").convert_alpha(), (taille, taille))
    img_pilier = pygame.transform.scale(pygame.image.load("images/pilier3.png").convert_alpha(), (taille, taille*3))

    chiffres_img = [pygame.transform.scale(pygame.image.load("images/chiffres/" + str(k) +".png").convert_alpha(), (taille, taille)) for k in range(10)]

chargeImages()

#time.sleep(1)


def perdu(defaite:list):
    global run
    if len(defaite)>0:
        run = False


def fond():#Affichage du fond
    screen.fill((0, 55, 0))
    #pygame.draw.rect(screen, (0, 155, 0), pygame.Rect(taille*margegauche, 0, taille*ncolonnes, taille*nlignes))
    for l in range(nlignes + 1):
        for k in range(ncolonnes):#Affichage de l'herbe
            screen.blit(img_herbe, (dx + taille*(margegauche + k), taille*(l - 1 + (clock*vitesse)%1)))

        for k in range(margegauche):#Affichage de la bordure gauche
            if k == margegauche - 1:
                screen.blit(img_herbe, (dx + taille*k, taille*(l - 1 + (clock*vitesse)%1)))
                screen.blit(img_feuillage_gauche, (dx + taille*k, taille*(l - 1 + (clock*vitesse)%1)))
            else:
                screen.blit(img_feuillage, (dx + taille*k, taille*(l - 1 + (clock*vitesse)%1)))

        for k in range(margedroite):#Affichage de la bordure droite
            if k == 0:
                screen.blit(img_herbe, (dx + taille*(margegauche + ncolonnes + k), taille*(l - 1 + (clock*vitesse)%1)))
                screen.blit(img_feuillage_droite, (dx + taille*(margegauche + ncolonnes + k), taille*(l - 1 + (clock*vitesse)%1)))
            else:
                screen.blit(img_feuillage, (dx + taille*(margegauche + ncolonnes + k), taille*(l - 1 + (clock*vitesse)%1)))



def gererScore():
    global score
    score = int(time.time() - temps_initial)
    for k in range(len(str(score))):
        screen.blit(chiffres_img[int(str(score)[k])], (dx + taille*(margegauche - 1 + largeur_chiffre*(k + 1 - len(str(score)))), 0))



class Singe:
    def __init__(self):
        self.x = ncolonnes//2 #Colonne (commence dans la colonne du milieu)
        self.visux = self.x #x affiché
        self.psaut = 0 #Progression du saut
        self.h = 0 #Hauteur
        self.accroche = False #Si le singe est accroché au perroquet

    def affiche(self):
        if self.accroche:
            self.h = perroquet.h
            self.x = perroquet.x
            self.visux = perroquet.visux
        else:
            if self.psaut == 0:
                self.h = 0
            elif self.psaut < dureesaut/5:#Ascension
                self.h = 1 - ((dureesaut/5 - self.psaut)**2)/((dureesaut/5)**2)
            elif self.psaut <= (dureesaut/5)*4:#Hauteur maximale
                self.h = 1
            else:#Redescente
                self.h = 1 - ((self.psaut - (dureesaut/5)*4)**2)/((dureesaut/5)**2)

        screen.blit(img_ombre, (dx + taille*(margegauche + self.visux), taille*ybase)) #Affichage de l'ombre
        if self.psaut == 0 and not self.accroche:
            '''
            if clock%(dureeimage*2) < dureeimage:
                screen.blit(img_singe, (dx + taille*(margegauche + self.visux), taille*ybase)) #Affichage du singe au sol (image 1)
            elif clock%(dureeimage*4) < dureeimage*2:
                screen.blit(img_singe_court1, (dx + taille*(margegauche + self.visux), taille*ybase)) #Affichage du singe au sol (image 1)
            else:
                screen.blit(img_singe_court2, (dx + taille*(margegauche + self.visux), taille*ybase)) #Affichage du singe au sol (image 2)
            '''
            if clock%(dureeimage*2) < dureeimage:
                screen.blit(img_singe_court1, (dx + taille*(margegauche + self.visux), taille*ybase)) #Affichage du singe au sol (image 1)
            else:
                screen.blit(img_singe_court2, (dx + taille*(margegauche + self.visux), taille*ybase)) #Affichage du singe au sol (image 2)
        elif self.accroche:
            screen.blit(img_singe_accroche, (dx + taille*(margegauche + self.visux), taille*(ybase - self.h*hmax))) #Affichage du singe accroche au perroquet
        else:
            screen.blit(img_singe_saut, (dx + taille*(margegauche + self.visux), taille*(ybase - self.h*hmax))) #Affichage du singe en l'air
        #pygame.draw.rect(screen, (155, 55, 0), pygame.Rect(taille*(margegauche + self.x), taille*(ybase - int(bool(self.hauteur))), taille, taille))

    def accrochage(self):
        global aide
        if self.x == perroquet.x and self.h == perroquet.h:
            self.accroche = True
            perroquet.pchute = 1
            aide += 1
            self.psaut = 0
        if perroquet.pchute == 0:
            self.accroche = False

    def visu(self):#Définit l'abcisse du singe visuellement pour que les déplacements soient fluides
        if not self.accroche:
            if self.x < self.visux:
                self.visux = round(self.visux - vvisu,3)
            elif self.x > self.visux:
                self.visux = round(self.visux + vvisu,3)

    def gauche(self):#Decale de 1 vers la gauche
        if self.x > 0 and not self.accroche:
            self.x -= 1

    def droite(self):#Decale de 1 vers la droite
        if self.x < ncolonnes-1 and not self.accroche:
            self.x += 1

    def haut(self):#Début du saut
        if self.psaut == 0 and not self.accroche:
            self.psaut += 1

    def saut(self):#Gestion du saut
        if self.psaut > 0 and not self.accroche:
            self.psaut = (self.psaut + 1)%dureesaut


class Perroquet:
    def __init__(self):
        self.x = ncolonnes//2 #Colonne (commence dans la colonne du milieu)
        self.visux = self.x #x affiché
        self.pchute = 0 #Progression de la chute
        self.h = hmax #Hauteur
        self.visuh = self.h #Hauteur affichée

    def afficheOmbre(self):
        screen.blit(img_ombre, (dx + taille*(margegauche + self.visux), taille*ybase)) #Affichage de l'ombre

    def affiche(self):
        if self.pchute == 0:
            self.h = hmax
        else:#Descente
            self.h = 1 - ((self.pchute)**2)/((dureechute)**2)

        if clock%(dureeimage*2) < dureeimage:
            screen.blit(img_perroquet1, (dx + taille*(margegauche + self.visux), taille*(ybase - self.visuh*hmax - 0.5))) #Affichage du perroquet en l'air (image 1)
        else:
            screen.blit(img_perroquet2, (dx + taille*(margegauche + self.visux), taille*(ybase - self.visuh*hmax - 0.5))) #Affichage du perroquet en l'air (image 2)

    def visu(self):#Définit l'abcisse du singe visuellement pour que les déplacements soient fluides
        if self.x < self.visux:
            self.visux = round(self.visux - vvisu,3)
        elif self.x > self.visux:
            self.visux = round(self.visux + vvisu,3)

        if abs(self.visuh - self.h)>vvisuh and presence_perroquet:
            if self.h < self.visuh:
                self.visuh = round(self.visuh - vvisuh,3)
            elif self.h > self.visuh:
                self.visuh = round(self.visuh + vvisuh,3)
        else:
            self.visuh = self.h

    def gauche(self):#Decale de 1 vers la gauche
        if self.x > 0:
            self.x -= 1

    def droite(self):#Decale de 1 vers la droite
        if self.x < ncolonnes-1:
            self.x += 1

    def chute(self):#Gestion du saut
        if self.pchute > 0:
            self.pchute = (self.pchute + 1)%dureechute




def obstaclesPeriodiques(Obstacle, periode, depart):
    global obstacles
    if clock%(periode/vitesse) == (depart/vitesse) or (clock%(periode/vitesse) == 0 and periode == 1):
        obstacles += [Obstacle(randint(0,ncolonnes-1))]

def apparitionObstacles():
    global obstacles
    if structures != []:
        for k in range(len(structures[0])):
            if structures[0][k] == "1":
                obstacles += [Trou(k)]
            elif structures[0][k] == "2":
                obstacles += [Pilier(k)]
        del structures[0]


class Trou:
    def __init__(self, abcissex):
        self.x = abcissex
        self.y = -1
        self.singe_saute = 0

    def derriereSinge(self):#Le trou est affiché derrière le singe
        return True

    def affiche(self):
        screen.blit(img_trou, (dx + taille*(margegauche + self.x), taille*(self.y)))
        #pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(taille*(margegauche + self.x), taille*(self.y), taille, taille))

    def defile(self):
        self.y = round(self.y + vitesse,3)
        return self.y >= nlignes

    def contact(self):
        global obs
        if self.singe_saute == 0 and (self.x == singe.x) and (ybase <= self.y and self.y < ybase + 1) and (singe.psaut != 0 or singe.accroche):
            self.singe_saute = 1
        if self.singe_saute == 1 and not ((self.x == singe.x) and (ybase <= self.y and self.y < ybase + 1)):
            self.singe_saute = 2
            obs += 1
        if (self.x == singe.x) and (ybase <= self.y and self.y < ybase + 1) and (singe.psaut == 0 and not singe.accroche):
            return ["st"] #Si le singe tombe dans un trou
        else:
            return []


class Pilier:
    def __init__(self, abcissex):
        self.x = abcissex
        self.y = -1

    def derriereSinge(self):#Le pilier doit-il être affiché derrière le singe ?
        return self.y <= ybase

    def affiche(self):
        screen.blit(img_pilier, (dx + taille*(margegauche + self.x), taille*(self.y - 2)))
        #pygame.draw.rect(screen, (55, 55, 55), pygame.Rect(taille*(margegauche + self.x), taille*(self.y - 1), taille, taille*2))

    def defile(self):
        self.y = round(self.y + vitesse,3)
        return self.y >= nlignes + 2

    def contact(self):
        r = []
        if (self.x == singe.x) and (ybase <= self.y and self.y < ybase + 1):
            r += ["sp"] #Si le singe percute un pilier
        if presence_perroquet :
            if (self.x == perroquet.x) and (ybase <= self.y and self.y < ybase + 1):
                r += ["pp"] #Si le perroquet percute un pilier
        return r

struct_niv0 = [["11100"],["11001"],["10011"],["00111"]]
struct_niv1 = [["22100"],["22001"],["10022"],["00122"],["11111"],["20102"],["11200","00200","00202"],["00211","00200","20200"],["20002","02020"]]
struct_niv2 = [["22200","00000","00000","00000","00000","00222"],["00222","00000","00000","00000","00000","22200"],["21212"],["12121"],["11111","00000","00000","11111"]]
struct_niv3 = [["01110","01110","10001","10001","20002"],["10101","10101","01010","01010","02020"]]
struct_niv4 = [["11101","11101","22000","00020"],["10111","10111","00022","02000"],["10111","10111","11011","11011","11101","11101"],["11101","11101","11011","11011","10111","10111"]]
struct_niv5 = [["00000","22220","00000","00000","00000","00000","00000","00000","00000","02222"],["00000","02222","00000","00000","00000","00000","00000","00000","00000","22220"],["00000","22211","00000","00000","00000","00000","11222"],["00000","11222","00000","00000","00000","00000","22211"]]
struct_perr_niv2 = [["22122","22122"],["12221","12221"]]
struct_perr_niv3 = [["11111","11111","11111","00000","00000","11111"]]

ecartniv = 15

Lstruct1j = [struct_niv0, struct_niv1, struct_niv2, struct_niv3, struct_niv4, struct_niv5, struct_perr_niv2, struct_perr_niv3]
Lstruct2j = [struct_niv0+struct_niv1, struct_niv2, struct_niv3, struct_perr_niv2, struct_niv4, struct_niv5, struct_perr_niv3]

pseudo1 = "ecrire"

police = pygame.font.Font("freesansbold.ttf",int(taille/2))
policetitre = pygame.font.Font("freesansbold.ttf",int(taille))



#BOUCLE DU JEU

menurun = True
menujrun = 0
while menurun:
    screen.fill((0, 55, 0))

    clic = 0
    pygame.draw.rect(screen, (255, 255, 0), pygame.Rect((fenx-7*taille)/2, (feny-taille)/2, taille*3, taille))
    pygame.draw.rect(screen, (255, 255, 0), pygame.Rect((fenx+taille)/2, (feny-taille)/2, taille*3, taille))
    screen.blit(police.render("1 joueur",False,(0,0,0)),((fenx-6*taille)/2, (feny-taille/2)/2))
    screen.blit(police.render("2 joueurs",False,(0,0,0)),((fenx+3*taille/2)/2, (feny-taille/2)/2))
    screen.blit(policetitre.render("CRAZY RUN",False,(255,255,0)),((fenx-6.1*taille)/2,taille))
    pygame.display.flip()
    while clic==0:
        ev = pygame.event.get()
        for event in ev:
            if event.type == pygame.QUIT:
                clic = -1
                menurun = False
            if event.type==pygame.MOUSEBUTTONUP:
                mx,my = pygame.mouse.get_pos()
                if (fenx-5*taille)/2<mx and mx<(fenx-taille)/2 and (feny-taille)/2<my and my<(feny+taille)/2:
                    clic = 1 #Jouer
                    menujrun = 1
                if (fenx+taille)/2<mx and mx<(fenx+5*taille)/2 and (feny-taille)/2<my and my<(feny+taille)/2:
                    clic = 2 #Menu
                    menujrun = 2

    while menujrun>0:

        screen.fill((0, 55, 0))

        select = 0
        clic = 0
        pygame.draw.rect(screen, (255, 255, 0), pygame.Rect((fenx-5*taille)/2, feny/2, taille*2, taille))
        pygame.draw.rect(screen, (255, 0, 0), pygame.Rect((fenx+taille)/2, feny/2, taille*2, taille))
        if menujrun>0:
            pygame.draw.rect(screen, (255, 255, 255), pygame.Rect((fenx-4*taille)/2, (feny-3*taille)/2, taille*4, taille/2))
        pygame.display.flip()

        keys = pygame.key.get_pressed()
        a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z,supprime = keys[pygame.K_a],keys[pygame.K_b],keys[pygame.K_c],keys[pygame.K_d],keys[pygame.K_e],keys[pygame.K_f],keys[pygame.K_g],keys[pygame.K_h],keys[pygame.K_i],keys[pygame.K_j],keys[pygame.K_k],keys[pygame.K_l],keys[pygame.K_m],keys[pygame.K_n],keys[pygame.K_o],keys[pygame.K_p],keys[pygame.K_q],keys[pygame.K_r],keys[pygame.K_s],keys[pygame.K_t],keys[pygame.K_u],keys[pygame.K_v],keys[pygame.K_w],keys[pygame.K_x],keys[pygame.K_y],keys[pygame.K_z],keys[pygame.K_BACKSPACE]
        while clic==0:
            partierun = False
            ev = pygame.event.get()
            for event in ev:
                if event.type == pygame.QUIT:
                    clic = -1
                    menujrun = 0
                    menurun = False
                if event.type==pygame.MOUSEBUTTONUP:
                    mx,my = pygame.mouse.get_pos()

                    if (fenx-5*taille)/2<mx and mx<(fenx-taille)/2 and feny/2<my and my<(feny+2*taille)/2:
                        clic = 1 #Jouer
                        partierun = True

                    if (fenx-taille)/2<mx and mx<(fenx+5*taille)/2 and feny/2<my and my<(feny+2*taille)/2:
                        clic = 2 #Menu
                        menujrun = 0

                    if menujrun>0:
                        if (fenx-4*taille)/2<mx and mx<fenx/2+taille*2 and (feny-3*taille)/2<my and my<(feny-2*taille)/2:
                            select = 1
                        else:
                            select = 0


            keys = pygame.key.get_pressed()
            a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z,supprime,pa,pb,pc,pd,pe,pf,pg,ph,pi,pj,pk,pl,pm,pn,po,pp,pq,pr,ps,pt,pu,pv,pw,px,py,pz,psupprime = keys[pygame.K_a],keys[pygame.K_b],keys[pygame.K_c],keys[pygame.K_d],keys[pygame.K_e],keys[pygame.K_f],keys[pygame.K_g],keys[pygame.K_h],keys[pygame.K_i],keys[pygame.K_j],keys[pygame.K_k],keys[pygame.K_l],keys[pygame.K_m],keys[pygame.K_n],keys[pygame.K_o],keys[pygame.K_p],keys[pygame.K_q],keys[pygame.K_r],keys[pygame.K_s],keys[pygame.K_t],keys[pygame.K_u],keys[pygame.K_v],keys[pygame.K_w],keys[pygame.K_x],keys[pygame.K_y],keys[pygame.K_z],keys[pygame.K_BACKSPACE],a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z,supprime
            if select==1:
                if a and not pa: pseudo1 += "a"
                if b and not pb: pseudo1 += "b"
                if c and not pc: pseudo1 += "c"
                if d and not pd: pseudo1 += "d"
                if e and not pe: pseudo1 += "e"
                if f and not pf: pseudo1 += "f"
                if g and not pg: pseudo1 += "g"
                if h and not ph: pseudo1 += "h"
                if i and not pi: pseudo1 += "i"
                if j and not pj: pseudo1 += "j"
                if k and not pk: pseudo1 += "k"
                if l and not pl: pseudo1 += "l"
                if m and not pm: pseudo1 += "m"
                if n and not pn: pseudo1 += "n"
                if o and not po: pseudo1 += "o"
                if p and not pp: pseudo1 += "p"
                if q and not pq: pseudo1 += "q"
                if r and not pr: pseudo1 += "r"
                if s and not ps: pseudo1 += "s"
                if t and not pt: pseudo1 += "t"
                if u and not pu: pseudo1 += "u"
                if v and not pv: pseudo1 += "v"
                if w and not pw: pseudo1 += "w"
                if x and not px: pseudo1 += "x"
                if y and not py: pseudo1 += "y"
                if z and not pz: pseudo1 += "z"
                if supprime and not psupprime: pseudo1 = pseudo1[:-1]
                #print(pseudo1)

            screen.fill((0, 55, 0))
            pygame.draw.rect(screen, (255, 255, 0), pygame.Rect((fenx-5*taille)/2, feny/2, taille*2, taille))
            pygame.draw.rect(screen, (255, 0, 0), pygame.Rect((fenx+taille)/2, feny/2, taille*2, taille))

            textepseudo1 = police.render(pseudo1,False,(0,0,0))

            if select!=1:
                pygame.draw.rect(screen, (255, 255, 255), pygame.Rect((fenx-4*taille)/2, (feny-3*taille)/2, taille*4, taille/2))
            else:
                pygame.draw.rect(screen, (155, 155, 255), pygame.Rect((fenx-4*taille)/2, (feny-3*taille)/2, taille*4, taille/2))

            if menujrun==1:
                screen.blit(police.render("1 joueur",False,(255,255,255)),(taille/2,taille/2))
            if menujrun==2:
                screen.blit(police.render("2 joueurs",False,(255,255,255)),(taille/2,taille/2))
            screen.blit(police.render("jouer",False,(0,0,0)),((fenx-4.3*taille)/2, (feny+taille/2)/2))
            screen.blit(police.render("quitter",False,(0,0,0)),((fenx+taille*1.3)/2, (feny+taille/2)/2))
            screen.blit(police.render("pseudo : ",False,(255,255,255)),((fenx-9*taille)/2,(feny-3*taille)/2))
            screen.blit(textepseudo1,((fenx-4*taille)/2,(feny-3*taille)/2))

            pygame.display.flip()

            time.sleep(0.01)

        while partierun:

            score = 0
            aide = 0
            obs = 0
            temps_initial = time.time()
            largeur_chiffre = 0.8


            singe = Singe()
            if presence_perroquet :
                perroquet = Perroquet()

            obstacles = []
            clock = 0
            caseclock = 0
            tick = True


            total_struct = []

            prochaine_struct = delai_struct
            structures = ["20002"]

            keys = pygame.key.get_pressed()
            left, up, right, q, d = keys[pygame.K_LEFT], keys[pygame.K_UP], keys[pygame.K_RIGHT], keys[pygame.K_q], keys[pygame.K_d]

            if accelerometre:
                dirSinge = "neutre"
                gyroSinge = ADXL345()   #main gauche = singe
                mvmSinge = False

            run = True
            while run: #Boucle de jeu
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False
                        partierun = False
                        menujrun = 0
                        menurun = False


                keys = pygame.key.get_pressed()

                if pautogui:
                    if keys[pygame.K_p] and not plein_ecran:
                        plein_ecran = True

                        taille = int(ecrany/(nlignes)) #Taille d'une case
                        margegauche = int((ecranx - ncolonnes*taille)/(2*taille))+1
                        margedroite = margegauche
                        dx = ecranx - (margegauche + ncolonnes + margedroite)*taille #Decalage de l'abcisse de tous les elements du jeu
                        fenx = taille*(margegauche + ncolonnes + margedroite)
                        feny = taille*nlignes
                        screen = pygame.display.set_mode([fenx, feny], pygame.FULLSCREEN)
                        chargeImages()

                    if keys[pygame.K_ESCAPE] and plein_ecran:
                        plein_ecran = False

                        taille = int(ecrany/(nlignes*2)) #Taille d'une case
                        margegauche = int((ecranx - ncolonnes*taille)/(4*taille))
                        margedroite = margegauche
                        dx = 0
                        fenx = taille*(margegauche + ncolonnes + margedroite)
                        feny = taille*nlignes
                        screen = pygame.display.set_mode([fenx, feny], 0)

                        chargeImages()


                #Gestion singe et perroquet
                if accelerometre:
                    axes = gyroSinge.getAxes(False)
                    #axe x : - vers + = avant vers arriere
                    #axe y : - vers + = droite vers gauche
                    if mvmSinge:
                        if (-3 <= axes["x"] <= 3) and (-3 <= axes["y"] <= 3):
                            mvmSinge = False
                    else:
                        #test mouvement vers la gauche
                        if axes["y"] >= 7:
                            dirSinge = "left"
                            mvmSinge = True
                        #test mouvement vers la droite
                        elif axes["y"] <= -7:
                            dirSinge = "right"
                            mvmSinge = True
                        #test mouvement vers la haut (saut)
                        elif axes["x"] >= 6:
                            dirSinge = "up"
                            mvmSinge = True

                        if not(dirSinge == "neutre"):
                            if dirSinge=="left":
                                singe.gauche()
                            elif dirSinge=="right":
                                singe.droite()
                            elif dirSinge=="up":
                                singe.haut()
                            dirSinge = "neutre"


                    if presence_perroquet :
                        q, d, preq, pred = keys[pygame.K_q], keys[pygame.K_d], q, d
                    if presence_perroquet :
                        if q and not preq:
                            perroquet.gauche()
                        if d and not pred:
                            perroquet.droite()

                else:
                    left, up, right, preleft, preup, preright = keys[pygame.K_LEFT], keys[pygame.K_UP], keys[pygame.K_RIGHT], left, up, right
                    if presence_perroquet :
                        q, d, preq, pred = keys[pygame.K_q], keys[pygame.K_d], q, d

                    if left and not preleft:
                        singe.gauche()
                    if right and not preright:
                        singe.droite()
                    if up:
                        singe.haut()
                    if presence_perroquet :
                        if q and not preq:
                            perroquet.gauche()
                        if d and not pred:
                            perroquet.droite()


                if presence_perroquet :
                    singe.accrochage()
                singe.visu()
                singe.saut()
                if presence_perroquet :
                    perroquet.visu()
                    perroquet.chute()

                #Gestion obstacles
                if score%ecartniv==0:
                    if menujrun==1:
                        if score//ecartniv<len(Lstruct1j):
                            total_struct += Lstruct1j[score//ecartniv]
                    elif menujrun==2:
                        if score//ecartniv<len(Lstruct2j):
                            total_struct += Lstruct2j[score//ecartniv]

                if tick:
                    if structures == []:
                        prochaine_struct -= 1
                    if prochaine_struct == 0:
                        prochaine_struct = delai_struct
                        structures += total_struct[randint(0,len(total_struct) - 1)]

                    apparitionObstacles()

                supprimer = []
                defaite = []
                for k in range(len(obstacles)):
                    if obstacles[k].defile():
                        supprimer += [k]
                    defaite += obstacles[k].contact()
                perdu(defaite)

                for k in supprimer[::-1]:
                    del obstacles[k]

                #Affichage
                fond()
                devant = []
                for k in range(len(obstacles)):
                    if obstacles[::-1][k].derriereSinge():
                        obstacles[::-1][k].affiche()
                    else:
                        devant += [k]
                if presence_perroquet :
                    perroquet.afficheOmbre() #L'ombre du perroquet est en dessous du singe
                singe.affiche()
                if presence_perroquet :
                    perroquet.affiche() #Le perroquet est au dessus du singe
                for k in devant: #Les piliers sont affichés devant les personnages s'ils ont une ordonnée plus grande
                    obstacles[::-1][k].affiche()
                gererScore()

                pygame.display.flip()

                time.sleep(0.01)
                tick = False
                clock += 1
                if clock%(1/vitesse) == 0:
                    caseclock += 1
                    tick = True


            #Gestion base de donnees
            Psd = pseudo1
            Mode = menujrun
            Score = score
            Aide = aide
            Obs = 0

            create_tables()
            update_Parties(Psd,Mode,Score,Aide,Obs)
            update_Calcul(Psd,Mode,Score,Aide,Obs)
            export_csv()

            histStats()
            modifCsvScore("Solo_score.csv")
            modifCsvScore("Duo_score.csv")
            modifCsvTemps("Solo_temps.csv")
            modifCsvTemps("Duo_temps.csv")


            #Menu si le joueur perd
            if partierun:
                clic = 0
                pygame.draw.rect(screen, (255, 255, 0), pygame.Rect((fenx-5*taille)/2, (feny-taille)/2, taille*2, taille))
                pygame.draw.rect(screen, (255, 0, 0), pygame.Rect((fenx+taille)/2, (feny-taille)/2, taille*2, taille))
                screen.blit(police.render("rejouer",False,(0,0,0)),((fenx-4.8*taille)/2, (feny-taille/2)/2))
                screen.blit(police.render("quitter",False,(0,0,0)),((fenx+taille*1.3)/2, (feny-taille/2)/2))
                pygame.display.flip()
                while clic==0:
                    ev = pygame.event.get()
                    for event in ev:
                        if event.type == pygame.QUIT:
                            clic = -1
                            partierun = False
                            menujrun = 0
                            menurun = False
                        if event.type==pygame.MOUSEBUTTONUP:
                            mx,my = pygame.mouse.get_pos()
                            if (fenx-5*taille)/2<mx and mx<(fenx-taille)/2 and (feny-taille)/2<my and my<(feny+taille)/2:
                                clic = 1 #Rejouer
                            if (fenx+taille)/2<mx and mx<(fenx+5*taille)/2 and (feny-taille)/2<my and my<(feny+taille)/2:
                                clic = 2 #Menu
                                partierun = False

C.close()
conn.close()

pygame.quit()
