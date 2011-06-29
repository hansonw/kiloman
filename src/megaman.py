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
	
#control for the main character

class MegaMan(Object):
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
		this.shots = []
		this.state = 'stand'
		this.hold = 0
		this.cooldown = 0
		this.midair = 0
		this.dir = 1
		this.hurt = 0
		this.hp = 19
		this.vy = 0
		this.x, this.y = x, y
		this.width, this.height = 32, 40
		this.speed = 4
		this.jump_speed = 8
		this.bullet_type = 'megaman'
		this.dy, this.dx = 0, 0
		
	def sprite(this):
		ret = pygame.sprite.Sprite()
		ret.image = this.anim[this.state].current_frame()
		ret.rect = pygame.Rect(this.x, this.y, ret.image.get_width(), ret.image.get_height())
		ret.mask = pygame.mask.from_surface(ret.image)
		return ret
		
	def intersect(this, sprite):
		if not this.sprite().rect.colliderect(sprite.rect):
			return 0
		return pygame.sprite.collide_rect(this.sprite(), sprite)
		
	def process(this, keys):
		this.dx = 0
		this.dy = 0
		this.cooldown -= 1
		
		#
		# Megaman is essentially a finite state automaton - each state has an animation, and 
		# actions allow you to go between states (e.g. stand -> stand_run transition -> run -> run_stand -> stand)
		#
		
		if this.hurt: this.hurt -= 1
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
		
		if keys[pygame.K_SPACE]:
			if this.hold == 0 and this.cooldown <= 0:
				xpos = this.x
				if this.dir == 1: xpos += 20
				ypos = this.y + 15
				if this.bullet_type == 'megamanu':
					ypos -= 3
				playsound('shot')
				this.shots.append(Projectile(this.bullet_type, xpos, ypos, this.dir*10, 0))
				this.hold = 1
				this.cooldown = 10
		else:
			this.hold = 0
		
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
				
		for shot in this.shots:
			if shot.state == 'dead':
				this.shots.remove(shot)
			else:
				shot.process()
		
	def change_state(this, newstate):
		this.anim[this.state].reset()
		this.state = newstate
	
	def move(this, dx, dy):
		this.x += dx
		this.y += dy
		this.dx += dx
		this.dy += dy
	
	def map_collide(this, map):
		#collide my projectiles
		for shot in this.shots:
			shot.map_collide(map)
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
		#invincible right now?
		if this.state == 'explode':
			return
		this.hp -= amt
		if this.hp <= 0:
			this.change_state('dead')
		playsound('hurt')
		this.hurt = 60
	
	def hit(this, enemy):
		for shot in this.shots:
			if shot.state == 'air' and enemy.intersect(shot.sprite()):
				shot.explode()
				#uranium = +1
				enemy.take_damage(1 + (this.bullet_type == 'megamanu'))
		
	def draw(this, screen):
		alpha = 255
		#blink when i'm injured
		if this.hurt/3%2 == 1:
			alpha = 125
		this.anim[this.state].draw(screen, this.x, this.y, this.dir == 1, alpha)
		for shot in this.shots:
			shot.draw(screen)
		hpbar = pygame.image.load('anims/health.png')
		hpbar.set_colorkey(hpbar.get_at((0,0)))
		hpnotch = pygame.image.load('anims/healthbar.png')
		hpnotch.set_colorkey(hpbar.get_at((0,0)))
		screen.blit(hpbar, (40, 40))
		cy = 99
		for i in range(this.hp):
			screen.blit(hpnotch, (41, cy))
			cy -= 3
			