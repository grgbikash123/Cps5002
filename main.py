import random
from typing import List, Tuple, Optional
import tkinter as tk
import time

from TechburgGrid import TechburgGrid
from Colors import COLORS




def main():
    root = tk.Tk()
    root.title("Techburg Simulation")

    # Create main container
    main_container = tk.Frame(root)
    main_container.pack(padx=10, pady=10)

    # Create canvas
    canvas_size = 900
    canvas = tk.Canvas(main_container, width=canvas_size, height=canvas_size, bg='white')
    canvas.pack(side=tk.LEFT)

    # Create control panel
    control_panel = tk.Frame(main_container)
    control_panel.pack(side=tk.RIGHT, padx=10)

    # Create and initialize the grid
    grid = TechburgGrid(20)
    grid.initialize_simulation(num_stations=3, num_bots=5, num_parts=10)

    # Simulation control variables
    simulation_running = tk.BooleanVar(value=False)
    delay_ms = tk.IntVar(value=500)  # Default delay of 500ms
    step_count = tk.IntVar(value=0)

    def toggle_simulation():
        simulation_running.set(not simulation_running.get())
        if simulation_running.get():
            start_button.config(text="Stop Simulation")
            update_simulation()
        else:
            start_button.config(text="Start Simulation")

    def update_simulation():
        if simulation_running.get():
            grid.simulate_step()
            grid.display_tkinter(canvas)
            root.after(delay_ms.get(), update_simulation)

    def reset_simulation():
        # Complete reset - new entities
        step_count.set(0)
        simulation_running.set(False)
        start_button.config(text="Start Simulation")

        grid.clear_entities()
        grid.initialize_simulation(num_stations=3, num_bots=5, num_parts=10)
        grid.display_tkinter(canvas)

    def restart_simulation():
        # Restart with same entities but new positions
        step_count.set(0)
        simulation_running.set(False)
        start_button.config(text="Start Simulation")
        
        # Store current counts
        num_stations = len(grid.stations)
        num_bots = len(grid.bots)
        num_parts = len(grid.parts)
        
        grid.clear_entities()
        # Reinitialize with same counts
        grid.initialize_simulation(num_stations=num_stations, 
                                 num_bots=num_bots, 
                                 num_parts=num_parts)
        grid.display_tkinter(canvas)

    # Create control buttons frame
    buttons_frame = tk.Frame(control_panel)
    buttons_frame.pack(fill="x", pady=5)

    # Create control buttons with consistent width and padding
    button_width = 12
    button_padx = 2


    # Create control buttons
    start_button = tk.Button(control_panel, text="Start Simulation", 
                           command=toggle_simulation,
                           width=20)
    start_button.pack(fill="x", pady=10)

    restart_button = tk.Button(buttons_frame, text="Restart", 
                            command=restart_simulation,
                            width=button_width)
    restart_button.pack(fill="x", pady=10)

    reset_button = tk.Button(buttons_frame, text="Reset", 
                           command=reset_simulation,
                           width=button_width)
    reset_button.pack(fill="x", pady=10)

    # Create speed control
    speed_frame = tk.LabelFrame(control_panel, text="Simulation Speed", padx=5, pady=5)
    speed_frame.pack(fill="x", pady=10)

    def update_delay_label(value):
        delay_label.config(text=f"Delay: {delay_ms.get()}ms")

    tk.Scale(speed_frame, 
            from_=100,    # Minimum delay (faster)
            to=2000,      # Maximum delay (slower)
            orient=tk.HORIZONTAL,
            variable=delay_ms,
            command=update_delay_label).pack(fill="x")
    
    delay_label = tk.Label(speed_frame, text=f"Delay: {delay_ms.get()}ms")
    delay_label.pack()

    
    # Create legend
    legend_frame = tk.LabelFrame(control_panel, text="Legend", padx=5, pady=5)
    legend_frame.pack(fill="x", pady=10)

    def create_legend_item(parent, color, text):
        frame = tk.Frame(parent)
        frame.pack(fill="x", pady=2)
        tk.Canvas(frame, width=20, height=20, bg=color).pack(side=tk.LEFT, padx=5)
        tk.Label(frame, text=text).pack(side=tk.LEFT)

    # Add legend items
    create_legend_item(legend_frame, COLORS["recharge_station"], "Recharge Station")
    create_legend_item(legend_frame, COLORS["bot"], "Survivor Bot")
    create_legend_item(legend_frame, COLORS["spare_part_small"], "Small Part")
    create_legend_item(legend_frame, COLORS["spare_part_medium"], "Medium Part")
    create_legend_item(legend_frame, COLORS["spare_part_large"], "Large Part")

    # Add statistics frame
    stats_frame = tk.LabelFrame(control_panel, text="Statistics", padx=5, pady=5)
    stats_frame.pack(fill="x", pady=10)

    bot_count = tk.StringVar(value="Bots: 5")
    parts_count = tk.StringVar(value="Parts: 10")
    stored_parts = tk.StringVar(value="Stored Parts: 0")

    tk.Label(stats_frame, textvariable=bot_count).pack(anchor="w")
    tk.Label(stats_frame, textvariable=parts_count).pack(anchor="w")
    tk.Label(stats_frame, textvariable=stored_parts).pack(anchor="w")

    def update_stats():
        total_stored = sum(len(station.stored_parts) for station in grid.stations)
        bot_count.set(f"Bots: {len(grid.bots)}")
        parts_count.set(f"Parts: {len(grid.parts)}")
        stored_parts.set(f"Stored Parts: {total_stored}")
        root.after(100, update_stats)

    # Start updating stats
    update_stats()

    # Initial display
    grid.display_tkinter(canvas)
    
    root.mainloop()

if __name__ == "__main__":
    main()