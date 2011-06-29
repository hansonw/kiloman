import pygame

from animation import *
from projectile import *
from map import *
from object import *

#base enemy class - supplies basic functions

class Enemy:
	def __init__():
		this.x, this.y = 0, 0
		this.anim = {}
		this.state = ''
		
	def sprite(this):
		ret = pygame.sprite.Sprite()
		ret.image = this.anim[this.state].current_frame()
		if this.dir == 1: ret.image = pygame.transform.flip(ret.image, 1, 0)
		ret.rect = pygame.Rect(this.x, this.y, ret.image.get_width(), ret.image.get_height())
		ret.mask = pygame.mask.from_surface(ret.image)
		return ret
		
	def intersect(this, sprite):
		if not this.sprite().rect.colliderect(sprite.rect):
			return 0
		return pygame.sprite.collide_mask(this.sprite(), sprite)
	
	def target(this, megaman):
		return
	
	def draw(this, screen, offx=0, offy=0):
		alpha = 255
		if this.hurt/3%2 == 1:
			alpha = 125
		this.anim[this.state].draw(screen, this.x+offx, this.y+offy, this.dir == 1, alpha)