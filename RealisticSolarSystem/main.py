import pygame
import math
import os

pygame.init()

WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Realistic 2D Solar System Simulation with Moons")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
SLIDER_COLOR = (100, 100, 255)

FONT = pygame.font.SysFont("Segoe UI", 18)
BIGFONT = pygame.font.SysFont("Segoe UI", 22, bold=True)
SMALL_FONT = pygame.font.SysFont("Segoe UI", 14)

clock = pygame.time.Clock()
center_x, center_y = WIDTH // 2, HEIGHT // 2

# Texture folder path
TEXTURE_PATH = r"C:\Users\veert\Downloads\RealisticSolarSystem\textures"

# Planet data: (name, orbital radius, size, speed, texture filename)
planets_info = [
    ("Mercury", 60, 12, 4.15, "mercury.png"),
    ("Venus", 90, 18, 1.62, "venus.png"),
    ("Earth", 130, 20, 1.0, "earth.png"),
    ("Mars", 170, 16, 0.53, "mars.png"),
    ("Jupiter", 230, 38, 0.08, "jupiter.png"),
    ("Saturn", 290, 34, 0.03, "saturn.png"),
    ("Uranus", 350, 28, 0.011, "uranus.png"),
    ("Neptune", 410, 27, 0.006, "neptune.png"),
]

# Moons data: (planet_index, name, orbital radius, size, texture filename)
# planet_index corresponds to planets_info index
moons_info = [
    (2, "Moon", 25, 8, "moon.png"),          # Earth's Moon
    (3, "Phobos", 12, 6, "phobos.png"),     # Mars' moon Phobos
    (3, "Deimos", 20, 5, "deimos.png"),     # Mars' moon Deimos
]

# Load textures
def load_texture(filename):
    try:
        return pygame.image.load(os.path.join(TEXTURE_PATH, filename)).convert_alpha()
    except Exception as e:
        print(f"Failed to load {filename}: {e}")
        return None

planet_textures = [load_texture(info[4]) for info in planets_info]
moon_textures = [load_texture(moon[4]) for moon in moons_info]
sun_texture = load_texture("sun.png")

# Angles and controls
planet_angles = [0 for _ in planets_info]
moon_angles = [0 for _ in moons_info]
paused = False
speed_multiplier = 1.0
zoomed_in = False
zoom_planet_index = None
zoom_scale = 3

# Slider variables
slider_x, slider_y = 20, HEIGHT - 60  # moved left side
slider_w, slider_h = 200, 8
slider_knob_radius = 10
min_speed, max_speed = 0.1, 100.0  # max speed now 100x
dragging_slider = False

def get_orbit_position(radius, angle_deg, center):
    angle_rad = math.radians(angle_deg)
    return center[0] + radius * math.cos(angle_rad), center[1] + radius * math.sin(angle_rad)

def draw_planet(x, y, index, zoom=False, is_moon=False):
    if is_moon:
        texture = moon_textures[index]
        size = moons_info[index][3]
    else:
        texture = planet_textures[index]
        size = planets_info[index][2]

    draw_size = int(size * (zoom_scale if zoom else 1))
    if texture:
        scaled = pygame.transform.smoothscale(texture, (draw_size, draw_size))
        rect = scaled.get_rect(center=(int(x), int(y)))
        screen.blit(scaled, rect)
    else:
        pygame.draw.circle(screen, WHITE, (int(x), int(y)), draw_size // 2)

def draw_text(text, x, y, font=FONT, color=BLACK):
    render = font.render(text, True, color)
    screen.blit(render, (x, y))

def draw_slider():
    pygame.draw.rect(screen, GRAY, (slider_x, slider_y, slider_w, slider_h))
    knob_x = slider_x + int(((speed_multiplier - min_speed) / (max_speed - min_speed)) * slider_w)
    pygame.draw.circle(screen, SLIDER_COLOR, (knob_x, slider_y + slider_h // 2), slider_knob_radius)

running = True
hovered_index = None
hovered_moon_index = None

while running:
    screen.fill((10, 10, 30))

    # Draw Sun image
    if sun_texture:
        sun_img = pygame.transform.smoothscale(sun_texture, (100, 100) if not zoomed_in else (60, 60))
        rect = sun_img.get_rect(center=(center_x, center_y))
        screen.blit(sun_img, rect)
    else:
        pygame.draw.circle(screen, (255, 255, 0), (center_x, center_y), 50 if not zoomed_in else 25)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
            elif event.key == pygame.K_ESCAPE and zoomed_in:
                zoomed_in = False
                zoom_planet_index = None

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            if event.button == 1:
                if slider_x <= mx <= slider_x + slider_w and slider_y - 10 <= my <= slider_y + 20:
                    dragging_slider = True
                elif not zoomed_in:
                    for i, info in enumerate(planets_info):
                        px, py = get_orbit_position(info[1], planet_angles[i], (center_x, center_y))
                        dist = math.hypot(px - mx, py - my)
                        if dist <= info[2] / 2:
                            zoomed_in = True
                            zoom_planet_index = i
                            break

        elif event.type == pygame.MOUSEBUTTONUP:
            dragging_slider = False

        elif event.type == pygame.MOUSEMOTION and dragging_slider:
            mx, _ = event.pos
            rel_x = max(0, min(mx - slider_x, slider_w))
            speed_multiplier = min_speed + (rel_x / slider_w) * (max_speed - min_speed)

    # Update angles if not paused
    if not paused:
        for i, info in enumerate(planets_info):
            planet_angles[i] = (planet_angles[i] + info[3] * speed_multiplier) % 360
        for i, moon in enumerate(moons_info):
            # Moons orbit faster for better visual effect
            moon_angles[i] = (moon_angles[i] + speed_multiplier * 5) % 360

    # Draw orbits and planets
    if zoomed_in and zoom_planet_index is not None:
        scale_factor = 150 / planets_info[zoom_planet_index][1]

        # Draw all planet orbits scaled
        for i, info in enumerate(planets_info):
            r = info[1] * scale_factor
            pygame.draw.ellipse(screen, GRAY, (center_x - r, center_y - r, 2 * r, 2 * r), 1)

        # Draw planets scaled
        for i, info in enumerate(planets_info):
            r = info[1] * scale_factor
            x, y = get_orbit_position(r, planet_angles[i], (center_x, center_y))
            draw_planet(x, y, i, zoom=(i == zoom_planet_index))

        # Draw moons orbiting zoomed planet
        for mi, moon in enumerate(moons_info):
            if moon[0] == zoom_planet_index:
                planet_idx = moon[0]
                planet_r = planets_info[planet_idx][1]
                # Get scaled planet position
                planet_x, planet_y = get_orbit_position(planet_r * scale_factor, planet_angles[planet_idx], (center_x, center_y))
                moon_r = moon[2] * scale_factor
                x, y = get_orbit_position(moon_r, moon_angles[mi], (planet_x, planet_y))
                draw_planet(x, y, mi, zoom=True, is_moon=True)
                # Draw moon orbit ellipse around the planet
                pygame.draw.ellipse(screen, GRAY, (planet_x - moon_r, planet_y - moon_r, 2 * moon_r, 2 * moon_r), 1)

    else:
        # Normal view: draw planet orbits and planets
        for i, info in enumerate(planets_info):
            pygame.draw.ellipse(screen, GRAY, (center_x - info[1], center_y - info[1], 2 * info[1], 2 * info[1]), 1)
        for i, info in enumerate(planets_info):
            x, y = get_orbit_position(info[1], planet_angles[i], (center_x, center_y))
            draw_planet(x, y, i)

    # Hover detection for planets and moons
    mx, my = pygame.mouse.get_pos()
    hovered_index = None
    hovered_moon_index = None

    # Check moons hover if zoomed in
    if zoomed_in and zoom_planet_index is not None:
        scale_factor = 150 / planets_info[zoom_planet_index][1]
        for mi, moon in enumerate(moons_info):
            if moon[0] == zoom_planet_index:
                planet_idx = moon[0]
                planet_r = planets_info[planet_idx][1]
                planet_x, planet_y = get_orbit_position(planet_r * scale_factor, planet_angles[planet_idx], (center_x, center_y))
                moon_r = moon[2] * scale_factor
                x, y = get_orbit_position(moon_r, moon_angles[mi], (planet_x, planet_y))
                draw_size = int(moon[3] * zoom_scale)
                if math.hypot(x - mx, y - my) <= draw_size / 2:
                    hovered_moon_index = mi
                    break

    # If no moon hovered, check planets hover
    if hovered_moon_index is None:
        for i, info in enumerate(planets_info):
            radius = info[1]
            if zoomed_in and zoom_planet_index is not None:
                radius *= 150 / planets_info[zoom_planet_index][1]
            x, y = get_orbit_position(radius, planet_angles[i], (center_x, center_y))
            draw_size = int(info[2] * (zoom_scale if zoomed_in and i == zoom_planet_index else 1))
            if math.hypot(x - mx, y - my) <= draw_size / 2:
                hovered_index = i
                break

    # Draw hovered planet or moon name
    if hovered_moon_index is not None:
        moon_name = moons_info[hovered_moon_index][1]
        draw_text(moon_name, mx + 12, my + 10, font=BIGFONT, color=WHITE)
    elif hovered_index is not None:
        planet_name = planets_info[hovered_index][0]
        draw_text(planet_name, mx + 12, my + 10, font=BIGFONT, color=WHITE)

    draw_slider()
    draw_text(f"{'Paused' if paused else 'Running'} | Speed: {speed_multiplier:.1f}x", 10, 10, font=SMALL_FONT, color=WHITE)
    draw_text("Use the slider to adjust speed", 10, 40, font=SMALL_FONT, color=WHITE)
    draw_text("Click on a planet to zoom in", 10, 60, font=SMALL_FONT, color=WHITE)
    draw_text("SPACE: Pause | Click Planet: Zoom | ESC: Exit Zoom", 10, HEIGHT - 20, font=SMALL_FONT, color=WHITE)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
