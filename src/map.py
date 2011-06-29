import pygame
from config import *
from string import *
from enemy import *

class Tile:
	def __init__(this, ch = ''):
		this.type = ch

#Areas are 16x12 grids
#Types of tiles:
	#A-F: links to other areas (the screen slides)
	#.: empty, shows background
	#other characters: defineable tiles
class Area:
	def __init__(this, name, grid, tile, neigh):
		this.grid = grid
		for row in grid: print row
		print ''
		this.name = name
		this.tile = {}
		this.neigh = neigh
		print this.neigh
		this.offx = 0
		this.offy = 0
		for letter, image in tile.iteritems():
			if letter < '0' or letter > '9':
				this.tile[letter] = pygame.image.load('maps/%s' % image)
		if not 'bg' in this.tile:
			this.tile['bg'] = pygame.Surface((0,0))
			
		this.enemies = []
		for y, row in enumerate(this.grid):
			for x, ch in enumerate(row):
				if ch >= '0' and ch <= '9':
					temp = __import__(tile[ch], globals(), locals(), [], -1)
					this.enemies.append(eval('temp.%s(%d, %d)' % (tile[ch], x*TILE_SIZE, y*TILE_SIZE)))
	
	def neighbor(this, dx, dy):
		return this.neigh[(-dx+1)/2+(-dy+1)/2+abs(dy)*2]
	
	def shift_bg(this, dx, dy):
		this.offx += dx
		this.offy += dy
		this.offx %= this.tile['bg'].get_width()
		this.offy %= this.tile['bg'].get_height()
		if this.offx > 0: this.offx -= this.tile['bg'].get_width()
		if this.offy > 0: this.offy -= this.tile['bg'].get_height()
	
	def draw(this, screen, offx=0, offy=0):
		cx = int(this.offx)
		while cx < 640:
			cy = int(this.offy)
			while cy < 480:
				screen.blit(this.tile['bg'], (cx+offx, cy+offy))
				cy += this.tile['bg'].get_height()
			cx += this.tile['bg'].get_width()
		for y, row in enumerate(this.grid):
			for x, ch in enumerate(row):
				if ch in this.tile:
					screen.blit(this.tile[ch], (x*TILE_SIZE+offx, y*TILE_SIZE+offy))

#Maps are a collection of linked areas
class Map:
	def __init__(this, name = ''):
		this.areas = []
		this.cur_area = 0
		f = open('maps/' + name + '.txt', 'r')
		try: #read until EOF
			while 1:
				area = strip(f.readline())
				if area == '': break
				grid = [strip(f.readline(), "\n") for i in range(480/TILE_SIZE)]
				neigh = map(strip, f.readline().split(','))
				tile = {}
				while 1:
					s = f.readline()
					if s.find('=') == -1: break
					s = map(strip, s.split('='))
					tile[s[0]] = s[1]
				this.areas.append(Area(area, grid, tile, neigh))
		except IOError:
			pass
				
	def start_pos(this):
		for row_num, row in enumerate(this.areas[0].grid):
			if row.find('S') != -1:
				return (row.find('S'), row_num)
		return (-1, -1)
		
	def current_area(this):
		return this.areas[this.cur_area]
	
	def draw(this, screen):
		this.current_area().draw(screen)
		
	def shift_bg(this, dx, dy):
		this.current_area().shift_bg(dx, dy)
		
	def enemies(this):
		return this.current_area().enemies