import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox, ttk
import json
import os

# --- Constants ---
TILE_SIZE = 32  # Base tile size, used for zooming
DEFAULT_WIDTH = 30
DEFAULT_HEIGHT = 20

SAVE_DIR = "maps"

# --- Tile and Entity Codes ---
FLOOR = 0
WALL = 1
EXIT = 2

# Organized tool categories
TOOL_CATEGORIES = {
    "Terrain": {
        "Floor": FLOOR,
        "Wall": WALL,
        "Exit": EXIT,
    },
    "Entities": {
        "Player Start": "player",
        "Melee Enemy": {"type": "enemy", "subtype": "melee"},
        "Ranged Enemy": {"type": "enemy", "subtype": "ranged"},
    },
    "Items": {
        "Item": {"type": "item", "subtype": None},
    },
    "Tools": {
        "Remove Enemy": "remove_enemy",
    }
}

# Keyboard shortcuts mapping
SHORTCUTS = {
    'f': FLOOR, 'w': WALL, 'e': EXIT,
    'p': "player", 'm': {"type": "enemy", "subtype": "melee"},
    'r': {"type": "enemy", "subtype": "ranged"}, 'i': {"type": "item", "subtype": None},
    'x': "remove_enemy"
}

# Brush size shortcuts
BRUSH_SHORTCUTS = {
    '1': 1, '2': 2, '3': 3, '4': 4, '5': 5
}


class CollapsibleFrame(tk.Frame):
    def __init__(self, parent, title="", **kwargs):
        super().__init__(parent, **kwargs)

        self.show = tk.BooleanVar(value=True)

        # Header frame with toggle button and title
        self.header_frame = tk.Frame(self, relief='raised', bd=1)
        self.header_frame.pack(fill='x', padx=2, pady=1)

        self.toggle_btn = tk.Button(
            self.header_frame,
            text="▼",
            command=self.toggle,
            width=2,
            relief='flat'
        )
        self.toggle_btn.pack(side='left')

        self.title_label = tk.Label(self.header_frame, text=title, font=('Arial', 9, 'bold'))
        self.title_label.pack(side='left', padx=(5, 0))

        # Content frame
        self.content_frame = tk.Frame(self)
        self.content_frame.pack(fill='both', expand=True, padx=5)

    def toggle(self):
        if self.show.get():
            self.content_frame.pack_forget()
            self.toggle_btn.config(text="▶")
            self.show.set(False)
        else:
            self.content_frame.pack(fill='both', expand=True, padx=5)
            self.toggle_btn.config(text="▼")
            self.show.set(True)


class LevelEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("RPG Level Editor")

        # Configure root grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0)

        # Multi-floor support
        self.floors = []
        self.current_floor = 0
        self.new_floor()

        self.selected_tool = FLOOR
        self.brush_size = 1  # New brush size property
        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.drag_start = None
        self.current_filename = None

        # Drawing state
        self.is_drawing = False
        self.last_draw_pos = None

        # Main layout
        self.setup_ui()

        os.makedirs(SAVE_DIR, exist_ok=True)
        self.draw()

    def setup_ui(self):
        # Canvas
        self.canvas = tk.Canvas(self.root, width=960, height=640, bg="white")
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=(5, 0), pady=5)

        # Bind canvas events
        self.canvas.bind("<Button-1>", self.start_drawing)
        self.canvas.bind("<B1-Motion>", self.continue_drawing)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drawing)
        self.canvas.bind("<MouseWheel>", self.zoom_view)
        self.canvas.bind("<B2-Motion>", self.drag_camera)
        self.canvas.bind("<ButtonPress-2>", self.start_drag)
        self.canvas.bind("<Motion>", self.show_brush_preview)  # New: brush preview
        self.root.bind("<Key>", self.key_shortcuts)

        # Right panel with scrollable content
        self.setup_right_panel()

    def setup_right_panel(self):
        # Right panel frame
        right_panel = tk.Frame(self.root, width=200, bg='lightgray')
        right_panel.grid(row=0, column=1, sticky="ns", padx=5, pady=5)
        right_panel.grid_propagate(False)

        # Scrollable area
        canvas_scroll = tk.Canvas(right_panel, bg='lightgray')
        scrollbar = ttk.Scrollbar(right_panel, orient="vertical", command=canvas_scroll.yview)
        scrollable_frame = tk.Frame(canvas_scroll, bg='lightgray')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all"))
        )

        canvas_scroll.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas_scroll.configure(yscrollcommand=scrollbar.set)

        canvas_scroll.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # File operations section
        self.create_file_section(scrollable_frame)

        # Tool categories
        self.create_tool_sections(scrollable_frame)

        # Brush size section
        self.create_brush_section(scrollable_frame)

        # Floor navigation section
        self.create_floor_section(scrollable_frame)

        # Map operations section
        self.create_map_section(scrollable_frame)

    def create_file_section(self, parent):
        file_frame = CollapsibleFrame(parent, "File")
        file_frame.pack(fill='x', pady=2)

        file_operations = [
            ("New", self.new_level),
            ("Open", self.open),
            ("Save", self.save),
            ("Save As", self.save_as),
        ]

        for text, command in file_operations:
            btn = tk.Button(file_frame.content_frame, text=text, command=command, width=15)
            btn.pack(fill='x', pady=1)

    def create_tool_sections(self, parent):
        self.tool_buttons = {}

        for category_name, tools in TOOL_CATEGORIES.items():
            category_frame = CollapsibleFrame(parent, category_name)
            category_frame.pack(fill='x', pady=2)

            for tool_name, tool_value in tools.items():
                btn = tk.Button(
                    category_frame.content_frame,
                    text=tool_name,
                    command=lambda t=tool_value: self.select_tool(t),
                    width=15,
                    relief='raised'
                )
                btn.pack(fill='x', pady=1)
                self.tool_buttons[str(tool_value)] = btn

    def create_brush_section(self, parent):
        brush_frame = CollapsibleFrame(parent, "Brush Size")
        brush_frame.pack(fill='x', pady=2)

        # Brush size info
        self.brush_info_label = tk.Label(brush_frame.content_frame, text="Size: 1x1", font=('Arial', 9))
        self.brush_info_label.pack(pady=2)

        # Brush size buttons
        brush_sizes = [1, 2, 3, 4, 5]
        brush_buttons_frame = tk.Frame(brush_frame.content_frame)
        brush_buttons_frame.pack(fill='x', pady=2)

        self.brush_buttons = {}
        for i, size in enumerate(brush_sizes):
            btn = tk.Button(
                brush_buttons_frame,
                text=f"{size}x{size}",
                command=lambda s=size: self.set_brush_size(s),
                width=4,
                relief='raised' if size != 1 else 'sunken',
                bg='SystemButtonFace' if size != 1 else 'lightblue'
            )
            btn.grid(row=0, column=i, padx=1)
            self.brush_buttons[size] = btn

        # Brush mode info
        info_label = tk.Label(brush_frame.content_frame, text="Keys 1-5: Brush size\nWorks with Floor/Wall",
                              font=('Arial', 8), fg='gray')
        info_label.pack(pady=2)

    def create_floor_section(self, parent):
        floor_frame = CollapsibleFrame(parent, "Floors")
        floor_frame.pack(fill='x', pady=2)

        # Floor info
        self.floor_info_label = tk.Label(floor_frame.content_frame, text="Floor: 1/1", font=('Arial', 9))
        self.floor_info_label.pack(pady=2)

        # Floor navigation buttons
        floor_nav_frame = tk.Frame(floor_frame.content_frame)
        floor_nav_frame.pack(fill='x', pady=2)

        tk.Button(floor_nav_frame, text="◀", command=self.prev_floor, width=4).pack(side='left')
        tk.Button(floor_nav_frame, text="▶", command=self.next_floor, width=4).pack(side='right')
        tk.Button(floor_nav_frame, text="+", command=self.add_floor, width=4).pack()

    def create_map_section(self, parent):
        map_frame = CollapsibleFrame(parent, "Map")
        map_frame.pack(fill='x', pady=2)

        tk.Button(map_frame.content_frame, text="Resize Map", command=self.resize_map, width=15).pack(fill='x', pady=1)

        # Zoom info
        self.zoom_label = tk.Label(map_frame.content_frame, text="Zoom: 100%", font=('Arial', 8))
        self.zoom_label.pack(pady=2)

    def new_floor(self):
        self.width = DEFAULT_WIDTH
        self.height = DEFAULT_HEIGHT
        grid = [[FLOOR for _ in range(self.width)] for _ in range(self.height)]
        floor_data = {
            "grid": grid,
            "player_start": None,
            "level_exit": None,
            "enemies": [],
            "items": []
        }
        self.floors.append(floor_data)

    def new_level(self):
        if messagebox.askyesno("New Level", "Create a new level? Unsaved changes will be lost."):
            self.floors = []
            self.current_floor = 0
            self.new_floor()
            self.current_filename = None
            self.zoom = 1.0
            self.offset_x = 0
            self.offset_y = 0
            self.update_ui()
            self.draw()

    def select_tool(self, tool):
        # Reset all button styles
        for btn in self.tool_buttons.values():
            btn.config(relief='raised', bg='SystemButtonFace')

        # Highlight selected tool
        tool_key = str(tool)
        if tool_key in self.tool_buttons:
            self.tool_buttons[tool_key].config(relief='sunken', bg='lightblue')

        self.selected_tool = tool

    def set_brush_size(self, size):
        # Reset all brush button styles
        for btn in self.brush_buttons.values():
            btn.config(relief='raised', bg='SystemButtonFace')

        # Highlight selected brush size
        self.brush_buttons[size].config(relief='sunken', bg='lightblue')
        self.brush_size = size
        self.update_ui()

    def key_shortcuts(self, event):
        key = event.char.lower()
        if key in SHORTCUTS:
            self.select_tool(SHORTCUTS[key])
        elif key in BRUSH_SHORTCUTS:
            self.set_brush_size(BRUSH_SHORTCUTS[key])

    def resize_map(self):
        new_width = simpledialog.askinteger("Width", "New map width:", initialvalue=self.width)
        new_height = simpledialog.askinteger("Height", "New map height:", initialvalue=self.height)
        if new_width and new_height:
            floor = self.floors[self.current_floor]
            new_grid = [[FLOOR for _ in range(new_width)] for _ in range(new_height)]
            for y in range(min(self.height, new_height)):
                for x in range(min(self.width, new_width)):
                    new_grid[y][x] = floor['grid'][y][x]
            floor['grid'] = new_grid
            self.width, self.height = new_width, new_height
            self.draw()

    def world_to_screen(self, x, y):
        size = int(TILE_SIZE * self.zoom)
        return (x * size - self.offset_x, y * size - self.offset_y)

    def screen_to_world(self, sx, sy):
        size = int(TILE_SIZE * self.zoom)
        return ((sx + self.offset_x) // size, (sy + self.offset_y) // size)

    def get_brush_tiles(self, center_x, center_y):
        """Get all tile positions affected by the current brush size"""
        tiles = []
        half_size = self.brush_size // 2

        for dy in range(-half_size, half_size + 1):
            for dx in range(-half_size, half_size + 1):
                if self.brush_size % 2 == 0:  # Even brush size
                    # Offset to make it feel more natural
                    x, y = center_x + dx, center_y + dy
                else:  # Odd brush size
                    x, y = center_x + dx, center_y + dy

                if 0 <= x < self.width and 0 <= y < self.height:
                    tiles.append((x, y))

        return tiles

    def show_brush_preview(self, event):
        """Show a preview of the brush area when hovering over the canvas"""
        if not hasattr(self, 'preview_items'):
            self.preview_items = []

        # Clear previous preview
        for item in self.preview_items:
            self.canvas.delete(item)
        self.preview_items = []

        # Only show preview for terrain tools (Floor/Wall) and when brush size > 1
        if self.selected_tool not in [FLOOR, WALL] or self.brush_size == 1:
            return

        x, y = self.screen_to_world(event.x, event.y)
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return

        size = int(TILE_SIZE * self.zoom)
        tiles = self.get_brush_tiles(x, y)

        # Draw preview rectangles
        for tile_x, tile_y in tiles:
            sx, sy = self.world_to_screen(tile_x, tile_y)
            preview_item = self.canvas.create_rectangle(
                sx + 1, sy + 1, sx + size - 1, sy + size - 1,
                outline='red', width=2, fill='', stipple='gray50'
            )
            self.preview_items.append(preview_item)

    def start_drawing(self, event):
        self.canvas.focus_set()  # Ensure canvas has focus for keyboard shortcuts
        self.is_drawing = True
        x, y = self.screen_to_world(event.x, event.y)
        self.last_draw_pos = (x, y)
        self.place_tile_at(x, y)

    def continue_drawing(self, event):
        if not self.is_drawing:
            return

        x, y = self.screen_to_world(event.x, event.y)

        # Only draw if we've moved to a different tile
        if self.last_draw_pos != (x, y):
            self.place_tile_at(x, y)
            self.last_draw_pos = (x, y)

    def stop_drawing(self, event):
        self.is_drawing = False
        self.last_draw_pos = None

    def remove_enemy_at(self, x, y):
        floor = self.floors[self.current_floor]
        # Find and remove enemy at this position
        for i, enemy in enumerate(floor['enemies']):
            if enemy['pos'] == [x, y]:
                floor['enemies'].pop(i)
                return True
        return False

    def place_tile_at(self, x, y):
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return

        floor = self.floors[self.current_floor]
        tool = self.selected_tool

        # Handle brush-based terrain tools (Floor and Wall)
        if tool in [FLOOR, WALL] and self.brush_size > 1:
            tiles = self.get_brush_tiles(x, y)
            for tile_x, tile_y in tiles:
                floor['grid'][tile_y][tile_x] = tool
            self.draw()
            return

        # Handle other tools (single tile placement)
        if tool == "remove_enemy":
            if self.remove_enemy_at(x, y):
                self.draw()
            return
        elif tool == "player":
            floor['player_start'] = [x, y]
        elif isinstance(tool, dict) and tool.get('type') == 'enemy':
            # Check if there's already an enemy at this position
            for enemy in floor['enemies']:
                if enemy['pos'] == [x, y]:
                    return  # Don't place multiple enemies on same tile
            floor['enemies'].append({"type": tool['subtype'], "pos": [x, y]})
        elif isinstance(tool, dict) and tool.get('type') == 'item':
            # Check if there's already an item at this position
            for item in floor['items']:
                if item['pos'] == [x, y]:
                    return  # Don't place multiple items on same tile
            subtype = simpledialog.askstring("Item subtype", "Enter item subtype:")
            if subtype:  # Only add if user didn't cancel
                floor['items'].append({"subtype": subtype, "pos": [x, y]})
        elif tool == EXIT:
            floor['level_exit'] = [x, y]
        elif isinstance(tool, int):
            floor['grid'][y][x] = tool

        self.draw()

    def draw(self):
        self.canvas.delete("all")
        size = int(TILE_SIZE * self.zoom)
        floor = self.floors[self.current_floor]

        # Draw grid
        for y in range(self.height):
            for x in range(self.width):
                sx, sy = self.world_to_screen(x, y)
                print(f"x- {x} y- {y}")
                print(f"width {self.width} height {self.height}")
                tile = floor['grid'][y][x]
                color = 'white' if tile == FLOOR else 'black' if tile == WALL else 'green' if tile == EXIT else 'white'
                self.canvas.create_rectangle(sx, sy, sx + size, sy + size, fill=color, outline='gray')

        # Draw player start
        ps = floor['player_start']
        if ps:
            sx, sy = self.world_to_screen(*ps)
            self.canvas.create_oval(sx + 4, sy + 4, sx + size - 4, sy + size - 4, fill='blue')

        # Draw level exit
        ex = floor['level_exit']
        if ex:
            sx, sy = self.world_to_screen(*ex)
            self.canvas.create_oval(sx + 6, sy + 6, sx + size - 6, sy + size - 6, outline='yellow', width=3)

        # Draw enemies
        for e in floor['enemies']:
            sx, sy = self.world_to_screen(*e['pos'])
            c = 'red' if e['type'] == 'melee' else 'orange'
            self.canvas.create_rectangle(sx + 8, sy + 8, sx + size - 8, sy + size - 8, fill=c)

        # Draw items
        for it in floor['items']:
            sx, sy = self.world_to_screen(*it['pos'])
            self.canvas.create_text(sx + size // 2, sy + size // 2, text='I',
                                    font=('Arial', int(12 * self.zoom), 'bold'))

        self.update_ui()

    def update_ui(self):
        # Update floor info
        if hasattr(self, 'floor_info_label'):
            self.floor_info_label.config(text=f"Floor: {self.current_floor + 1}/{len(self.floors)}")

        # Update zoom info
        if hasattr(self, 'zoom_label'):
            self.zoom_label.config(text=f"Zoom: {int(self.zoom * 100)}%")

        # Update brush info
        if hasattr(self, 'brush_info_label'):
            self.brush_info_label.config(text=f"Size: {self.brush_size}x{self.brush_size}")

    def zoom_view(self, event):
        factor = 1.1 if event.delta > 0 else 0.9
        old = self.zoom
        self.zoom *= factor
        self.zoom = max(0.2, min(5.0, self.zoom))
        mx, my = event.x + self.offset_x, event.y + self.offset_y
        scale = self.zoom / old
        self.offset_x = int(mx * scale - event.x)
        self.offset_y = int(my * scale - event.y)
        self.draw()

    def start_drag(self, event):
        self.drag_start = (event.x, event.y)

    def drag_camera(self, event):
        if self.drag_start:
            dx, dy = event.x - self.drag_start[0], event.y - self.drag_start[1]
            self.offset_x -= dx
            self.offset_y -= dy
            self.drag_start = (event.x, event.y)
            self.draw()

    # --- Multi-floor management ---
    def add_floor(self):
        self.new_floor()
        self.current_floor = len(self.floors) - 1
        self.draw()

    def prev_floor(self):
        if self.current_floor > 0:
            self.current_floor -= 1
            self.update_size()
            self.draw()

    def next_floor(self):
        if self.current_floor < len(self.floors) - 1:
            self.current_floor += 1
            self.update_size()
            self.draw()

    # --- File I/O ---
    def save_as(self):
        path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON Files', '*.json')])
        if not path:
            return
        self.current_filename = path
        self.save()

    def save(self):
        if not self.current_filename:
            self.current_filename = os.path.join(SAVE_DIR, 'level.json')
        data = {'floors': self.floors}
        with open(self.current_filename, 'w') as f:
            json.dump(data, f, indent=2)
        messagebox.showinfo('Saved', f'Level saved to {self.current_filename}')

    def open(self):
        path = filedialog.askopenfilename(filetypes=[('JSON Files', '*.json')])
        if not path:
            return
        with open(path) as f:
            data = json.load(f)
        self.floors = data.get('floors', [])
        self.current_floor = 0
        first = self.floors[0]
        self.width = len(first['grid'][0])
        self.height = len(first['grid'])
        self.current_filename = path
        self.draw()

    def update_size(self):
        floor = self.floors[self.current_floor]["grid"]
        print(self.width, self.height)
        self.width = floor.__len__()
        self.height = floor[0].__len__()


if __name__ == '__main__':
    root = tk.Tk()
    app = LevelEditor(root)
    root.mainloop()