import pygame
import sys
import random
from game_objects import Paddle, Ball, Brick, PowerUp, Shield, Laser

pygame.init()
pygame.mixer.init()
clock = pygame.time.Clock()

screen_width, screen_height = 750, 550
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Arkanoid by Khamidakhon Ibodullaeva")


BG_COLOR = pygame.Color('grey12')
BRICK_COLORS = [(176, 224, 230), (216, 191, 216), (255, 182, 193), (152, 251, 152)]
font = pygame.font.Font(None, 40)

# === Sounds ===
try:
    bounce_sound = pygame.mixer.Sound('sounds/bounce.wav')
    brick_break_sound = pygame.mixer.Sound('sounds/brick_break.wav')
    game_over_sound = pygame.mixer.Sound('sounds/game_over.wav')
    laser_sound = pygame.mixer.Sound('sounds/laser.wav')
except pygame.error as e:
    print(f"Sound error: {e}")

    class DummySound:
        def play(self): pass

    bounce_sound = brick_break_sound = game_over_sound = laser_sound = DummySound()

# === Game objects ===
paddle = Paddle(screen_width, screen_height)
balls = [Ball(screen_width, screen_height)]
bricks = []
power_ups = []
lasers = []
shield = None

score = 0
lives = 3
current_level = 0
is_muted = False

def create_brick_wall(rows):
    b_list = []
    brick_cols = 10
    brick_width = 75
    brick_height = 20
    brick_padding = 5
    wall_start_y = 50
    for row in range(rows):
        for col in range(brick_cols):
            x = col * (brick_width + brick_padding) + brick_padding
            y = row * (brick_height + brick_padding) + wall_start_y
            color = BRICK_COLORS[row % len(BRICK_COLORS)]
            b_list.append(Brick(x, y, brick_width, brick_height, color))
    return b_list

levels = [2, 4, 6]
bricks = create_brick_wall(levels[current_level])

game_state = 'title'

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game_state == 'title':
                    game_state = 'playing'
                elif game_state == 'game_over':
                    paddle.reset()
                    balls = [Ball(screen_width, screen_height)]
                    current_level = 0
                    bricks = create_brick_wall(levels[current_level])
                    score = 0
                    lives = 3
                    power_ups.clear()
                    lasers.clear()
                    shield = None
                    game_state = 'title'
            if event.key == pygame.K_m:
                is_muted = not is_muted
            if event.key == pygame.K_r and game_state == 'game_over':
                paddle.reset()
                balls = [Ball(screen_width, screen_height)]
                current_level = 0
                bricks = create_brick_wall(levels[current_level])
                score = 0
                lives = 3
                power_ups.clear()
                lasers.clear()
                shield = None
                game_state = 'playing'
            if event.key == pygame.K_f and paddle.has_laser:
                lasers.append(Laser(paddle.rect.centerx - 30, paddle.rect.top))
                lasers.append(Laser(paddle.rect.centerx + 30, paddle.rect.top))
                if not is_muted:
                    laser_sound.play()

    screen.fill(BG_COLOR)

    if game_state == 'title':
        title_surf = font.render("ARKANOID by Khamidakhon", True, (255, 255, 255))
        start_surf = font.render("Press SPACE to Start", True, (255, 255, 255))
        mute_surf = font.render("Press M to Mute", True, (255, 255, 255))
        screen.blit(title_surf, (screen_width//2 - title_surf.get_width()//2, 200))
        screen.blit(start_surf, (screen_width//2 - start_surf.get_width()//2, 300))
        screen.blit(mute_surf, (screen_width//2 - mute_surf.get_width()//2, 350))
    elif game_state == 'playing':
        paddle.update()
        paddle.draw(screen)

        for ball in balls[:]:
            status = ball.update(paddle)
            ball.draw(screen)

            if status == 'lost':
                if shield and shield.active:
                    ball.rect.bottom = shield.rect.top
                    ball.speed_y *= -1
                    shield.active = False
                else:
                    balls.remove(ball)
                    if not balls:
                        lives -= 1
                        if not is_muted:
                            game_over_sound.play()
                        if lives <= 0:
                            game_state = 'game_over'
                        else:
                            balls = [Ball(screen_width, screen_height)]
                            paddle.reset()

        for brick in bricks[:]:
            for ball in balls:
                if ball.rect.colliderect(brick.rect):
                    if not ball.is_fireball:
                        ball.speed_y *= -1
                    if not is_muted:
                        bounce_sound.play()
                    bricks.remove(brick)
                    score += 10
                    if random.random() < 0.3:
                        p_type = random.choice(['grow', 'multi', 'shield', 'fireball', 'laser'])
                        power_ups.append(PowerUp(brick.rect.centerx, brick.rect.centery, p_type))
                    break
            brick.draw(screen)

        for power_up in power_ups[:]:
            power_up.update()
            power_up.draw(screen)
            if paddle.rect.colliderect(power_up.rect):
                if power_up.type == 'grow':
                    paddle.width = 150
                    paddle.rect.width = paddle.width
                elif power_up.type == 'multi':
                    new_ball = Ball(screen_width, screen_height)
                    new_ball.rect.center = balls[0].rect.center
                    new_ball.speed_x = -balls[0].speed_x
                    new_ball.speed_y = balls[0].speed_y
                    balls.append(new_ball)
                elif power_up.type == 'shield':
                    shield = Shield(screen_width, screen_height - 10)
                elif power_up.type == 'fireball':
                    for b in balls:
                        b.is_fireball = True
                elif power_up.type == 'laser':
                    paddle.has_laser = True
                power_ups.remove(power_up)

        for laser in lasers[:]:
            laser.update()
            if laser.rect.bottom < 0:
                lasers.remove(laser)
            else:
                for brick in bricks[:]:
                    if laser.rect.colliderect(brick.rect):
                        bricks.remove(brick)
                        if not is_muted:
                            brick_break_sound.play()
                        score += 10
                        lasers.remove(laser)
                        break
            laser.draw(screen)

        if shield:
            shield.draw(screen)

        if not bricks:
            current_level += 1
            if current_level < len(levels):
                bricks = create_brick_wall(levels[current_level])
                balls = [Ball(screen_width, screen_height)]
                paddle.reset()
            else:
                # Вместо win начинаем снова
                current_level = 0
                bricks = create_brick_wall(levels[current_level])
                balls = [Ball(screen_width, screen_height)]
                paddle.reset()

        score_surf = font.render(f"Score: {score}", True, (255, 255, 255))
        lives_surf = font.render(f"Lives: {lives}", True, (255, 255, 255))
        sound_status_text = "Sound: OFF" if is_muted else "Sound: ON"
        sound_surf = font.render(sound_status_text, True, (255, 255, 255))
        
        score_x = 10
        score_y = 10
        
        lives_x = screen_width - lives_surf.get_width() - 10
        lives_y = 10
        
        sound_x = screen_width // 2 - sound_surf.get_width() // 2
        sound_y = 10
        
        screen.blit(score_surf, (score_x, score_y))
        screen.blit(lives_surf, (lives_x, lives_y))
        screen.blit(sound_surf, (sound_x, sound_y))


    elif game_state == 'game_over':
        over_surf = font.render("GAME OVER", True, (255, 255, 255))
        restart_surf = font.render("Press R to Retry or SPACE for Title", True, (255, 255, 255))
        screen.blit(over_surf, (screen_width//2 - over_surf.get_width()//2, 250))
        screen.blit(restart_surf, (screen_width//2 - restart_surf.get_width()//2, 300))

    pygame.display.flip()
    clock.tick(60)
