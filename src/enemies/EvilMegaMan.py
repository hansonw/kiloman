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

class Robot(Enemy):
	def __init__(this, x=0, y=0):
		this.anim = {}
		this.anim['run'] = Animation('megaman_run')
		this.anim['stand'] = Animation('megaman_stand')
		this.anim['run_stand'] = Animation('megaman_run_stand')
		this.anim['stand_run'] = Animation('megaman_stand_run')
		this.anim['jump'] = Animation('megaman_jump')
		this.anim['midair'] = Animation('megaman_midair')
		this.anim['explode'] = Animation('explosion')
		this.anim['dead'] = Animation('empty')
		this.state = 'stand'
		this.cooldown = 0
		this.midair = 0
		this.dir = 1
		this.hp = 5
		this.vy = 0
		this.x, this.y = x, y-8
		this.width, this.height = 32, 40
		this.speed = 2
		this.jump_speed = 7
		this.dy, this.dx = 0, 0
	def process(this, keys):
		this.dx = 0
		this.dy = 0
		if this.state == 'explode':
			this.anim[this.state].step()
			if this.anim[this.state].iter == 1:
				this.change_state('dead')
			return
		
		if keys[pygame.K_LEFT]:
			if this.dir == 1:
				if this.state == 'stand_run' or this.state == 'run_stand':
					this.change_state('run') #smoother motion
			this.dir = -1
			this.move(-this.speed, 0)
			if this.state == 'stand':
				this.change_state('stand_run')
		elif keys[pygame.K_RIGHT]:
			if this.dir == 1:
				if this.state == 'stand_run' or this.state == 'run_stand':
					this.change_state('run') #smoother motion
			this.dir = 1
			this.move(this.speed, 0)
			if this.state == 'stand':
				this.change_state('stand_run')
		else:
			if this.state == 'run':
				this.change_state('run_stand')
			elif this.state == 'stand_run':
				this.change_state('stand')
		
		if keys[pygame.K_UP]: 
			if this.state != 'jump' and this.state != 'midair':
				this.change_state('jump')
				this.midair = 1
				this.vy = -this.jump_speed
				
		this.anim[this.state].step()
		if this.anim[this.state].iter == 1:
			if this.state == 'run_stand':
				this.change_state('stand')
			elif this.state == 'stand_run':
				this.change_state('run')
			elif this.state == 'jump':
				this.change_state('midair')
		this.move(0, this.vy)
		if this.midair:
			if this.vy < TERMINAL_VELOCITY:
				this.vy += GRAVITY
		
	def change_state(this, newstate):
		this.anim[this.state].reset()
		this.state = newstate
	
	def move(this, dx, dy):
		this.x += dx
		this.y += dy
		this.dx += dx
		this.dy += dy
	
	def map_collide(this, map):
		#check if i'm touching any of the map tiles
		grid = map.current_area().grid
		collide, grounded = 0, 0
		#print this.x, this.y, this.state
		for y, row in enumerate(grid):
			for x, ch in enumerate(row):
				if ch in map.current_area().tile:
					my_rect = pygame.Rect(this.x, this.y, this.width, this.height)
					my_rectd = pygame.Rect(this.x, this.y+1, this.width, this.height)
					my_rectx = pygame.Rect(this.x, this.y-this.dy, this.width, this.height) #I only move X
					my_recty = pygame.Rect(this.x-this.dx, this.y, this.width, this.height) #I only move Y
					tile = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
					if tile.colliderect(my_rect):
						#os.system("pause")
						#print x, y
						#print this.dx, this.dy
						collide = 1
						#which one caused the collision?
						if tile.colliderect(my_rectx):
							this.x += absmin(x*TILE_SIZE-this.x-this.width, (x+1)*TILE_SIZE-this.x)
						if tile.colliderect(my_recty):
							this.y += absmin(y*TILE_SIZE-this.y-this.height, (y+1)*TILE_SIZE-this.y)
							this.vy = 0
							if this.y+this.height == y*TILE_SIZE:
								this.change_state("stand")
								this.midair = 0
					if tile.colliderect(my_rectd):
						grounded = 1
		if not (collide or grounded):
			this.change_state("midair")
			this.midair = 1
		return collide
		
	def take_damage(this, amt):
		this.hp -= amt
		if this.hp <= 0:
			this.change_state('explode')
		
	def hit(this, megaman):
		x = 1
		
	def draw(this, screen):
		this.anim[this.state].draw(screen, this.x, this.y, this.dir == 1)