import pygame, os
from config import *
from map import *
from animation import *
from object import *
from projectile import *

def between(x, a, b):
	return x >= a and x <= b
def absmin(a, b):
	if abs(a) < abs(b): return a
	return b

class Grass(Enemy):
	def __init__(this, x=0, y=0):
		this.anim = {}
		this.image = pygame.image.load('maps/grass.png')
		this.image.set_colorkey(this.image.get_at((0,0)))
		this.x, this.y = x, y
		this.hurt = 0
		this.state = 'vegetative'
		
	def draw(this, screen, dx=0, dy=0): screen.blit(this.image, (this.x+dx,this.y+dy))
	def process(this, keys): pass
	def take_damage(this, amt): pass
	def map_collide(this, map): pass
	def intersect(this, sprite): pass
	def hit(this, megaman): pass
	