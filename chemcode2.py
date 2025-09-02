import pygame
import math

pygame.init()

WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Covalent Bond Learning")

FONT = pygame.font.SysFont(None, 20)
BIGFONT = pygame.font.SysFont(None, 40)
INSTRUCTION_FONT = pygame.font.SysFont(None, 24)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (230, 230, 230)
BLUE = (100, 100, 255)
RED = (255, 100, 100)
GREEN = (100, 255, 100)
YELLOW = (255, 255, 100)
DARKBLUE = (0, 0, 150)
PURPLE = (180, 100, 240)

ELEMENTS = [
    ("H", 1, 1, 1),
    ("He", 18, 1, 2),
    ("Li", 1, 2, 1),
    ("Be", 2, 2, 2),
    ("B", 13, 2, 3),
    ("C", 14, 2, 4),
    ("N", 15, 2, 5),
    ("O", 16, 2, 6),
    ("F", 17, 2, 7),
    ("Ne", 18, 2, 8),
    ("Na", 1, 3, 1),
    ("Mg", 2, 3, 2),
    ("Al", 13, 3, 3),
    ("Si", 14, 3, 4),
    ("P", 15, 3, 5),
    ("S", 16, 3, 6),
    ("Cl", 17, 3, 7),
    ("Ar", 18, 3, 8),
    ("K", 1, 4, 1),
    ("Ca", 2, 4, 2),
]

CELL_SIZE = 40
TABLE_ORIGIN = (20, 20)

def element_pos(group, period):
    x = TABLE_ORIGIN[0] + (group - 1) * CELL_SIZE
    y = TABLE_ORIGIN[1] + (period - 1) * CELL_SIZE
    return (x, y)

def rotate_point(cx, cy, px, py, angle_rad):
    """Rotate point (px,py) around center (cx,cy) by angle_rad."""
    s, c = math.sin(angle_rad), math.cos(angle_rad)
    dx, dy = px - cx, py - cy
    nx = dx * c - dy * s + cx
    ny = dx * s + dy * c + cy
    return (nx, ny)

class ElectronDot:
    def __init__(self, element, side, position_in_side, paired=False, radius=20):
        self.element = element
        self.side = side
        self.pos_in_side = position_in_side
        self.radius = radius
        self.paired = paired
        self.connected_to = None
        self.position = (0, 0)
        self.update_position()
    
    def update_position(self):
        cx, cy = self.element.center
        r = self.radius
        offset = 12
        
        # base electron position before rotation (local to element center)
        if self.side == 0:  # top
            base_x = cx
            base_y = cy - r
            local_pos = (base_x, base_y)
        elif self.side == 1:  # right
            base_x = cx + r
            base_y = cy
            local_pos = (base_x, base_y)
        elif self.side == 2:  # bottom
            base_x = cx
            base_y = cy + r
            local_pos = (base_x, base_y)
        else:  # left
            base_x = cx - r
            base_y = cy
            local_pos = (base_x, base_y)
        
        # Rotate local_pos around center by element.rotation (radians)
        angle = math.radians(self.element.rotation)
        self.position = rotate_point(cx, cy, local_pos[0], local_pos[1], angle)
    
    def draw(self, surface, highlight=False):
        if self.paired:
            color = DARKBLUE
            radius = 6
        else:
            color = RED if self.connected_to else (YELLOW if highlight else BLUE)
            radius = 8
        
        pygame.draw.circle(surface, color, (int(self.position[0]), int(self.position[1])), radius)
        pygame.draw.circle(surface, BLACK, (int(self.position[0]), int(self.position[1])), radius, 1)
    
    def is_hovered(self, pos):
        x, y = pos
        px, py = self.position
        return math.hypot(x - px, y - py) < 10
    
    def can_connect(self):
        return self.connected_to is None and not self.paired

class ElementDisplay:
    def __init__(self, symbol, valence_electrons, pos):
        self.symbol = symbol
        self.valence = valence_electrons
        self.center = list(pos)
        self.radius = 30
        self.rotation = 0  # degrees, 0 = normal
        self.electrons = []
        self.selected = False
        self.dragging = False
        self.drag_offset = (0, 0)
        self.create_electrons()
    
    def create_electrons(self):
        self.electrons.clear()
        
        # Carbon group elements (C, Si) get one electron on each side
        if self.valence == 4:
            for side in range(4):  # top, right, bottom, left
                self.electrons.append(ElectronDot(self, side, 0, paired=False))
            return
        
        # Aluminum group elements (B, Al) - 3 valence electrons
        if self.valence == 3:
            for side in range(3):  # top, right, bottom
                self.electrons.append(ElectronDot(self, side, 0, paired=False))
            return
            
        # Magnesium group elements (Be, Mg) - 2 valence electrons
        if self.valence == 2:
            for side in range(2):  # top, right
                self.electrons.append(ElectronDot(self, side, 0, paired=False))
            return
            
        # Other elements follow standard rules
        sides = [0, 1, 2, 3]  # top, right, bottom, left
        
        pairs_needed = self.valence // 2
        singles_needed = self.valence % 2
        
        count = 0
        for side in sides:
            if pairs_needed > 0:
                self.electrons.append(ElectronDot(self, side, 0, paired=True))
                pairs_needed -= 1
                count += 1
            elif singles_needed > 0:
                self.electrons.append(ElectronDot(self, side, 0, paired=False))
                singles_needed -= 1
                count += 1
            if count >= self.valence:
                break
    
    def draw(self, surface):
        pygame.draw.circle(surface, GREEN if self.selected else LIGHT_GRAY, self.center, self.radius)
        pygame.draw.circle(surface, BLACK, self.center, self.radius, 2)
        text = BIGFONT.render(self.symbol, True, BLACK)
        rect = text.get_rect(center=self.center)
        surface.blit(text, rect)
        for e in self.electrons:
            e.draw(surface)
    
    def is_hovered(self, pos):
        x, y = pos
        cx, cy = self.center
        return math.hypot(x - cx, y - cy) < self.radius + 5
    
    def update_electron_positions(self):
        for e in self.electrons:
            e.update_position()
    
    def rotate_to_align_bond(self, bonded_electron):
        """Rotate element so bonded_electron points toward bonded element center."""
        other_element = bonded_electron.connected_to.element
        cx, cy = self.center
        ocx, ocy = other_element.center
        
        # Angle from this element to other element
        dx = ocx - cx
        dy = ocy - cy
        angle_to_other = math.degrees(math.atan2(dy, dx))
        
        # Electron sides (0=top,1=right,2=bottom,3=left), each side is 90 degrees apart starting at -90 deg for top
        # We want to rotate element so the electron's side faces angle_to_other.
        
        # Electron base angle by side:
        side_angles = {0: -90, 1: 0, 2: 90, 3: 180}
        electron_base_angle = side_angles[bonded_electron.side]
        
        # Calculate needed rotation
        # After rotation, electron_base_angle + rotation should equal angle_to_other
        needed_rotation = angle_to_other - electron_base_angle
        
        self.rotation = needed_rotation
        self.update_electron_positions()

def draw_periodic_table(surface):
    # Draw table background
    pygame.draw.rect(surface, LIGHT_GRAY, (TABLE_ORIGIN[0]-10, TABLE_ORIGIN[1]-10, 
                                          CELL_SIZE*18 + 20, CELL_SIZE*4 + 20))
    pygame.draw.rect(surface, BLACK, (TABLE_ORIGIN[0]-10, TABLE_ORIGIN[1]-10, 
                                     CELL_SIZE*18 + 20, CELL_SIZE*4 + 20), 2)
    
    for sym, group, period, valence in ELEMENTS:
        x, y = element_pos(group, period)
        rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, GRAY, rect)
        pygame.draw.rect(surface, BLACK, rect, 1)
        text = FONT.render(sym, True, BLACK)
        text_rect = text.get_rect(center=rect.center)
        surface.blit(text, text_rect)

def find_element_at_pos(pos):
    mx, my = pos
    for sym, group, period, valence in ELEMENTS:
        x, y = element_pos(group, period)
        rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
        if rect.collidepoint(mx, my):
            return sym, valence
    return None, None

def draw_connection(surface, dot1, dot2):
    x1, y1 = dot1.position
    x2, y2 = dot2.position
    pygame.draw.line(surface, PURPLE, (x1, y1), (x2, y2), 3)

def draw_instructions(surface):
    instructions = [
        "Click on an element to add it to the workspace",
        "Drag from an electron to form a bond with another element",
        "Drag elements to reposition them",
        "Right-click to remove an element"
    ]
    
    y_pos = HEIGHT - 120
    for instruction in instructions:
        text = INSTRUCTION_FONT.render(instruction, True, BLACK)
        surface.blit(text, (20, y_pos))
        y_pos += 25

def main():
    clock = pygame.time.Clock()
    running = True
    
    summoned_elements = []
    
    dragging_dot = None
    drag_line_start = None
    drag_line_end = None
    
    dragging_element = None
    drag_offset = (0, 0)
    
    connections = []
    
    while running:
        screen.fill(WHITE)
        
        draw_periodic_table(screen)
        draw_instructions(screen)
        
        for d1, d2 in connections:
            draw_connection(screen, d1, d2)
        
        for el in summoned_elements:
            el.draw(screen)
        
        mx, my = pygame.mouse.get_pos()
        
        # Highlight hovered electrons
        for el in summoned_elements:
            for e_dot in el.electrons:
                if e_dot.is_hovered((mx, my)) and e_dot.can_connect():
                    e_dot.draw(screen, highlight=True)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                clicked_dot = None
                clicked_element = None
                
                if event.button == 1:  # Left click
                    for el in summoned_elements:
                        for e_dot in el.electrons:
                            if e_dot.is_hovered((mx, my)) and e_dot.can_connect():
                                clicked_dot = e_dot
                                break
                        if clicked_dot:
                            break
                    
                    if not clicked_dot:
                        for el in reversed(summoned_elements):
                            if el.is_hovered((mx, my)):
                                clicked_element = el
                                break
                    
                    if clicked_dot:
                        dragging_dot = clicked_dot
                        drag_line_start = dragging_dot.position
                        drag_line_end = (mx, my)
                        if dragging_dot.connected_to:
                            other_dot = dragging_dot.connected_to
                            dragging_dot.connected_to = None
                            other_dot.connected_to = None
                            connections = [c for c in connections if dragging_dot not in c and other_dot not in c]
                    
                    elif clicked_element:
                        dragging_element = clicked_element
                        dragging_element.dragging = True
                        drag_offset = (dragging_element.center[0] - mx, dragging_element.center[1] - my)
                        summoned_elements.remove(dragging_element)
                        summoned_elements.append(dragging_element)
                    
                    else:
                        sym, valence = find_element_at_pos((mx, my))
                        if sym:
                            new_x = 800
                            new_y = 50 + len(summoned_elements) * 100
                            if not any(e.symbol == sym for e in summoned_elements):
                                summoned_elements.append(ElementDisplay(sym, valence, (new_x, new_y)))
                
                elif event.button == 3:  # Right click
                    for el in reversed(summoned_elements):
                        if el.is_hovered((mx, my)):
                            # Remove any connections to this element
                            for e_dot in el.electrons:
                                if e_dot.connected_to:
                                    other_dot = e_dot.connected_to
                                    e_dot.connected_to = None
                                    other_dot.connected_to = None
                                    connections = [c for c in connections if e_dot not in c and other_dot not in c]
                            summoned_elements.remove(el)
                            break
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and dragging_dot:
                    target_dot = None
                    for el in summoned_elements:
                        if el != dragging_dot.element:
                            for e_dot in el.electrons:
                                if e_dot.is_hovered((mx, my)) and e_dot.can_connect():
                                    target_dot = e_dot
                                    break
                            if target_dot:
                                break
                    
                    if target_dot and dragging_dot.can_connect():
                        dragging_dot.connected_to = target_dot
                        target_dot.connected_to = dragging_dot
                        connections.append((dragging_dot, target_dot))
                        # Rotate elements to face bond electrons
                        dragging_dot.element.rotate_to_align_bond(dragging_dot)
                        target_dot.element.rotate_to_align_bond(target_dot)
                    
                    dragging_dot = None
                    drag_line_start = None
                    drag_line_end = None
                
                if dragging_element:
                    dragging_element.dragging = False
                    dragging_element = None
            
            elif event.type == pygame.MOUSEMOTION:
                if dragging_dot:
                    drag_line_end = (mx, my)
                
                if dragging_element and dragging_element.dragging:
                    dragging_element.center[0] = mx + drag_offset[0]
                    dragging_element.center[1] = my + drag_offset[1]
                    dragging_element.update_electron_positions()
        
        if dragging_dot and drag_line_start and drag_line_end:
            pygame.draw.line(screen, RED, drag_line_start, drag_line_end, 3)
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
    pygame.quit()