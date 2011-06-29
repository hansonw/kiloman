import pygame

from object import *
from animation import *
from map import *
from sound import *

class Projectile(Object):
	def __init__(this, type, x, y, vx, vy):
		this.x, this.y = x, y 
		this.vx, this.vy = vx, vy
		this.anim = {}
		this.anim['air'] = Animation('projectiles/' + type + '_air')
		this.anim['explode'] = Animation('projectiles/' + type + '_explode')
		this.anim['dead'] = this.anim['air']
		this.state = 'air'
		
	def process(this):
		this.x += this.vx
		this.y += this.vy
		this.anim[this.state].step()
		if this.state == 'explode' and this.anim[this.state].iter == 1:
			this.change_state('dead')
		if this.x < -32 or this.x > 670 or this.y < -32 or this.y > 670:
			this.change_state('dead')
			
	def draw(this, screen):
		if this.state != 'dead':
			this.anim[this.state].draw(screen, this.x, this.y)
		
	def change_state(this, newstate):
		this.anim[this.state].reset()
		this.state = newstate
	
	def explode(this):
		this.change_state('explode')
		this.vx, this.vy = 0, 0
	
	def sprite(this):
		ret = pygame.sprite.Sprite()
		ret.image = this.anim[this.state].current_frame()
		ret.rect = pygame.Rect(this.x, this.y, ret.image.get_width(), ret.image.get_height())
		ret.mask = pygame.mask.from_surface(ret.image)
		return ret
	
	def map_collide(this, map):
		if this.state != 'air':
			return
		grid = map.current_area().grid
		my_rect = pygame.Rect(this.x, this.y, this.anim[this.state].width, this.anim[this.state].height)
		for y, row in enumerate(grid):
			for x, ch in enumerate(row):
				if ch in map.current_area().tile:
					tile = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
					if tile.colliderect(my_rect):
						this.explode()
						playsound('tink')
						return