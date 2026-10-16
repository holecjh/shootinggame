import asyncio
import pygame
import random
import sys

async def main():
    pygame.init()

    # 화면 설정 (800x600 가로형)
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("헌법 수호 갤럭시 아케이드")

    # 색상 정의
    WHITE = (255, 255, 255)
    BLACK = (20, 20, 20)
    NAVY = (15, 20, 40)
    BLUE = (50, 150, 255)
    RED = (255, 80, 80)
    GREEN = (80, 220, 100)
    YELLOW = (255, 220, 50)
    PURPLE = (180, 100, 255)
    CYAN = (0, 220, 255)
    BTN_BG = (70, 80, 110)
    BTN_PRESS = (100, 120, 160)

    # 웹에서 100% 안전한 기본 폰트 사용 (한글 깨짐 방지)
    font_large = pygame.font.Font(None, 32)
    font_medium = pygame.font.Font(None, 24)
    font_title = pygame.font.Font(None, 48)

    # 고1 수준 핵심 헌법 조문 퀴즈 데이터베이스
    QUESTIONS = [
        {
            "desc": "모든 국민은 법 앞에 평등하다. 누구든지 성별·종교·사회적 신분에 의하여 차별을 받지 아니한다.",
            "answer": "제11조",
            "options": ["제11조", "제12조", "제31조"]
        },
        {
            "desc": "모든 국민은 신체의 자유를 가진다. 법률에 의하지 아니하고는 체포·구속·압수·수색·심문을 받지 아니한다.",
            "answer": "제12조",
            "options": ["제10조", "제12조", "제37조"]
        },
        {
            "desc": "모든 국민은 능력에 따라 균등하게 교육을 받을 권리를 가진다.",
            "answer": "제31조",
            "options": ["제11조", "제27조", "제31조"]
        },
        {
            "desc": "모든 국민은 인간다운 생활을 할 권리를 가진다. 국가는 사회보장·사회복지의 증진에 노력할 의무를 진다.",
            "answer": "제34조",
            "options": ["제10조", "제31조", "제34조"]
        },
        {
            "desc": "국민의 모든 자유와 권리는 국가안전보장·질서유지 또는 공공복리를 위하여 필요한 경우에 한하여 법률로써 제한할 수 있다.",
            "answer": "제37조",
            "options": ["제21조", "제34조", "제37조"]
        }
    ]

    # 파티클(빵빠레 효과) 클래스
    class Particle:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.vx = random.uniform(-6, 6)
            self.vy = random.uniform(-6, 6)
            self.color = random.choice([RED, GREEN, YELLOW, CYAN, PURPLE])
            self.life = random.randint(40, 70)

        def update(self):
            self.x += self.vx
            self.y += self.vy
            self.life -= 1

        def draw(self, surface):
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), 4)

    # 배경 별(Starfield) 효과 클래스
    class Star:
        def __init__(self):
            self.x = random.randint(0, SCREEN_WIDTH)
            self.y = random.randint(0, SCREEN_HEIGHT)
            self.speed = random.uniform(0.5, 2.0)
            self.size = random.randint(1, 3)

        def update(self):
            self.y += self.speed
            if self.y > SCREEN_HEIGHT:
                self.y = 0
                self.x = random.randint(0, SCREEN_WIDTH)

        def draw(self, surface):
            pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.size)

    stars = [Star() for _ in range(60)]

    # 게임 변수 설정
    player_x = SCREEN_WIDTH // 2 - 25
    player_y = SCREEN_HEIGHT - 180  
    player_speed = 7
    bullets = []
    enemies = []
    particles = []

    score = 0
    lives = 3
    game_time = 120 * 60  # 총 2분 (120초)
    clock = pygame.time.Clock()
    current_q = None

    # 터치/마우스용 가상 버튼 영역
    rect_left = pygame.Rect(30, 510, 80, 70)
    rect_right = pygame.Rect(130, 510, 80, 70)
    rect_fire = pygame.Rect(650, 510, 120, 70)

    def load_new_question():
        nonlocal current_q, enemies
        current_q = random.choice(QUESTIONS)
        enemies = []
        
        options = current_q["options"].copy()
        random.shuffle(options)
        
        for i, opt in enumerate(options):
            ex = 150 + i * 220
            ey = -60
            # 단어가 콕콕 박히는 통일된 애니메이션을 위해 초기 오프셋/스케일 부여
            enemies.append({
                "text": opt,
                "x": ex,
                "y": ey,
                "base_x": ex,
                "wobble_offset": random.uniform(0, 100), # 둥실둥실 액션용
                "rect": pygame.Rect(ex, ey, 140, 55),
                "is_correct": (opt == current_q["answer"])
            })

    # --- [요청 4] 게임 시작 전 3 -> 2 -> 1 카운트다운 ---
    for count in [3, 2, 1]:
        start_tick = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start_tick < 1000:
            screen.fill(NAVY)
            for star in stars:
                star.update()
                star.draw(screen)
            
            cnt_txt = font_title.render(f"READY... {count}", True, YELLOW)
            screen.blit(cnt_txt, (SCREEN_WIDTH // 2 - cnt_txt.get_width() // 2, SCREEN_HEIGHT // 2 - 30))
            pygame.display.flip()
            await asyncio.sleep(0)
            clock.tick(60)

    load_new_question()

    # 메인 게임 루프 (2분 내외)
    running = True
    while running:
        screen.fill(NAVY)
        
        # 우주 배경 별 흐름
        for star in stars:
            star.update()
            star.draw(screen)

        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        
        moving_left = False
        moving_right = False
        
        # 1. 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if rect_fire.collidepoint(event.pos):
                    # 갤럭시 전투기 포신에서 나가는 레이저 (더블 레이저 느낌)
                    bullets.append(pygame.Rect(player_x + 10, player_y, 4, 15))
                    bullets.append(pygame.Rect(player_x + 36, player_y, 4, 15))
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullets.append(pygame.Rect(player_x + 10, player_y, 4, 15))
                    bullets.append(pygame.Rect(player_x + 36, player_y, 4, 15))

        # 하단 버튼 터치/클릭 유지 처리
        if mouse_pressed[0]:
            if rect_left.collidepoint(mouse_pos):
                moving_left = True
            elif rect_right.collidepoint(mouse_pos):
                moving_right = True

        # 키보드 입력 병행 처리
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or moving_left:
            if player_x > 20:
                player_x -= player_speed
        if keys[pygame.K_RIGHT] or moving_right:
            if player_x < SCREEN_WIDTH - 70:
                player_x += player_speed

        # 3. 시간 관리 (120초 타이머)
        if game_time > 0:
            game_time -= 1
        else:
            running = False

        # 4. 총알 업데이트
        for bullet in bullets[:]:
            bullet.y -= 12
            if bullet.y < 0:
                bullets.remove(bullet)

        # 5. 적(보기) 업데이트 및 이동 + [요청 3] 단어가 콕콕 박히는(통통 튀는) 액션 효과
        for enemy in enemies:
            enemy["y"] += 1.2  # 하강 속도
            # 좌우로 톡톡 튀며 내려오는 탄력 있는 움직임 (시각적 액션)
            enemy["wobble_offset"] += 0.08
            enemy["x"] = enemy["base_x"] + int(math.sin(enemy["wobble_offset"]) * 15)
            enemy["rect"].x = enemy["x"]
            enemy["rect"].y = enemy["y"]
            
            # 바닥에 닿으면 오답 처리 및 다음 문제로 정상 전환 ([요청 5] 버그 해결)
            if enemy["y"] > SCREEN_HEIGHT - 150:
                load_new_question()
                lives -= 1
                if lives <= 0:
                    running = False
                break

        # 6. 충돌 검사 (총알과 적)
        hit_occurred = False
        for bullet in bullets[:]:
            for enemy in enemies:
                if bullet.colliderect(enemy["rect"]):
                    hit_occurred = True
                    if enemy["is_correct"]:
                        score += 10
                        for _ in range(40):
                            particles.append(Particle(enemy["x"] + 70, enemy["y"] + 25))
                    else:
                        score = max(0, score - 5)
                        lives -= 1
                        if lives <= 0:
                            running = False
                    if bullet in bullets:
                        bullets.remove(bullet)
                    break
            if hit_occurred:
                break
        
        if hit_occurred:
            load_new_question() # 정/오답 판정 시 즉시 다음 문제 세팅

        # 7. 파티클 업데이트
        for p in particles[:]:
            p.update()
            if p.life <= 0:
                particles.remove(p)

        # --- 화면 그리기 ---
        
        # 정보 표시 (점수, 남은 시간, 목숨)
        timer_sec = game_time // 60
        info_text = font_medium.render(f"SCORE: {score}  |  TIME: {timer_sec}s  |  LIFE: {'❤️' * lives}", True, YELLOW)
        screen.blit(info_text, (30, 20))

        # --- [요청 2] 문장이 완성되는 부분을 하단(조준선 위쪽)으로 배치 ---
        desc_box_rect = pygame.Rect(50, 410, SCREEN_WIDTH - 100, 75)
        pygame.draw.rect(screen, (25, 35, 60), desc_box_rect, border_radius=10)
        pygame.draw.rect(screen, CYAN, desc_box_rect, 2, border_radius=10)
        
        # 헌법 조문 텍스트 렌더링 (간단 줄바꿈 처리)
        desc_text = current_q["desc"]
        words = desc_text.split(" ")
        line1, line2 = "", ""
        for word in words:
            if font_medium.size(line1 + " " + word)[0] < SCREEN_WIDTH - 140:
                line1 += (" " if line1 else "") + word
            else:
                line2 += (" " if line2 else "") + word

        t1 = font_medium.render(line1, True, WHITE)
        t2 = font_medium.render(line2 if line2 else "", True, WHITE)
        screen.blit(t1, (70, 420))
        if line2:
            screen.blit(t2, (70, 445))

        # --- [요청 1] 갤럭시게임 스타일의 화려하고 멋진 비행기 디자인 ---
        # 본체 삼각형
        pygame.draw.polygon(screen, CYAN, [(player_x + 25, player_y), (player_x + 5, player_y + 40), (player_x + 45, player_y + 40)])
        # 날개 및 조종석 포인트
        pygame.draw.polygon(screen, BLUE, [(player_x + 5, player_y + 30), (player_x - 5, player_y + 45), (player_x + 10, player_y + 40)])
        pygame.draw.polygon(screen, BLUE, [(player_x + 45, player_y + 30), (player_x + 55, player_y + 45), (player_x + 40, player_y + 40)])
        pygame.draw.circle(screen, WHITE, (player_x + 25, player_y + 20), 4) # 조종석 불빛
        # 엔진 부스터 불꽃 효과
        booster_color = random.choice([RED, YELLOW])
        pygame.draw.polygon(screen, booster_color, [(player_x + 15, player_y + 40), (player_x + 25, player_y + 55), (player_x + 35, player_y + 40)])

        # 총알 그리기 (네온 레이저 스타일)
        for bullet in bullets:
            pygame.draw.rect(screen, CYAN, bullet, border_radius=2)

        # 적(보기) 그리기 + [요청 3] 단어 뱃지 디자인
        for enemy in enemies:
            pygame.draw.rect(screen, (40, 50, 80), enemy["rect"], border_radius=8)
            pygame.draw.rect(screen, PURPLE, enemy["rect"], 2, border_radius=8)
            txt = font_large.render(enemy["text"], True, WHITE)
            tx = enemy["x"] + (140 - txt.get_width()) // 2
            ty = enemy["y"] + (55 - txt.get_height()) // 2
            screen.blit(txt, (tx, ty))

        # 파티클 그리기
        for p in particles:
            p.draw(screen)

        # --- 터치 컨트롤 UI (하단 가상 버튼) ---
        pygame.draw.rect(screen, BTN_PRESS if rect_left.collidepoint(mouse_pos) and mouse_pressed[0] else BTN_BG, rect_left, border_radius=12)
        pygame.draw.rect(screen, WHITE, rect_left, 2, border_radius=12)
        txt_l = font_large.render("◀", True, WHITE)
        screen.blit(txt_l, (rect_left.x + 25, rect_left.y + 18))

        pygame.draw.rect(screen, BTN_PRESS if rect_right.collidepoint(mouse_pos) and mouse_pressed[0] else BTN_BG, rect_right, border_radius=12)
        pygame.draw.rect(screen, WHITE, rect_right, 2, border_radius=12)
        txt_r = font_large.render("▶", True, WHITE)
        screen.blit(txt_r, (rect_right.x + 25, rect_right.y + 18))

        pygame.draw.rect(screen, (220, 60, 60) if rect_fire.collidepoint(mouse_pos) and mouse_pressed[0] else (180, 50, 50), rect_fire, border_radius=12)
        pygame.draw.rect(screen, YELLOW, rect_fire, 2, border_radius=12)
        txt_f = font_medium.render("FIRE 🚀", True, WHITE)
        screen.blit(txt_f, (rect_fire.x + (rect_fire.width - txt_f.get_width()) // 2, rect_fire.y + (rect_fire.height - txt_f.get_height()) // 2))

        pygame.display.flip()
        await asyncio.sleep(0)
        clock.tick(60)

    # --- 게임 종료 화면 ---
    screen.fill(NAVY)
    game_over_txt = font_title.render(f"GAME OVER! SCORE: {score}", True, YELLOW)
    sub_txt = font_medium.render("새로고침하면 다시 시작합니다.", True, WHITE)
    screen.blit(game_over_txt, (SCREEN_WIDTH // 2 - game_over_txt.get_width() // 2, 220))
    screen.blit(sub_txt, (SCREEN_WIDTH // 2 - sub_txt.get_width() // 2, 290))
    pygame.display.flip()

    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    import math
    asyncio.run(main())
