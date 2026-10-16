import asyncio
import pygame
import random
import sys

async def main():
    # 초기화
    pygame.init()

    # 화면 설정 (태블릿/모바일 가로 비율에 적합한 해상도)
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("헌법 수호 아케이드 (웹 최적화 버전)")

    # 색상 정의
    WHITE = (255, 255, 255)
    BLACK = (20, 20, 20)
    BLUE = (50, 150, 255)
    RED = (255, 80, 80)
    GREEN = (80, 220, 100)
    YELLOW = (255, 220, 50)
    PURPLE = (180, 100, 255)
    BTN_BG = (70, 80, 110)
    BTN_PRESS = (100, 120, 160)

    # 폰트 설정 (웹 환경 안전 fallback 적용)
    try:
        font_large = pygame.font.SysFont("malgungothic", 26)
        font_medium = pygame.font.SysFont("malgungothic", 18)
    except:
        font_large = pygame.font.Font(None, 32)
        font_medium = pygame.font.Font(None, 24)

    # 고1 수준 핵심 헌법 조문 퀴즈 데이터베이스
    QUESTIONS = [
        {
            "desc": "모든 국민은 법 앞에 평등하다. 누구든지 성별·종교·사회적\n신분에 의하여 차별을 받지 아니한다.",
            "answer": "제11조",
            "options": ["제11조", "제12조", "제31조"]
        },
        {
            "desc": "모든 국민은 신체의 자유를 가진다. 법률에 의하지 아니하고는\n체포·구속·압수·수색·심문을 받지 아니한다.",
            "answer": "제12조",
            "options": ["제10조", "제12조", "제37조"]
        },
        {
            "desc": "모든 국민은 능력에 따라 균등하게\n교육을 받을 권리를 가진다.",
            "answer": "제31조",
            "options": ["제11조", "제27조", "제31조"]
        },
        {
            "desc": "모든 국민은 인간다운 생활을 할 권리를 가진다.\n국가는 사회보장·사회복지의 증진에 노력할 의무를 진다.",
            "answer": "제34조",
            "options": ["제10조", "제31조", "제34조"]
        },
        {
            "desc": "국민의 모든 자유와 권리는 국가안전보장·질서유지 또는\n공공복리를 위하여 필요한 경우에 한하여 법률로써 제한할 수 있다.",
            "answer": "제37조",
            "options": ["제21조", "제34조", "제37조"]
        }
    ]

    # 파티클(빵빠레 효과) 클래스
    class Particle:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.vx = random.uniform(-5, 5)
            self.vy = random.uniform(-5, 5)
            self.color = random.choice([RED, GREEN, YELLOW, BLUE, PURPLE])
            self.life = random.randint(30, 60)

        def update(self):
            self.x += self.vx
            self.y += self.vy
            self.life -= 1

        def draw(self, surface):
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), 5)

    # 게임 변수 설정
    player_x = SCREEN_WIDTH // 2 - 25
    player_y = SCREEN_HEIGHT - 160  
    player_speed = 7
    bullets = []
    enemies = []
    particles = []

    score = 0
    lives = 3
    game_time = 120 * 60  # 120초 (60프레임 기준)
    clock = pygame.time.Clock()
    current_q = None

    # 터치/마우스용 가상 버튼 영역 정의
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
            ey = -50
            enemies.append({
                "text": opt,
                "x": ex,
                "y": ey,
                "rect": pygame.Rect(ex, ey, 140, 50),
                "is_correct": (opt == current_q["answer"])
            })

    load_new_question()

    # 메인 게임 루프
    running = True
    while running:
        screen.fill(BLACK)
        
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
                    bullets.append(pygame.Rect(player_x + 22, player_y, 6, 15))
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullets.append(pygame.Rect(player_x + 22, player_y, 6, 15))

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
            bullet.y -= 10
            if bullet.y < 0:
                bullets.remove(bullet)

        # 5. 적(보기) 업데이트 및 이동
        for enemy in enemies:
            enemy["y"] += 1.1  
            enemy["rect"].y = enemy["y"]
            
            if enemy["y"] > SCREEN_HEIGHT - 130:
                load_new_question()
                lives -= 1
                if lives <= 0:
                    running = False
                break

        # 6. 충돌 검사 (총알과 적)
        for bullet in bullets[:]:
            hit = False
            for enemy in enemies:
                if bullet.colliderect(enemy["rect"]):
                    hit = True
                    if enemy["is_correct"]:
                        score += 10
                        for _ in range(50):
                            particles.append(Particle(enemy["x"] + 70, enemy["y"] + 25))
                        load_new_question()
                    else:
                        score = max(0, score - 5)
                        lives -= 1
                        if lives <= 0:
                            running = False
                        load_new_question()
                    break
            if hit:
                if bullet in bullets:
                    bullets.remove(bullet)
                break

        # 7. 파티클 업데이트
        for p in particles[:]:
            p.update()
            if p.life <= 0:
                particles.remove(p)

        # --- 화면 그리기 ---
        
        # 상단 문제 패널
        pygame.draw.rect(screen, (30, 40, 60), (50, 15, SCREEN_WIDTH - 100, 90), border_radius=10)
        pygame.draw.rect(screen, BLUE, (50, 15, SCREEN_WIDTH - 100, 90), 2, border_radius=10)
        
        lines = current_q["desc"].split("\n")
        for i, line in enumerate(lines):
            txt_surface = font_medium.render(line, True, WHITE)
            screen.blit(txt_surface, (70, 24 + (i * 24)))

        # 정보 표시 (점수, 남은 시간, 목숨)
        timer_sec = game_time // 60
        info_text = font_medium.render(f"점수: {score} | 남은 시간: {timer_sec}초 | 목숨: {'❤️' * lives}", True, YELLOW)
        screen.blit(info_text, (50, 115))

        # 플레이어 캐릭터
        pygame.draw.polygon(screen, GREEN, [(player_x + 25, player_y), (player_x, player_y + 40), (player_x + 50, player_y + 40)])

        # 총알 그리기
        for bullet in bullets:
            pygame.draw.rect(screen, YELLOW, bullet)

        # 적(보기) 그리기
        for enemy in enemies:
            pygame.draw.rect(screen, (50, 50, 70), enemy["rect"], border_radius=8)
            pygame.draw.rect(screen, PURPLE, enemy["rect"], 2, border_radius=8)
            txt = font_large.render(enemy["text"], True, WHITE)
            tx = enemy["x"] + (140 - txt.get_width()) // 2
            ty = enemy["y"] + (50 - txt.get_height()) // 2
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

        pygame.draw.rect(screen, (200, 60, 60) if rect_fire.collidepoint(mouse_pos) and mouse_pressed[0] else (180, 50, 50), rect_fire, border_radius=12)
        pygame.draw.rect(screen, YELLOW, rect_fire, 2, border_radius=12)
        txt_f = font_medium.render("발사 🚀", True, WHITE)
        screen.blit(txt_f, (rect_fire.x + (rect_fire.width - txt_f.get_width()) // 2, rect_fire.y + (rect_fire.height - txt_f.get_height()) // 2))

        pygame.display.flip()
        
        # **가장 중요: 웹 브라우저가 멈추지 않도록 제어권을 양보**
        await asyncio.sleep(0)
        clock.tick(60)

    # --- 게임 종료 화면 ---
    screen.fill(BLACK)
    game_over_txt = font_large.render(f"게임 종료! 최종 점수: {score}점", True, YELLOW)
    sub_txt = font_medium.render("새로고침하면 다시 시작합니다.", True, WHITE)
    screen.blit(game_over_txt, (SCREEN_WIDTH // 2 - game_over_txt.get_width() // 2, 220))
    screen.blit(sub_txt, (SCREEN_WIDTH // 2 - sub_txt.get_width() // 2, 280))
    pygame.display.flip()

    # 종료 후 대기
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
