import pygame
import random

pygame.init()

screen_width = 800
screen_height = 800

bg = pygame.image.load('assets/starbg.png')
rocket = pygame.image.load('assets/spaceRocket.png')
asteroid50 = pygame.image.load('assets/asteroid50.png')
asteroid100 = pygame.image.load('assets/asteroid100.png')
asteroid150 = pygame.image.load('assets/asteroid150.png')

pygame.display.set_caption("Asteroid")
screen = pygame.display.set_mode((screen_width, screen_height))

clock = pygame.time.Clock()

gameover = False

class Player:
  def __init__(self):
    self.img = rocket
    self.width = self.img.get_width()
    self.height = self.img.get_height()
    self.x = screen_width // 2
    self.y = screen_height // 2
    self.rR = min(self.width, self.height) * 0.35

  def draw(self, screen):
    screen.blit(self.img, [self.x, self.y, self.width, self.height])

  def movement(self):
    speed = 4
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] or keys[pygame.K_UP]:
      self.y -= speed
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
      self.y += speed
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
      self.x += speed
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
      self.x -= speed
    
    # Clamping
    self.x = max(0, min(self.x, screen_width - self.width))
    self.y = max(0, min(self.y, screen_height - self.height))

class Asteroid:
  def __init__(self, rank):
    self.rank = rank
    if self.rank == 1:
      self.image = asteroid50
    elif self.rank == 2:
      self.image = asteroid100
    else:
      self.image = asteroid150
    
    self.width = 50 * rank
    self.height = 50 * rank
    self.r = self.width // 2

    self.x, self.y, self.edge = self.spawn_at_edge()

    self.vx, self.vy = self.set_velocity()

  def spawn_at_edge(self):
    edge = random.choice(["top", "bottom" ,"left", "right"])

    if edge == "top":
      x = random.uniform(0, screen_width - self.width)
      y = -self.height
    elif edge == "bottom":
      x = random.uniform(0, screen_width - self.width)
      y = screen_height
    elif edge == "left":
      x = -self.width
      y = random.uniform(0, screen_height - self.height)
    else:
      x = screen_width
      y = random.uniform(0, screen_height - self.height)

    return x,y,edge

  def set_velocity(self):
    main_speed = random.uniform(2,4)
    side_speed = random.uniform(-1.5, 1.5)

    if self.edge == "top":
      vy = main_speed
      vx = side_speed
    elif self.edge == "bottom":
      vy = -main_speed
      vx = side_speed
    elif self.edge == "left":
      vy = side_speed
      vx = main_speed
    else:
      vy = side_speed
      vx = -main_speed
    
    return vx,vy
  
  def update(self):
    self.x += self.vx
    self.y += self.vy

  def draw(self, screen):
    screen.blit(self.image, (int(self.x), int(self.y)))
  
  def is_off_screen(self,margin=100):
    if self.x < -self.width - margin or self.x > screen_width + margin or self.y < -self.height - margin or self.y > screen_height + margin:
      return True
    else:
      return False

class Bullet:
  def __init__(self,bx,by):
    self.x = bx
    self.y = by
    self.vy = -5
    self.r = 2

  def update(self):
    self.y += self.vy
  
  def draw(self, screen):
    pygame.draw.circle(screen, (255,255,255), (self.x, self.y), self.r)
  
  def is_off_screen(self,margin=100):
    if self.y < -margin:
      return True
    return False

def redrawGameWindow():
  screen.blit(bg,(0,0))
  font = pygame.font.Font(None, 36)

  for ast in asteroids:
    ast.draw(screen)
  
  if gameover == True:
    text_surface = font.render(f"GAME OVER — press R to restart", True, (255, 255, 255))
    show_score = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(text_surface, (200,400))
    screen.blit(show_score, (330,430))
  else:
    player.draw(screen)
    score_text = font.render(f"Score: {score}", True, (255,255,255))
    screen.blit(score_text, (20,20))
    for bullet in bullets:
      bullet.draw(screen)

  pygame.display.update()


def collides(x1, y1, r1, x2, y2, r2):
  dx = x1 - x2
  dy = y1 - y2

  if dx*dx + dy*dy < (r1 + r2)**2:
    return True

  return False

# Main loop
asteroids = []
bullets = []
spawn_timer = 0
player = Player()
run = True
score = 0
shoot_cooldown = 0

while run:
  clock.tick(60)
  bullets_to_remove = set()
  asteroids_to_remove = set()

  if not gameover:
    player.movement()
    if shoot_cooldown > 0 : shoot_cooldown -= 1

  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      run = False
    elif event.type == pygame.KEYDOWN and gameover == True:
      if event.key == pygame.K_r:
          player = Player()
          asteroids = []
          spawn_timer = 0
          gameover = False
          score = 0
    elif event.type == pygame.KEYDOWN and shoot_cooldown <= 0:
      if event.key == pygame.K_SPACE:
        bx = player.x + player.width / 2
        by = player.y

        bullets.append(Bullet(bx,by))
        shoot_cooldown = 15

  spawn_timer += 1

  if spawn_timer >= 45:
    rank = random.randint(1,3)
    asteroids.append(Asteroid(rank))
    spawn_timer = 0

  for ast in asteroids: ast.update()
  asteroids = [ast for ast in asteroids if not ast.is_off_screen()]

  for ast in asteroids:
    if collides(player.x + player.width/2, player.y + player.height/2, player.rR, ast.x + ast.width/2, ast.y + ast.height/2, ast.r) == True:
      gameover = True
    
    for b in bullets:
      if collides(b.x, b.y, b.r, ast.x + ast.width/2, ast.y + ast.height/2, ast.r) == True:
        bullets_to_remove.add(b)
        asteroids_to_remove.add(ast)
        score += ast.rank
        break

  bullets = [b for b in bullets if b not in bullets_to_remove]
  asteroids = [a for a in asteroids if a not in asteroids_to_remove]

  for bullet in bullets: bullet.update()
  bullets = [b for b in bullets if not b.is_off_screen()]

  redrawGameWindow()

pygame.quit()