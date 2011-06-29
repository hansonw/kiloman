import pygame, config, os, sys
from megaman import *
from map import *
from sound import *

sys.path.append('enemies')

config = config.Config()
pygame.init()
initsound()

screen = pygame.display.set_mode((config.screen))
pygame.display.set_caption("Game")

keys = [0 for i in range(500)]
def processEvent(event):
	if event.type == pygame.KEYDOWN:
		keys[event.key] = 1
	elif event.type == pygame.KEYUP:
		keys[event.key] = 0
	elif event.type == pygame.QUIT:
		exit()

#
# INTRO SCREEN
#
bg = pygame.image.load('intro.png')
fg = pygame.image.load('introfg.png')
st = pygame.image.load('introtext.png')
cnt = 0
while 1:
	for event in pygame.event.get():
		processEvent(event)
	if keys[pygame.K_RETURN]:
		break
		
	screen.blit(bg, (0,0))
	screen.blit(fg, (0,0))
	
	if cnt % 10 < 5:
		screen.blit(st, (0,0))
	cnt += 1
	
	pygame.time.Clock().tick(60)
	pygame.display.flip()

#
# MAIN GAME LOOP
#
	
levels = ['level1', 'level2']
clock = pygame.time.Clock()

for level in levels:
	map = Map(level)
	start_pos = map.start_pos()
	megaman = MegaMan(start_pos[0]*TILE_SIZE, start_pos[1]*TILE_SIZE-8)
	if level == 'level2': megaman.bullet_type = 'megamanu'
	
	def sgn(a):
		if a < 0: return -1
		return a != 0
	
	score = 0
	slidex, slidey = 0, 0
	cdx, cdy = 0, 0
	next_area = -1
	while 1:
		for event in pygame.event.get():
			processEvent(event)
		
		if megaman.state == 'dead':
			break
		
		#level complete? (last area)
		if map.current_area().name == 'area5':
			break
		if map.current_area().name == 'area4' and len(map.enemies()) == 0:
			break
		
		screen.fill((255,255,255))
		
		#slidex, slidey are for scrolling
		if slidex or slidey:
			map.current_area().draw(screen, cdx, cdy)
			map.areas[next_area].draw(screen, -slidex, -slidey)
			megaman.draw(screen)
			megaman.x += sgn(slidex)*8
			megaman.y += sgn(slidey)*8
			megaman.shots = []
			cdx += sgn(slidex)*8
			cdy += sgn(slidey)*8
			slidex -= sgn(slidex)*8
			slidey -= sgn(slidey)*8
			for enemy in map.enemies():
				enemy.draw(screen, cdx, cdy)
				try: #hack: remove shots if they exist
					enemy.shots = []
				except:
					pass
			for enemy in map.areas[next_area].enemies:
				enemy.draw(screen, -slidex, -slidey)
			if slidex == 0 and slidey == 0:
				map.cur_area = next_area
				cdx, cdy = 0, 0
		else:
			map.draw(screen)
			
			megaman.process(keys)
			megaman.map_collide(map)
			megaman.draw(screen)
			
			#did megaman go off the screen? I might need to scroll
			x, y = megaman.x, megaman.y
			x1, y1 = megaman.x + 34, megaman.y + 40
			if x < 0 or x1 > 640 or y < 0 or y1 > 480:
				if x < 0:
					slidex = 640
					megaman.x = -34
				if x1 > 640:
					slidex = -640
					megaman.x = 640
				if y < 0:
					slidey = 480
					megaman.y = 0
				if y1 > 480:
					slidey = -480
					megaman.y = 480
				
				next_area = map.current_area().neighbor(slidex/640, slidey/480)
				print next_area
				found = 0
				for i, area in enumerate(map.areas):
					if area.name == next_area:
						next_area = i
						found = 1
						break
				if not found: #don't let him get off the screen
					slidex = 0
					slidey = 0
					megaman.x = max(megaman.x, 0)
					megaman.x = min(megaman.x, 640-megaman.width)
			
			for enemy in map.enemies():
				megaman.hit(enemy)
				if enemy.state == 'dead':
					map.enemies().remove(enemy)
					score += enemy.points
				else:
					enemy.process(keys)
					enemy.map_collide(map)
					enemy.target(megaman)
					if not megaman.hurt:
						enemy.hit(megaman)
					enemy.draw(screen)
			
			#Uncomment the next line to enable shifting of the background.. it's pretty cool
			#map.shift_bg(megaman.dx/-20.0, megaman.dy/-20.0)
		
		font = pygame.font.Font(pygame.font.match_font('Verdana'), 12)
		text = font.render('Score: ' + str(score), True, (255,255,255))
		screen.blit(text, (70, 50))
		
		#May not be necessary on your computer - try it without if it's too slow
		clock.tick(60)
		pygame.display.flip()
	
	if megaman.hp <= 0:
		#
		# LOSING SCREEN
		#
	
		while 1:
			for event in pygame.event.get():
				processEvent(event)
			if keys[pygame.K_RETURN]:
				break
			screen.blit(bg, (0,0))
			font = pygame.font.Font(pygame.font.match_font('Verdana'), 20)
			text = font.render("You lost the game. Sorry! Press enter to exit.", 1, (255,255,255))
			screen.blit(text, (70, 50))
			pygame.display.flip()
		exit()
	else:
		bscore = score
	hpbonus = megaman.hp*50
	
	#
	# WINNING SCREEN
	#
	
	while 1:
			for event in pygame.event.get():
				processEvent(event)
			if keys[pygame.K_RETURN]:
				break
			screen.blit(bg, (0,0))
			font = pygame.font.Font(pygame.font.match_font('Verdana'), 20)
			text = font.render("STAGE CLEAR", 1, (255,255,255))
			screen.blit(text, (70, 50))
			text = font.render("Base score: %d" % bscore, 1, (255,255,255))
			screen.blit(text, (70, 70))
			text = font.render("HP Bonus: %d" % hpbonus, 1, (255,255,255))
			if hpbonus:
				score += 1
				hpbonus -= 1
			screen.blit(text, (70, 90))
			text = font.render("Your final score: %d" % score, 1, (255,255,255))
			screen.blit(text, (70, 110))
			if level == 'level1':
				text = font.render("UPGRADE: Uranium-enriched bullets!", 1, (255,255,255))
				screen.blit(text, (70, 150))
			text = font.render("Press enter to continue to the next stage.", 1, (255,255,255))
			screen.blit(text, (70, 170))
			clock.tick(200)
			pygame.display.flip()

#keyup not quite registered yet...
keys[pygame.K_RETURN] = 0

while 1:
		for event in pygame.event.get():
			processEvent(event)
		if keys[pygame.K_RETURN]:
			break
		screen.blit(bg, (0,0))
		font = pygame.font.Font(pygame.font.match_font('Verdana'), 20)
		text = font.render("You won the game! Congratulations!", 1, (255,255,255))
		screen.blit(text, (70, 50))
		clock.tick(200)
		pygame.display.flip()