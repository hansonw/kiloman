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

class Hopper(Enemy):
	def __init__(this, x=0, y=0):
		this.anim = {}
		this.anim['stand'] = Animation('hopper_stand')
		this.anim['jump'] = Animation('hopper_jump')
		this.anim['explode'] = Animation('explosion')
		this.anim['dead'] = Animation('empty')
		this.state = 'stand'
		this.cooldown = 0
		this.hurt = 0
		this.midair = 0
		this.dir = -1
		this.hp = 3
		this.vy = 0
		this.points = 100
		this.x, this.y = x, y+39
		this.width, this.height = 30, 25
		this.speed = 5
		this.jump_speed = 7
		this.dy, this.dx = 0, 0
	def process(this, keys):
		this.dx = 0
		this.dy = 0
		if this.hurt: this.hurt -= 1
		if this.state == 'explode':
			this.anim[this.state].step()
			if this.anim[this.state].iter == 1:
				this.change_state('dead')
			return
		
		this.move(this.dir, 0)
		
		if this.state == 'stand' and this.anim['stand'].iter == 1:
			this.vy = -10
			this.change_state('jump')
		if this.state == 'jump' and this.anim['jump'].iter == 1:
			this.change_state('stand')
				
		this.anim[this.state].step()
		this.move(0, this.vy)
		if this.state == 'jump' or this.midair:
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
							this.dir *= -1
						if tile.colliderect(my_recty):
							this.y += absmin(y*TILE_SIZE-this.y-this.height, (y+1)*TILE_SIZE-this.y)
							this.vy = 0
							if this.y+this.height == y*TILE_SIZE:
								this.change_state("stand")
								this.midair = 0
					if tile.colliderect(my_rectd):
						grounded = 1
		
		if not (collide or grounded):
			this.midair = 1
		
		return collide
		
	def take_damage(this, amt):
		if this.state == 'explode':
			return
		playsound('hit')
		print amt, this.hp
		this.hp -= amt
		this.hurt = 60
		if this.hp <= 0:
			playsound('enemydie')
			this.change_state('explode')
		
	def hit(this, megaman):
		if megaman.x < this.x: this.dir = -1
		else: this.dir = 1
		if this.intersect(megaman.sprite()):
			megaman.take_damage(2)