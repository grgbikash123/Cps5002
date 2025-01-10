import random
from typing import List, Tuple, Optional
import tkinter as tk
import time

from TechburgGrid import TechburgGrid
from Colors import COLORS


class SimulationState:
    def __init__(self, stations, bots, parts, drones, swarms, step_count):
        self.stations = [(s.x, s.y, [p for p in s.stored_parts]) for s in stations]
        self.bots = [(b.x, b.y, b.energy, b.carried_part) for b in bots]
        self.parts = [(p.x, p.y, p.size) for p in parts]
        self.drones = [(d.x, d.y, d.energy, d.is_hibernating) for d in drones]
        self.swarms = [(s.x, s.y, s.size, s.consumed_material) for s in swarms]
        self.step_count = step_count

def main():
    root = tk.Tk()
    root.title("Techburg Simulation")

    # simulation parameters
    GRID_SIZE = 30
    NUM_STATIONS = 4
    NUM_BOTS = 6
    NUM_PARTS = 15
    NUM_DRONES = 8
    NUM_SWARMS = 7

    # history lists for both backward and forward states
    MAX_HISTORY = 10  # number of steps upto which it is to be recorded
    backward_history = []
    forward_history = []

    main_container = tk.Frame(root)
    main_container.pack(padx=10, pady=10)

    # size of tkinter canvas
    canvas_size = 1000
    canvas = tk.Canvas(main_container, width=canvas_size, height=canvas_size, bg='white')
    canvas.pack(side=tk.LEFT)

    # control panel
    control_panel = tk.Frame(main_container)
    control_panel.pack(side=tk.RIGHT, padx=10)

    grid = TechburgGrid(GRID_SIZE)
    grid.initialize_simulation(
        num_stations=NUM_STATIONS,
        num_bots=NUM_BOTS,
        num_parts=NUM_PARTS,
        num_drones=NUM_DRONES,
        num_swarms=NUM_SWARMS
    )

    simulation_running = tk.BooleanVar(value=False)
    delay_ms = tk.IntVar(value=500)  # default delay of between each simulation steps (500ms)
    step_count = tk.IntVar(value=0)  # step counter


    def save_current_state():
        """Save current state to backward history"""
        if len(backward_history) >= MAX_HISTORY:   # if the backward history is full then remove the oldest one
            backward_history.pop(0)
        current_state = SimulationState(
            grid.stations, 
            grid.bots, 
            grid.parts, 
            grid.drones,
            grid.swarms,
            step_count.get()
            )
        backward_history.append(current_state)
        forward_history.clear()

    def toggle_simulation():
        simulation_running.set(not simulation_running.get())
        if simulation_running.get():
            start_button.config(text="Stop Simulation")
            update_simulation()
        else:
            start_button.config(text="Start Simulation")

    def update_simulation():
        if simulation_running.get():
            save_current_state()  # record the current simulation state
            grid.simulate_step()
            step_count.set(step_count.get() + 1)
            grid.display_tkinter(canvas)

            # Update button states
            step_back_button.config(state='normal' if backward_history else 'disabled')
            step_forward_button.config(state='normal' if forward_history else 'disabled')
            root.after(delay_ms.get(), update_simulation)

    def reset_simulation():
        # reset the simulation with new entities 
        step_count.set(0)
        simulation_running.set(False)
        start_button.config(text="Start Simulation")

        grid.clear_entities()
        grid.initialize_simulation(
            num_stations=NUM_STATIONS,
            num_bots=NUM_BOTS,
            num_parts=NUM_PARTS,
            num_drones=NUM_DRONES,
            num_swarms=NUM_SWARMS
        )
        grid.display_tkinter(canvas)

    def step_back():
        """Move one step backward in simulation"""
        if not backward_history:
            return
        
        # stop simulation if running
        simulation_running.set(False)
        start_button.config(text="Start Simulation")
        
        # save current state to forward history
        current_state = SimulationState(
            grid.stations,
            grid.bots,
            grid.parts,
            grid.drones,
            grid.swarms,
            step_count.get()
            )
        if len(forward_history) >= MAX_HISTORY:
            forward_history.pop(0)
        forward_history.append(current_state)
        
        # restore previous state
        previous_state = backward_history.pop()
        grid.clear_entities()
        grid.restore_from_state(previous_state)
        step_count.set(previous_state.step_count)
        grid.display_tkinter(canvas)
        
        # update button states
        step_back_button.config(state='normal' if backward_history else 'disabled')
        step_forward_button.config(state='normal' if forward_history else 'disabled')

    def step_forward():
        """Move one step forward in simulation"""
        if not forward_history:
            return
        
        # stop simulation if running
        simulation_running.set(False)
        start_button.config(text="Start Simulation")
        
        # save current state to backward history
        current_state = SimulationState(
            grid.stations,
            grid.bots,
            grid.parts,
            grid.drones,
            grid.swarms,
            step_count.get()
            )
        if len(backward_history) >= MAX_HISTORY:
            backward_history.pop(0)
        backward_history.append(current_state)
        
        # restore next state
        next_state = forward_history.pop()
        grid.clear_entities()
        grid.restore_from_state(next_state)
        step_count.set(next_state.step_count)
        grid.display_tkinter(canvas)
        
        # update button states
        step_back_button.config(state='normal' if backward_history else 'disabled')
        step_forward_button.config(state='normal' if forward_history else 'disabled')


    # create control buttons frame
    buttons_frame = tk.Frame(control_panel)
    buttons_frame.pack(fill="x", pady=5)

    # variables for control buttons with consistent width and padding
    button_width = 12
    button_padx = 2

    # add step back and forward buttons
    step_back_button = tk.Button(buttons_frame, 
                                text="← Step Back", 
                                command=step_back,
                                width=button_width,
                                state='disabled')
    step_back_button.pack(fill="x", pady=10)

    step_forward_button = tk.Button(buttons_frame, 
                                   text="Step Forward →", 
                                   command=step_forward,
                                   width=button_width,
                                   state='disabled')
    step_forward_button.pack(fill="x", pady=10)


    # control buttons
    start_button = tk.Button(control_panel, text="Start Simulation", 
                           command=toggle_simulation,
                           width=20)
    start_button.pack(fill="x", pady=10)

    reset_button = tk.Button(buttons_frame, text="Reset", 
                           command=reset_simulation,
                           width=button_width)
    reset_button.pack(fill="x", pady=10)

    # speed control
    speed_frame = tk.LabelFrame(control_panel, text="Simulation Speed", padx=5, pady=5)
    speed_frame.pack(fill="x", pady=10)

    def update_delay_label(value):
        delay_label.config(text=f"Delay: {delay_ms.get()}ms")

    tk.Scale(speed_frame, 
            from_=100,    # mimium delay between simulation step (faster)
            to=2000,      # maximum delay between simulation step (slower)
            orient=tk.HORIZONTAL,
            variable=delay_ms,
            command=update_delay_label).pack(fill="x")
    
    delay_label = tk.Label(speed_frame, text=f"Delay: {delay_ms.get()}ms")
    delay_label.pack()

    
    # legend
    legend_frame = tk.LabelFrame(control_panel, text="Legend", padx=5, pady=5)
    legend_frame.pack(fill="x", pady=10)

    def create_legend_item(parent, color, text):
        frame = tk.Frame(parent)
        frame.pack(fill="x", pady=2)
        tk.Canvas(frame, width=20, height=20, bg=color).pack(side=tk.LEFT, padx=5)
        tk.Label(frame, text=text).pack(side=tk.LEFT)

    create_legend_item(legend_frame, COLORS["recharge_station"], "Recharge Station")
    create_legend_item(legend_frame, COLORS["bot"], "Survivor Bot")
    create_legend_item(legend_frame, COLORS["spare_part_small"], "Small Part")
    create_legend_item(legend_frame, COLORS["spare_part_medium"], "Medium Part")
    create_legend_item(legend_frame, COLORS["spare_part_large"], "Large Part")
    create_legend_item(legend_frame, COLORS["drone"], "Active Drone")
    create_legend_item(legend_frame, COLORS["drone_hibernating"], "Hibernating Drone")

    # statistics of the number of bots
    stats_frame = tk.LabelFrame(control_panel, text="Statistics", padx=5, pady=5)
    stats_frame.pack(fill="x", pady=10)

    bot_count = tk.StringVar(value="Bots: 0")
    parts_count = tk.StringVar(value="Parts: 0")
    stored_parts = tk.StringVar(value="Stored Parts: 0")
    active_drones = tk.StringVar(value="Active Drones: 0")
    hibernating_drones = tk.StringVar(value="Hibernating Drones: 0")
    swarm_count = tk.StringVar(value="Swarms: 0")

    tk.Label(stats_frame, textvariable=bot_count).pack(anchor="w")
    tk.Label(stats_frame, textvariable=parts_count).pack(anchor="w")
    tk.Label(stats_frame, textvariable=stored_parts).pack(anchor="w")
    tk.Label(stats_frame, textvariable=active_drones).pack(anchor="w")
    tk.Label(stats_frame, textvariable=hibernating_drones).pack(anchor="w")
    tk.Label(stats_frame, textvariable=swarm_count).pack(anchor="w")

    def update_stats():
        total_stored = sum(len(station.stored_parts) for station in grid.stations)
        active_drone_count = sum(1 for drone in grid.drones if not drone.is_hibernating)
        hibernating_drone_count = sum(1 for drone in grid.drones if drone.is_hibernating)
        
        bot_count.set(f"Bots: {len(grid.bots)}")
        parts_count.set(f"Parts: {len(grid.parts)}")
        stored_parts.set(f"Stored Parts: {total_stored}")
        active_drones.set(f"Active Drones: {active_drone_count}")
        hibernating_drones.set(f"Hibernating Drones: {hibernating_drone_count}")
        swarm_count.set(f"Swarms: {len(grid.swarms)}")

        root.after(100, update_stats)

    # start updating stats
    update_stats()

    # initial display
    grid.display_tkinter(canvas)
    
    root.mainloop()

if __name__ == "__main__":
    main()