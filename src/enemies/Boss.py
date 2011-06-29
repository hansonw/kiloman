import pygame, os
from math import *
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

class Boss(Enemy):
	def __init__(this, x=0, y=0):
		this.anim = {}
		this.anim['stand'] = Animation('boss_stand')
		this.anim['shoot'] = Animation('boss_shoot')
		this.anim['explode'] = Animation('explosion')
		this.anim['dead'] = Animation('empty')
		this.state = 'stand'
		this.cooldown = 0
		this.hurt = 0
		this.midair = 0
		this.angle = 0
		this.dir = 1
		this.ydir = 3
		this.hp = 20
		this.vy = 0
		this.shots = []
		this.x, this.y = x, y-8
		this.width, this.height = 132, 158
		this.speed = 2
		this.points = 1000
		this.jump_speed = 7
		this.dy, this.dx = 0, 0
	def process(this, keys):
		this.dx = 0
		this.dy = 0
		this.angle += 0.05
		if this.hurt: this.hurt -= 1
		if this.state == 'explode':
			this.anim[this.state].step()
			if this.anim[this.state].iter == 1:
				this.change_state('dead')
			return
				
		this.move(0, this.ydir / ((this.state=='shoot')+1))		
		this.anim[this.state].step()
		
		if this.state == 'shoot' and this.anim['shoot'].subframe == 0:
			xpos = this.x + 64
			ypos = this.y + 64
			for i in range(-this.anim['shoot'].frame, 10, 2):
				this.shots.append(Projectile('megaman', xpos, ypos, -3, i))

		for shot in this.shots:
			if shot.state == 'dead':
				this.shots.remove(shot)
			else:
				shot.process()

		if this.state == 'stand' and this.anim['stand'].iter == 1:
			this.change_state('shoot')
		if this.state == 'shoot' and this.anim['shoot'].iter == 1:
			this.change_state('stand')
		
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
							this.ydir *= -1
		return collide
		
	def take_damage(this, amt):
		if this.state == 'stand':
			return
		if this.state == 'explode':
			return
		playsound('hit')
		this.hp -= amt
		this.hurt = 60
		if this.hp <= 0:
			playsound('enemydie')
			this.change_state('explode')
		
	def hit(this, megaman):
		if this.intersect(megaman.sprite()):
			megaman.take_damage(9)
		for shot in this.shots:
			if shot.state == 'air' and megaman.intersect(shot.sprite()):
				shot.explode()
				megaman.take_damage(2)
	def draw(this, screen, offx=0, offy=0):
		alpha = 255
		if this.hurt/3%2 == 1:
			alpha = 125
		this.anim[this.state].draw(screen, this.x+offx, this.y+sin(this.angle)+offy, this.dir == 1, alpha)
		for shot in this.shots:
			shot.draw(screen)