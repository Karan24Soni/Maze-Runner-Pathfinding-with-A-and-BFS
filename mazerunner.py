import asyncio
import pygame
import random
import colorsys
import heapq


FPS = 30
MAZE_WIDTH = 100
MAZE_HEIGHT = 100
CELL_SIZE = 8
WINDOW_WIDTH = MAZE_WIDTH * CELL_SIZE
WINDOW_HEIGHT = MAZE_HEIGHT * CELL_SIZE
BG_COLOR = (10, 10, 21)      # Dark background
WALL_COLOR = (255, 255, 255) # White
CURRENT_COLOR = (255, 20, 147)# Pink
GENERATION_PARTICLE = (0, 255, 127) # Spring Green
SOLVING_PARTICLE = (30, 144, 255)  # Dodger Blue
VISITED_COLOR = (58, 28, 113)      # Dark Purple
PATH_COLOR = (255, 51, 51)         # Red
START_COLOR = (0, 255, 127)        # Spring Green
END_COLOR = (255, 69, 0)           # Orange Red
PARTICLE_LIFETIME = 10
PARTICLE_SIZE = 1.0
PULSE_SPEED = 0.15

class Particle:
    def __init__(self, x, y, color, size=PARTICLE_SIZE, lifetime=PARTICLE_LIFETIME, velocity=(0, 0)):
        self.x = x
        self.y = y
        self.original_color = color
        self.color = color
        self.size = size * random.uniform(0.8, 1.2)
        self.max_lifetime = lifetime
        self.lifetime = lifetime
        self.decay = 0.85
        self.vx = velocity[0] * random.uniform(0.5, 1.5)
        self.vy = velocity[1] * random.uniform(0.5, 1.5)

    def update(self):
        self.lifetime -= 1
        self.size *= self.decay
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.9
        self.vy *= 0.9
        alpha = self.lifetime / self.max_lifetime
        r, g, b = self.original_color
        self.color = (r, g, b, alpha)
        return self.lifetime > 0 and self.size > 0.1

class GlowParticle(Particle):
    def __init__(self, x, y, color, size=PARTICLE_SIZE * 1.5, lifetime=PARTICLE_LIFETIME * 1.2):
        super().__init__(x, y, color, size, lifetime)
        self.decay = 0.92
        self.pulsate = True
        self.pulse_speed = random.uniform(0.1, 0.2)
        self.pulse_amplitude = random.uniform(0.05, 0.15)
        self.time = random.uniform(0, 2 * 3.14159)

    def update(self):
        self.lifetime -= 1
        if self.pulsate:
            self.time += self.pulse_speed
            pulse_factor = 1.0 + self.pulse_amplitude * (self.time % (2 * 3.14159))
            self.size *= self.decay * pulse_factor
        else:
            self.size *= self.decay
        alpha = self.lifetime / self.max_lifetime
        r, g, b = self.original_color
        self.color = (r, g, b, alpha)
        return self.lifetime > 0 and self.size > 0.1

class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.walls = {'N': True, 'E': True, 'S': True, 'W': True}
        self.visited = False
        self.in_path = False
        self.is_start = False
        self.is_end = False
        self.is_frontier = False
        self.generation_order = -1
        self.distance = float('inf')

def create_gradient_color(order, total):
    if order < 0:
        return (26, 26, 51)
    norm_pos = min(1.0, order / total)
    h1, s1, v1 = 0.11, 0.9, 0.8
    h2, s2, v2 = 0.65, 0.85, 0.9
    h = h1 + (h2 - h1) * norm_pos
    s = s1 + (s2 - s1) * norm_pos
    v = v1 + (v2 - v1) * norm_pos
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))

def draw_maze(grid, screen, particles, current_x, current_y, total_cells, generation_phase):
    screen.fill(BG_COLOR)
    for x in range(len(grid)):
        for y in range(len(grid[0])):
            cell = grid[x][y]
            cell_x = x * CELL_SIZE
            cell_y = y * CELL_SIZE
            if cell.is_start:
                color = START_COLOR
            elif cell.is_end:
                color = END_COLOR
            elif cell.in_path and not generation_phase:
                color = PATH_COLOR
            elif cell.visited:
                color = create_gradient_color(cell.generation_order, total_cells) if generation_phase else VISITED_COLOR
            elif cell.is_frontier and generation_phase:
                color = (170, 170, 255)
            else:
                color = BG_COLOR
            pygame.draw.rect(screen, color, (cell_x, cell_y, CELL_SIZE, CELL_SIZE))
            wall_width = 1
            if cell.walls['N']:
                pygame.draw.line(screen, WALL_COLOR, (cell_x, cell_y), (cell_x + CELL_SIZE, cell_y), wall_width)
            if cell.walls['E']:
                pygame.draw.line(screen, WALL_COLOR, (cell_x + CELL_SIZE, cell_y), (cell_x + CELL_SIZE, cell_y + CELL_SIZE), wall_width)
            if cell.walls['S']:
                pygame.draw.line(screen, WALL_COLOR, (cell_x, cell_y + CELL_SIZE), (cell_x + CELL_SIZE, cell_y + CELL_SIZE), wall_width)
            if cell.walls['W']:
                pygame.draw.line(screen, WALL_COLOR, (cell_x, cell_y), (cell_x, cell_y + CELL_SIZE), wall_width)
            if x == current_x and y == current_y:
                pygame.draw.rect(screen, CURRENT_COLOR, (cell_x + 1, cell_y + 1, CELL_SIZE - 2, CELL_SIZE - 2))
    new_particles = []
    for particle in particles:
        if particle.update():
            new_particles.append(particle)
            alpha = int(particle.lifetime / particle.max_lifetime * 255)
            color = particle.color[:3] + (alpha,)
            pygame.draw.circle(screen, color, (int(particle.x), int(particle.y)), int(particle.size * CELL_SIZE / 10))
    particles[:] = new_particles

async def create_maze_prim(width, height, screen, clock):
    print("Generating maze...")
    grid = [[Cell(x, y) for y in range(height)] for x in range(width)]
    particles = []
    start_x, start_y = random.randint(0, width - 1), random.randint(0, height - 1)
    grid[start_x][start_y].visited = True
    grid[start_x][start_y].generation_order = 0
    frontier = []
    directions = [('N', 0, -1), ('E', 1, 0), ('S', 0, 1), ('W', -1, 0)]
    opposite = {'N': 'S', 'E': 'W', 'S': 'N', 'W': 'E'}
    for dir_name, dx, dy in directions:
        nx, ny = start_x + dx, start_y + dy
        if 0 <= nx < width and 0 <= ny < height:
            grid[nx][ny].is_frontier = True
            frontier.append((nx, ny))
    cells_added = 1
    while frontier:
        fx, fy = random.choice(frontier)
        frontier.remove((fx, fy))
        grid[fx][fy].is_frontier = False
        neighbors = []
        for dir_name, dx, dy in directions:
            nx, ny = fx + dx, fy + dy
            if 0 <= nx < width and 0 <= ny < height and grid[nx][ny].visited:
                neighbors.append((nx, ny, dir_name))
        if neighbors:
            nx, ny, dir_name = random.choice(neighbors)
            grid[fx][fy].walls[dir_name] = False
            grid[nx][ny].walls[opposite[dir_name]] = False
            grid[fx][fy].visited = True
            grid[fx][fy].generation_order = cells_added
            cells_added += 1
            for dir_name, dx, dy in directions:
                nnx, nny = fx + dx, fy + dy
                if 0 <= nnx < width and 0 <= nny < height and not grid[nnx][nny].visited and not grid[nnx][nny].is_frontier:
                    grid[nnx][nny].is_frontier = True
                    frontier.append((nnx, nny))
            draw_maze(grid, screen, particles, fx, fy, cells_added, generation_phase=True)
            for _ in range(random.randint(2, 4)):
                vel_x, vel_y = random.uniform(-0.02, 0.02), random.uniform(-0.02, 0.02)
                particles.append(Particle(
                    fx * CELL_SIZE + CELL_SIZE / 2,
                    fy * CELL_SIZE + CELL_SIZE / 2,
                    GENERATION_PARTICLE,
                    velocity=(vel_x, vel_y)
                ))
            pygame.display.flip()
            clock.tick(FPS)
            await asyncio.sleep(0.005)
    entrance_x = random.randint(1, width - 2)
    exit_x = random.randint(1, width - 2)
    grid[entrance_x][0].walls['N'] = False
    grid[exit_x][height - 1].walls['S'] = False
    grid[entrance_x][0].is_start = True
    grid[exit_x][height - 1].is_end = True
    print("Maze generated.")
    return grid, (entrance_x, 0), (exit_x, height - 1), particles

async def solve_maze_astar(grid, start_pos, end_pos, screen, clock, particles):
    print("Solving maze with A*...")
    width, height = len(grid), len(grid[0])
    start_x, start_y = start_pos
    end_x, end_y = end_pos
    for x in range(width):
        for y in range(height):
            grid[x][y].visited = False
            grid[x][y].in_path = False
            grid[x][y].distance = float('inf')
    grid[start_x][start_y].distance = 0
    pq = [(0, 0, start_pos)]
    came_from = {}
    visited = set()
    directions = [('N', 0, -1), ('E', 1, 0), ('S', 0, 1), ('W', -1, 0)]
    while pq:
        f_score, g_score, current_pos = heapq.heappop(pq)
        x, y = current_pos
        if current_pos in visited:
            continue
        visited.add(current_pos)
        grid[x][y].visited = True
        if current_pos == end_pos:
            path = []
            pos = end_pos
            while pos in came_from:
                path.append(pos)
                grid[pos[0]][pos[1]].in_path = True
                pos = came_from[pos]
            path.append(start_pos)
            path.reverse()
            for px, py in path:
                grid[px][py].in_path = True
                draw_maze(grid, screen, particles, px, py, len(visited), generation_phase=False)
                for _ in range(random.randint(1, 3)):
                    particles.append(GlowParticle(
                        px * CELL_SIZE + CELL_SIZE / 2,
                        py * CELL_SIZE + CELL_SIZE / 2,
                        PATH_COLOR
                    ))
                pygame.display.flip()
                clock.tick(FPS)
                await asyncio.sleep(0.05)
            print("Path found.")
            break
        for dir_name, dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                if not grid[x][y].walls[dir_name]:
                    new_g_score = g_score + 1
                    if new_g_score < grid[nx][ny].distance:
                        grid[nx][ny].distance = new_g_score
                        came_from[(nx, ny)] = (x, y)
                        h_score = abs(end_x - nx) + abs(end_y - ny)
                        f_score = new_g_score + h_score
                        heapq.heappush(pq, (f_score, new_g_score, (nx, ny)))
        draw_maze(grid, screen, particles, x, y, len(visited), generation_phase=False)
        for _ in range(random.randint(2, 4)):
            vel_x, vel_y = random.uniform(-0.02, 0.02), random.uniform(-0.02, 0.02)
            particles.append(Particle(
                x * CELL_SIZE + CELL_SIZE / 2,
                y * CELL_SIZE + CELL_SIZE / 2,
                SOLVING_PARTICLE,
                velocity=(vel_x, vel_y)
            ))
        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(0.005)
    print("Solving complete.")
    return particles

async def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Aesthetic Maze Solver")
    clock = pygame.time.Clock()
    particles = []
    print("Starting program...")
    grid, start_pos, end_pos, particles = await create_maze_prim(MAZE_WIDTH, MAZE_HEIGHT, screen, clock)
    print("Press spacebar to solve...")
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("User quit.")
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
        draw_maze(grid, screen, particles, -1, -1, MAZE_WIDTH * MAZE_HEIGHT, generation_phase=False)
        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(0)
    particles = await solve_maze_astar(grid, start_pos, end_pos, screen, clock, particles)
    print("Keeping window open...")
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        draw_maze(grid, screen, particles, -1, -1, MAZE_WIDTH * MAZE_HEIGHT, generation_phase=False)
        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(0)
    print("Exiting.")
    pygame.quit()

try:
    loop = asyncio.get_running_loop()
    loop.create_task(main())
except RuntimeError:
    asyncio.run(main())