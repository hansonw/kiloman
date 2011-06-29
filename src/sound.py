import pygame

sounds = {}

def initsound():
	pygame.mixer.init(44100, -16, 2, 1024)
	s = ['hit', 'hurt', 'die', 'shot', 'tink', 'enemydie']
	for sound in s:
		sounds[sound] = pygame.mixer.Sound('sounds/' + sound + '.wav')

def playsound(soundfile):
	sounds[soundfile].play()