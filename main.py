import asyncio
import pygame
import random
import sys

async def main():
    pygame.init()

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

    # 한글 폰트 로드 (font.ttf 필수)
    try:
        font_large = pygame.font.Font("font.ttf", 24)
        font_medium = pygame.font.Font("font.ttf", 19)
        font_small = pygame.font.Font("font.ttf", 15)
        font_title = pygame.font.Font("font.ttf", 38)
    except:
        font_large = pygame.font.Font(None, 28)
        font_medium = pygame.font.Font(None, 22)
        font_small = pygame.font.Font(None, 16)
        font_title = pygame.font.Font(None, 42)

    # 총 10개의 핵심 헌법 조문 퀴즈 데이터베이스
    QUESTIONS = [
        {
            "desc": "모든 국민은 인간으로서의 존엄과 가치를 가지며, 행복을 추구할 권리를 가진다.",
            "answer": "제10조",
            "options": ["제10조", "제11조", "제12조"]
        },
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
            "desc": "모든 국민은 언론·출판의 자유와 집회·결사의 자유를 가진다.",
            "answer": "제21조",
            "options": ["제11조", "제21조", "제34조"]
        },
        {
            "desc": "모든 국민은 헌법과 법률이 정한 법관에 의하여 법률에 의한 재판을 받을 권리를 가진다.",
            "answer": "제27조",
            "options": ["제21조", "제27조", "제37조"]
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
            "desc": "모든 국민은 근로의 권리를 가진다. 국가는 사회적·경제적 방법으로 근로자의 고용의 증진과 적정임금의 보장에 노력하여야 한다.",
            "answer": "제32조",
            "options": ["제32조", "제34조", "제37조"]
        },
        {
            "desc": "국민의 모든 자유와 권리는 국가안전보장·질서유지 또는 공공복리를 위하여 필요한 경우에 한하여 법률로써 제한할 수 있다.",
            "answer": "제37조",
            "options": ["제21조", "제34조", "제37조"]
        },
        {
            "desc": "모든 국민의 재산권은 보장된다. 그 내용과 한계는 법률로 정한다.",
            "answer": "제23조",
            "options": ["제21조", "제23조", "제31조"]
        }
    ]

    class Particle:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.vx = random.uniform(-5, 5)
            self.vy = random.uniform(-5, 5)
            self.color = random.choice([RED, GREEN, YELLOW, CYAN, PURPLE])
            self.life = random.randint(30, 60)

        def update(self):
            self.x += self.vx
            self.y += self.vy
            self.life -= 1

        def draw(self, surface):
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), 4)

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

    # 게임 변수 설정 (우주선을 위쪽 안전한 영역에 고정)
    player_x = SCREEN_WIDTH // 2 - 25
    player_y = 280  
    bullets = []
    enemies = []
    particles = []

    score = 0
    lives = 3
    q_index = 0
    game_history = []
    clock = pygame.time.Clock()
    current_q = None

    # [레이아웃 수정] 하단 UI 영역 분리 (설상 상자 왼쪽, FIRE 버튼 오른쪽)
    desc_box_rect = pygame.Rect(30, 430, 560, 140)
    rect_fire = pygame.Rect(610, 430, 160, 140)

    def load_question():
        nonlocal current_q, enemies, q_index
        if q_index >= len(QUESTIONS):
            return False
        
        current_q = QUESTIONS[q_index]
        enemies = []
        
        options = current_q["options"].copy()
        random.shuffle(options)
        
        for i, opt in enumerate(options):
            ex = 150 + i * 220
            ey = -40
            enemies.append({
                "text": opt,
                "x": ex,
                "y": ey,
                "base_x": ex,
                "wobble_offset": random.uniform(0, 100),
                "rect": pygame.Rect(ex, ey, 130, 50),
                "is_correct": (opt == current_q["answer"])
            })
        return True

    # 3초 카운트다운
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

    if not load_question():
        return

    game_state = "PLAY"
    running = True

    while running:
        screen.fill(NAVY)
        
        for star in stars:
            star.update()
            star.draw(screen)

        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()

        if game_state == "PLAY":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if rect_fire.collidepoint(event.pos):
                        # [요청 2] 싱글 레이저 (정중앙에서 1발 발사)
                        bullets.append(pygame.Rect(player_x + 23, player_y, 4, 16))
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        bullets.append(pygame.Rect(player_x + 23, player_y, 4, 16))

            # 터치/마우스 드래그 이동 (하단 UI 영역 침범 불가)
            if mouse_pressed[0]:
                if not rect_fire.collidepoint(mouse_pos) and mouse_pos[1] < 400:
                    target_x = mouse_pos[0] - 25
                    player_x += (target_x - player_x) * 0.25
                    if player_x < 20: player_x = 20
                    if player_x > SCREEN_WIDTH - 70: player_x = SCREEN_WIDTH - 70

            for bullet in bullets[:]:
                bullet.y -= 12
                if bullet.y < 0:
                    bullets.remove(bullet)

            # [요청 3] 느긋한 단어 낙하 속도 (0.7)
            for enemy in enemies:
                enemy["y"] += 0.7  
                enemy["wobble_offset"] += 0.05
                enemy["x"] = enemy["base_x"] + int(math.sin(enemy["wobble_offset"]) * 12)
                enemy["rect"].x = enemy["x"]
                enemy["rect"].y = enemy["y"]
                
                # 상단 설명 상자(y=430)에 닿기 전에 처리되도록 설정
                if enemy["y"] > 370:
                    game_history.append({
                        "desc": current_q["desc"],
                        "answer": current_q["answer"],
                        "user": "시간 초과",
                        "correct": False
                    })
                    q_index += 1
                    lives -= 1
                    if lives <= 0 or not load_question():
                        game_state = "RESULT"
                    break

            hit_result = None
            for bullet in bullets[:]:
                for enemy in enemies:
                    if bullet.colliderect(enemy["rect"]):
                        if enemy["is_correct"]:
                            score += 10
                            for _ in range(40):
                                particles.append(Particle(enemy["x"] + 65, enemy["y"] + 25))
                            hit_result = "CORRECT"
                        else:
                            score = max(0, score - 5)
                            lives -= 1
                            hit_result = "WRONG"
                        
                        game_history.append({
                            "desc": current_q["desc"],
                            "answer": current_q["answer"],
                            "user": enemy["text"],
                            "correct": (hit_result == "CORRECT")
                        })
                        
                        if bullet in bullets:
                            bullets.remove(bullet)
                        break
                if hit_result:
                    break

            if hit_result:
                q_index += 1
                if lives <= 0 or not load_question():
                    game_state = "RESULT"

            for p in particles[:]:
                p.update()
                if p.life <= 0:
                    particles.remove(p)

            # --- 화면 렌더링 (플레이 중) ---
            info_text = font_medium.render(f"QUESTION: {q_index + 1}/10  |  SCORE: {score}  |  LIFE: {'❤️' * lives}", True, YELLOW)
            screen.blit(info_text, (30, 20))

            # [요청 3] 하단 설명 박스 (우주선과 절대 겹치지 않도록 맨 아래 배치)
            pygame.draw.rect(screen, (25, 35, 60), desc_box_rect, border_radius=12)
            pygame.draw.rect(screen, CYAN, desc_box_rect, 2, border_radius=12)
            
            desc_text = current_q["desc"]
            words = desc_text.split(" ")
            line1, line2, line3 = "", "", ""
            for word in words:
                if font_large.size(line1 + " " + word)[0] < 520:
                    line1 += (" " if line1 else "") + word
                elif font_large.size(line2 + " " + word)[0] < 520:
                    line2 += (" " if line2 else "") + word
                else:
                    line3 += (" " if line3 else "") + word

            screen.blit(font_large.render(line1, True, WHITE), (50, 445))
            if line2:
                screen.blit(font_large.render(line2, True, WHITE), (50, 480))
            if line3:
                screen.blit(font_large.render(line3, True, WHITE), (50, 515))

            # 우주선 그리기 (상단 영역)
            pygame.draw.polygon(screen, CYAN, [(player_x + 25, player_y), (player_x + 5, player_y + 40), (player_x + 45, player_y + 40)])
            pygame.draw.polygon(screen, BLUE, [(player_x + 5, player_y + 30), (player_x - 5, player_y + 45), (player_x + 10, player_y + 40)])
            pygame.draw.polygon(screen, BLUE, [(player_x + 45, player_y + 30), (player_x + 55, player_y + 45), (player_x + 40, player_y + 40)])
            pygame.draw.circle(screen, WHITE, (player_x + 25, player_y + 20), 4)
            booster_color = random.choice([RED, YELLOW])
            pygame.draw.polygon(screen, booster_color, [(player_x + 15, player_y + 40), (player_x + 25, player_y + 55), (player_x + 35, player_y + 40)])

            for bullet in bullets:
                pygame.draw.rect(screen, CYAN, bullet, border_radius=2)

            for enemy in enemies:
                pygame.draw.rect(screen, (40, 50, 80), enemy["rect"], border_radius=8)
                pygame.draw.rect(screen, PURPLE, enemy["rect"], 2, border_radius=8)
                txt = font_large.render(enemy["text"], True, WHITE)
                tx = enemy["x"] + (130 - txt.get_width()) // 2
                ty = enemy["y"] + (50 - txt.get_height()) // 2
                screen.blit(txt, (tx, ty))

            for p in particles:
                p.draw(screen)

            # 우측 대형 FIRE 버튼 UI
            is_fire_pressed = rect_fire.collidepoint(mouse_pos) and mouse_pressed[0]
            pygame.draw.rect(screen, (220, 60, 60) if is_fire_pressed else (180, 50, 50), rect_fire, border_radius=15)
            pygame.draw.rect(screen, YELLOW, rect_fire, 3, border_radius=15)
            txt_f = font_title.render("FIRE 🚀", True, WHITE)
            screen.blit(txt_f, (rect_fire.x + (rect_fire.width - txt_f.get_width()) // 2, rect_fire.y + (rect_fire.height - txt_f.get_height()) // 2 - 5))

        elif game_state == "RESULT":
            screen.fill(NAVY)
            
            title_txt = font_title.render(f"QUIZ RESULT - SCORE: {score}", True, YELLOW)
            screen.blit(title_txt, (SCREEN_WIDTH // 2 - title_txt.get_width() // 2, 25))

            y_offset = 80
            for idx, h in enumerate(game_history[:8]):
                status_str = "O" if h["correct"] else "X"
                status_color = GREEN if h["correct"] else RED
                
                res_line = f"[{idx+1}] 정답: {h['answer']} | 내 선택: {h['user']}"
                t_surf = font_small.render(res_line, True, WHITE)
                s_surf = font_small.render(status_str, True, status_color)
                
                screen.blit(t_surf, (50, y_offset))
                screen.blit(s_surf, (720, y_offset))
                y_offset += 38

            sub_txt = font_medium.render("새로고침(F5)하면 다시 시작할 수 있습니다.", True, CYAN)
            screen.blit(sub_txt, (SCREEN_WIDTH // 2 - sub_txt.get_width() // 2, SCREEN_HEIGHT - 50))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

        pygame.display.flip()
        await asyncio.sleep(0)
        clock.tick(60)

    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    import math
    asyncio.run(main())
