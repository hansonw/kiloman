import pygame
from string import *

class Animation:
	def __init__(this, file = ''):
		this.frames = []
		this.frame = 0
		this.subframe = 0
		this.width = 0
		this.iter = 0
		if file != '':
			f = open('anims/' + file + '.txt', "r")
			imagefile = f.readline().strip()
			this.duration = int(f.readline())
			this.width, this.height = map(int, f.readline().split())
			positions = map(int, map(strip, f.readline().split(",")))
			widths = map(int, map(strip, f.readline().split(",")))
			img = pygame.image.load('anims/' + imagefile)
			height = img.get_height()
			for pos, width in zip(positions, widths):
				sub = pygame.Surface((width, height))
				sub.blit(img, (0,0), (pos,0,width,height))
				sub.set_colorkey(sub.get_at((0,0)))
				this.frames.append(sub)
	
	def reset(this):
		this.frame = 0
		this.subframe = 0
		this.iter = 0
	
	def step(this):
		this.subframe += 1
		if this.subframe == this.duration:
			this.subframe = 0
			this.frame = (this.frame+1) % len(this.frames)
		if this.frame+this.subframe == 0:
			this.iter += 1
	
	def current_frame(this):
		return this.frames[this.frame]
			
	def draw(this, screen, x, y, flip=0, alpha=255):
		this.frames[this.frame].set_alpha(alpha)
		if flip:
			frame = pygame.transform.flip(this.frames[this.frame], 1, 0)
			screen.blit(frame, (x+this.width-frame.get_width(),y))
		else:
			screen.blit(this.frames[this.frame], (x,y))