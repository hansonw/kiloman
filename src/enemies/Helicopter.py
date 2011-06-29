import pygame, os
from config import *
from math import *
from map import *
from animation import *
from object import *
from projectile import *

def between(x, a, b):
	return x >= a and x <= b
def absmin(a, b):
	if abs(a) < abs(b): return a
	return b

class Helicopter(Enemy):
	def __init__(this, x=0, y=0):
		this.anim = {}
		this.anim['stand'] = Animation('helicopter')
		this.anim['explode'] = Animation('explosion')
		this.anim['dead'] = Animation('empty')
		this.state = 'stand'
		this.hurt = 0
		this.dir = 1
		this.hp = 5
		this.points = 150
		this.vx = 0
		this.vy = 0
		this.x, this.y = x, y
		this.width, this.height = 38, 30
		this.speed = 2
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
				
		this.anim[this.state].step()
		this.move(this.vx, 0)
		this.move(0, this.vy)
		
	def change_state(this, newstate):
		this.anim[this.state].reset()
		this.state = newstate
	
	def move(this, dx, dy):
		this.x += dx
		this.y += dy
		this.dx += dx
		this.dy += dy
	
	def map_collide(this, map):
		#I can go through anything! haha
		return
		
	def take_damage(this, amt):
		print amt
		if this.state == 'explode':
			return
		playsound('hit')
		this.hp -= amt
		this.hurt = 60
		if this.hp <= 0:
			playsound('enemydie')
			this.change_state('explode')
		
	def target(this, megaman):
		dx = megaman.x - this.x
		dy = megaman.y - this.y
		mag = sqrt(dx*dx + dy*dy)
		if mag == 0: mag = 10
		dx /= mag
		dy /= mag
		this.vx = dx*2
		this.vy = dy*2
		
	def hit(this, megaman):
		if this.intersect(megaman.sprite()):
			megaman.take_damage(5)