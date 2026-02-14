import pygame
import sys
import random
import os
import wave
import math

# Street Fight MVP with combos, blocking, enemy waves, simple generated sounds
# Controls: A/D or left/right arrows to move, J to attack, K to block, W/space or up to jump

WIDTH, HEIGHT = 900, 480
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER_COLOR = (50, 150, 255)
ENEMY_COLOR = (200, 50, 50)
RANGED_COLOR = (180, 100, 40)
FLOOR_COLOR = (70, 70, 70)
ATTACK_COLOR = (255, 200, 0)
PROJECTILE_COLOR = (255, 120, 0)

GRAVITY = 0.8
PLAYER_SPEED = 4.5
JUMP_VELOCITY = -12

PLAYER_MAX_HEALTH = 14
ENEMY_MAX_HEALTH = 8
RANGED_MAX_HEALTH = 5
BASE_ATTACK_DAMAGE = 3
ENEMY_DAMAGE = 2
ATTACK_COOLDOWN = 0.22  # seconds between allowed attacks (faster)
ATTACK_DURATION = 0.12
COMBO_WINDOW = 0.35  # time allowed between presses to chain combos

ATTACK_SOUND = '.tmp/sounds/attack.wav'
HIT_SOUND = '.tmp/sounds/hit.wav'


def ensure_sounds():
    os.makedirs('.tmp/sounds', exist_ok=True)
    def make_tone(path, freq=440, duration=0.12, volume=0.3):
        if os.path.exists(path):
            return
        frate = 44100
        amp = int(32767 * volume)
        nframes = int(duration * frate)
        with wave.open(path, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(frate)
            for i in range(nframes):
                t = float(i) / frate
                val = int(amp * math.sin(2.0 * math.pi * freq * t))
                wf.writeframesraw(val.to_bytes(2, byteorder='little', signed=True))
    try:
        make_tone(ATTACK_SOUND, freq=760, duration=0.10, volume=0.35)
        make_tone(HIT_SOUND, freq=220, duration=0.12, volume=0.4)
    except Exception:
        pass


class Fighter:
    def __init__(self, x, y, w, h, color, max_health):
        self.rect = pygame.Rect(x, y, w, h)
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.color = color
        self.max_health = max_health
        self.health = max_health
        self.facing = 1
        self.invuln_timer = 0

    def apply_gravity(self):
        self.vy += GRAVITY
        if self.vy > 20:
            self.vy = 20

    def update(self, platforms):
        self.apply_gravity()
        self.rect.x += int(self.vx)
        self.collide(self.vx, 0, platforms)
        self.rect.y += int(self.vy)
        self.on_ground = False
        self.collide(0, self.vy, platforms)
        if self.invuln_timer > 0:
            self.invuln_timer -= 1.0 / FPS

    def collide(self, vx, vy, platforms):
        for p in platforms:
            if self.rect.colliderect(p):
                if vy > 0:
                    self.rect.bottom = p.top
                    self.vy = 0
                    self.on_ground = True
                elif vy < 0:
                    self.rect.top = p.bottom
                    self.vy = 0
                if vx > 0:
                    self.rect.right = p.left
                elif vx < 0:
                    self.rect.left = p.right

    def draw(self, surf):
        pygame.draw.rect(surf, self.color, self.rect)

    def take_damage(self, amount):
        if self.invuln_timer <= 0:
            self.health -= amount
            self.invuln_timer = 0.4


class Player(Fighter):
    def __init__(self, x, y):
        super().__init__(x, y, 42, 64, PLAYER_COLOR, PLAYER_MAX_HEALTH)
        self.attack_cooldown = 0
        self.attack_timer = 0
        self.combo_stage = 0
        self.combo_timer = 0
        self.blocking = False

    def attack(self):
        if self.attack_cooldown <= 0:
            # chain combos
            now_chain = 1
            if self.combo_timer > 0:
                self.combo_stage = min(3, self.combo_stage + 1)
            else:
                self.combo_stage = 1
            self.combo_timer = COMBO_WINDOW
            self.attack_timer = ATTACK_DURATION
            self.attack_cooldown = ATTACK_COOLDOWN

    def update(self, platforms):
        super().update(platforms)
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1.0 / FPS
        if self.attack_timer > 0:
            self.attack_timer -= 1.0 / FPS
        if self.combo_timer > 0:
            self.combo_timer -= 1.0 / FPS
        else:
            self.combo_stage = 0

    def get_attack_rect(self):
        if self.attack_timer > 0:
            length = 22 + 8 * self.combo_stage
            if self.facing >= 0:
                return pygame.Rect(self.rect.right, self.rect.top + 8, length, self.rect.height - 16)
            else:
                return pygame.Rect(self.rect.left - length, self.rect.top + 8, length, self.rect.height - 16)
        return None

    def effective_damage(self):
        # stronger hits at higher combo stages
        return BASE_ATTACK_DAMAGE + (self.combo_stage - 1)


class Enemy(Fighter):
    def __init__(self, x, y):
        super().__init__(x, y, 36, 56, ENEMY_COLOR, ENEMY_MAX_HEALTH)
        self.attack_cooldown = 1.0
        self.attack_timer = 0

    def ai(self, player, platforms):
        dx = player.rect.centerx - self.rect.centerx
        if abs(dx) > 48:
            self.vx = 1.2 if dx > 0 else -1.2
            self.facing = 1 if dx > 0 else -1
        else:
            self.vx = 0
            if self.attack_cooldown <= 0:
                self.attack_timer = 0.18
                self.attack_cooldown = 1.0
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1.0 / FPS
        if self.attack_timer > 0:
            self.attack_timer -= 1.0 / FPS

    def get_attack_rect(self):
        if self.attack_timer > 0:
            if self.facing >= 0:
                return pygame.Rect(self.rect.right, self.rect.top + 6, 26, self.rect.height - 12)
            else:
                return pygame.Rect(self.rect.left - 26, self.rect.top + 6, 26, self.rect.height - 12)
        return None


class RangedEnemy(Fighter):
    def __init__(self, x, y):
        super().__init__(x, y, 36, 56, RANGED_COLOR, RANGED_MAX_HEALTH)
        self.shoot_cooldown = 1.5
        self.shoot_timer = 0

    def ai(self, player, platforms, projectiles):
        # keep some distance, occasionally shoot
        dx = player.rect.centerx - self.rect.centerx
        if abs(dx) < 120:
            # step back
            self.vx = -0.8 if dx > 0 else 0.8
            self.facing = -1 if dx > 0 else 1
        else:
            self.vx = 0
        if self.shoot_cooldown <= 0:
            # spawn projectile toward player
            dirx = 1 if dx > 0 else -1
            px = self.rect.centerx + dirx * 20
            py = self.rect.centery
            projectiles.append({'rect': pygame.Rect(px, py, 10, 6), 'vx': dirx * 6, 'life': 3.0})
            self.shoot_cooldown = 1.8
        else:
            self.shoot_cooldown -= 1.0 / FPS


def draw_health_bar(surf, x, y, w, h, current, maximum):
    pygame.draw.rect(surf, (100, 0, 0), (x, y, w, h))
    if maximum > 0 and current > 0:
        inner_w = int(w * (current / maximum))
        pygame.draw.rect(surf, (0, 200, 0), (x, y, inner_w, h))


WAVES = [
    [('melee', 520), ('melee', 660)],
    [('melee', 520), ('ranged', 700), ('melee', 760)],
    [('ranged', 520), ('ranged', 660), ('melee', 740)],
]


def main():
    ensure_sounds()
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    try:
        attack_snd = pygame.mixer.Sound(ATTACK_SOUND)
        hit_snd = pygame.mixer.Sound(HIT_SOUND)
    except Exception:
        attack_snd = None
        hit_snd = None

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Street Fight — Extended MVP')
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    floor = pygame.Rect(0, HEIGHT - 64, WIDTH, 64)
    platforms = [floor]

    player = Player(120, HEIGHT - 64 - 64)

    enemies = []
    projectiles = []
    current_wave = 0
    def spawn_wave(idx):
        nonlocal enemies
        enemies = []
        for kind, x in WAVES[idx]:
            if kind == 'melee':
                enemies.append(Enemy(x, HEIGHT - 64 - 56))
            else:
                enemies.append(RangedEnemy(x, HEIGHT - 64 - 56))

    spawn_wave(0)

    running = True
    win = False
    lose = False

    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        move_left = keys[pygame.K_a] or keys[pygame.K_LEFT]
        move_right = keys[pygame.K_d] or keys[pygame.K_RIGHT]
        jump = keys[pygame.K_w] or keys[pygame.K_SPACE] or keys[pygame.K_UP]
        attack = keys[pygame.K_j]
        block = keys[pygame.K_k]

        player.blocking = block

        # movement
        if player.blocking:
            player.vx = 0
        else:
            player.vx = 0
            if move_left:
                player.vx = -PLAYER_SPEED
                player.facing = -1
            if move_right:
                player.vx = PLAYER_SPEED
                player.facing = 1
        if jump and player.on_ground and not player.blocking:
            player.vy = JUMP_VELOCITY
        if attack and not player.blocking:
            prev_combo = player.combo_stage
            player.attack()
            if attack_snd:
                attack_snd.play()

        player.update(platforms)

        # Update enemies and projectiles
        for e in enemies:
            if isinstance(e, RangedEnemy):
                e.ai(player, platforms, projectiles)
            else:
                e.ai(player, platforms)
            e.update(platforms)

        # projectiles update
        for p in list(projectiles):
            p['rect'].x += int(p['vx'])
            p['life'] -= 1.0 / FPS
            if p['life'] <= 0:
                projectiles.remove(p)

        # Player attack collisions
        player_attack_rect = player.get_attack_rect()
        if player_attack_rect:
            for e in enemies:
                if e.health > 0 and player_attack_rect.colliderect(e.rect):
                    dmg = player.effective_damage()
                    e.take_damage(dmg)
                    if hit_snd:
                        hit_snd.play()

        # Enemy melee attacks
        for e in enemies:
            if isinstance(e, Enemy):
                er = e.get_attack_rect()
                if er and er.colliderect(player.rect):
                    # player may block
                    if player.blocking:
                        player.take_damage(max(0, ENEMY_DAMAGE // 2))
                    else:
                        player.take_damage(ENEMY_DAMAGE)
                        if hit_snd:
                            hit_snd.play()

        # Projectiles hit player
        for p in list(projectiles):
            if p['rect'].colliderect(player.rect):
                if player.blocking:
                    player.take_damage(max(0, ENEMY_DAMAGE // 2))
                else:
                    player.take_damage(ENEMY_DAMAGE)
                try:
                    projectiles.remove(p)
                except ValueError:
                    pass

        # clean dead
        enemies = [e for e in enemies if e.health > 0]

        if not enemies:
            current_wave += 1
            if current_wave < len(WAVES):
                spawn_wave(current_wave)
            else:
                win = True

        if player.health <= 0:
            lose = True

        # Draw
        screen.fill((25, 25, 25))
        pygame.draw.rect(screen, FLOOR_COLOR, floor)

        for p in projectiles:
            pygame.draw.rect(screen, PROJECTILE_COLOR, p['rect'])

        for e in enemies:
            e.draw(screen)
            er = None
            if isinstance(e, Enemy):
                er = e.get_attack_rect()
            if er:
                pygame.draw.rect(screen, ATTACK_COLOR, er)

        player.draw(screen)
        if player_attack_rect:
            pygame.draw.rect(screen, ATTACK_COLOR, player_attack_rect)

        # UI
        draw_health_bar(screen, 10, 10, 180, 16, player.health, player.max_health)
        screen.blit(font.render('Player', True, WHITE), (10, 30))
        screen.blit(font.render(f'Wave: {min(current_wave+1, len(WAVES))}/{len(WAVES)}', True, WHITE), (10, 46))

        if enemies:
            # show first enemy health
            draw_health_bar(screen, WIDTH - 200, 10, 180, 16, enemies[0].health, enemies[0].max_health)
            screen.blit(font.render('Enemy', True, WHITE), (WIDTH - 200, 30))

        if win:
            surf = font.render('You win! Press Esc to exit.', True, WHITE)
            screen.blit(surf, (WIDTH//2 - surf.get_width()//2, HEIGHT//2))
        if lose:
            surf = font.render('You lose! Press Esc to exit.', True, WHITE)
            screen.blit(surf, (WIDTH//2 - surf.get_width()//2, HEIGHT//2))

        pygame.display.flip()

        if keys[pygame.K_ESCAPE]:
            running = False

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
