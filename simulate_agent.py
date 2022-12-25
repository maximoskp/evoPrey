#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  7 09:32:58 2022

@author: max
"""

from optparse import make_option
import tkinter as tk
from tkinter import ttk

import sys
if sys.version_info >= (3,8):
    import pickle
else:
    import pickle5 as pickle
import World
import Agent
import Evolution

# initialize constants and environment
constants = World.Constants()
environment = World.Environment( constants )

evoConst =  Evolution.Constants()

# get a weight
agent_tribe = 'predator'
generation = 1000
wf = 'weights_' + "{:05d}".format(generation)
with open('weights/' + wf, 'rb') as handle:
    w = pickle.load(handle)

weights = w[ agent_tribe ][0]

a = Agent.PredatorAgent( genome=weights, constants=constants, environment=environment )

a.friends_number = 5 # 1
a.friends_proximity = 0.5 # 2
a.closest_friend_proximity = 0.1 # 3
a.friends_velocity_alignment = 0.5 # 4
a.friends_velocity_magnitude = 0.3 # 5
a.closest_friend_velocity_alignment = 0.2 # 6
a.closest_friend_velocity_magnitude = 0.4 # 7
a.enemies_number = 7 # 8
a.enemies_proximity = 0.6 # 9
a.closest_enemy_proximity = 0.1 # 10
a.enemies_velocity_alignment = 0.1 # 11
a.enemies_velocity_magnitude = 0.6 # 12
a.closest_enemy_velocity_alignment = 0.4 # 13
a.closest_enemy_velocity_magnitude = 0.5 # 14
a.friends_loudest_message = 3 #15
a.enemies_loudest_message = 5 #16
# min( self.x , self.constants.world_width - self.x )/self.constants.agent_constants[self.category]['perception_radius'], #17
# min( self.y , self.constants.world_height - self.y )/self.constants.agent_constants[self.category]['perception_radius'], #18
a.x = 500
a.y = 500
a.food_level = 10 # 1
a.vx = 0.5 # 2
a.vy = 0.3 # 3
a.ax = 0.4 # 4
a.ay = 0.6 # 5

motion_output = None
message = None
def run_agent():
    a.run_network()
    global motion_output
    motion_output = a.motion_output
    global message
    message = a.message

def run_and_show():
    run_agent()
    print(' ============================================== ')
    print('accelerate to friends mean: \t', motion_output[0])
    l1.set_text(text = 'accelerate to friends mean: ' + '{: .2f}'.format(motion_output[0]))

    print('accelerate to closest friend: \t', motion_output[1])
    l2.set_text(text = 'accelerate to closest friend: ' + '{: .2f}'.format(motion_output[1]))

    print('align with velocity of friends: \t', motion_output[2])
    l3.set_text(text = 'align with velocity of friends: ' + '{: .2f}'.format(motion_output[2]))
    
    print('accelerate to enemies mean: \t', motion_output[3])
    l4.set_text(text = 'accelerate to enemies mean: ' + '{: .2f}'.format(motion_output[3]))

    print('accelerate to closest enemy: \t', motion_output[4])
    l5.set_text(text = 'accelerate to closest enemy: ' + '{: .2f}'.format(motion_output[4]))

    print('align with velocity of enemies: \t', motion_output[5])
    l6.set_text(text = 'align with velocity of enemies: ' + '{: .2f}'.format(motion_output[5]))

    print('accelerate towards walls: \t', motion_output[6])
    l7.set_text(text = 'accelerate towards walls: ' + '{: .2f}'.format(motion_output[6]))

    print('message: \t', message)
    l8.set_text(text = 'message: ' + str(message))
    print(' ============================================== ')

# ============ class CompountSlider =========================
class CompountSlider:
    def __init__(self, text='CSlider', root=None, range_low=0, range_high=100, value=10, integer=True, row=0):
        # slider current value
        self.value = value
        self.current_value = eval('a.' + self.value)
        # self.range_low = range_low
        # self.range_high = range_high
        self.integer = integer
        self.text = text
        self.row = row
        # label for the slider
        self.slider_label = ttk.Label(
            root,
            text=self.text
        )
        self.slider_label.grid(
            column=0,
            row=self.row,
            sticky='w'
        )
        #  slider
        self.slider = ttk.Scale(
            root,
            from_=range_low,
            to=range_high,
            orient='horizontal',  # vertical
            command=self.slider_changed,
            variable=self.current_value
        )
        self.slider.grid(
            column=1,
            row=self.row,
            sticky='we'
        )
        # value label
        self.value_label = ttk.Label(
            root,
            text=self.get_current_value()
        )
        self.value_label.grid(
            row=self.row,
            column=2,
            # row=2,
            # columnspan=2,
            sticky='n'
        )
    # end init
    def get_current_value(self):
        if self.integer:
            return "{:03d}".format(self.current_value)
        else:
            return '{: .2f}'.format(self.current_value)
    # end get_current_value
    def slider_changed(self, event):
        if self.integer:
            self.current_value = int(float(event))
        else:
            self.current_value = float(event)
        self.value_label.configure(text=self.get_current_value())
        exec('a.' + self.value + ' = self.current_value')
        run_and_show()
    # end slider_changed
# class CompountSlider

# ============ class CompountSlider =========================
class GenerationSlider:
    def __init__(self, text='CSlider', root=None, range_low=0, range_high=100, value=10, integer=True, row=0):
        # slider current value
        self.current_value = value
        # self.range_low = range_low
        # self.range_high = range_high
        self.integer = integer
        self.text = text
        self.row = row
        # label for the slider
        self.slider_label = ttk.Label(
            root,
            text=self.text
        )
        self.slider_label.grid(
            column=0,
            row=self.row,
            sticky='w'
        )
        #  slider
        self.slider = ttk.Scale(
            root,
            from_=range_low,
            to=range_high,
            orient='horizontal',  # vertical
            command=self.slider_changed,
            variable=self.current_value
        )
        self.slider.grid(
            column=1,
            row=self.row,
            sticky='we'
        )
        # value label
        self.value_label = ttk.Label(
            root,
            text=self.get_current_value()
        )
        self.value_label.grid(
            row=self.row,
            column=2,
            # row=2,
            # columnspan=2,
            sticky='n'
        )
    # end init
    def get_current_value(self):
        if self.integer:
            return "{:03d}".format(self.current_value)
        else:
            return '{: .2f}'.format(self.current_value)
    # end get_current_value
    def slider_changed(self, event):
        if self.integer:
            self.current_value = int(float(event))
        else:
            self.current_value = float(event)
        self.value_label.configure(text=self.get_current_value())
        global generation
        generation = self.current_value
        global a
        wf = 'weights_' + "{:05d}".format(generation)
        with open('weights/' + wf, 'rb') as handle:
            w = pickle.load(handle)
        weights = w[ agent_tribe ][0]
        a = Agent.PredatorAgent( genome=weights, constants=constants, environment=environment )
        sliders2agent()
        run_and_show()
    # end slider_changed
# class CompountSlider

# root window
root = tk.Tk()
root.geometry('800x800')
root.resizable(True, True)
root.title('Agent simulation')

root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=3)

variable = tk.StringVar(root)
variable.set('predator') # default value

def change_type(event):
    global agent_tribe
    agent_tribe = event
    global a
    wf = 'weights_' + "{:05d}".format(generation)
    with open('weights/' + wf, 'rb') as handle:
        w = pickle.load(handle)
    weights = w[ agent_tribe ][0]
    a = Agent.PredatorAgent( genome=weights, constants=constants, environment=environment )
    sliders2agent()
    run_and_show()
    print(event)

w = tk.OptionMenu(root, variable, 'predator', 'prey', command=change_type)
w.grid(
    column=0,
    row=0,
    sticky='we'
)

row = 1
s_gen = GenerationSlider(text='Generation number', root=root, range_low=0, range_high=1300, value=generation, integer=True, row=row); row += 1

external_label = ttk.Label(
    root,
    text='------ External intput ------'
)
external_label.grid(
    row=row,
    column=0,
    # row=2,
    # columnspan=2,
    sticky='n'
)
row += 1

s1 = CompountSlider(text='Friends number', root=root, range_low=0, range_high=100, value='friends_number', integer=True, row=row); row += 1
s2 = CompountSlider(text='Friends proximity', root=root, range_low=0, range_high=1, value='friends_proximity', integer=False, row=row); row += 1
s3 = CompountSlider(text='Closest friend proximity', root=root, range_low=0, range_high=1, value='closest_friend_proximity', integer=False, row=row); row += 1
s4 = CompountSlider(text='Friends velocity alignment', root=root, range_low=-1, range_high=1, value='friends_velocity_alignment', integer=False, row=row); row += 1
s5 = CompountSlider(text='Friends velocity magnitude', root=root, range_low=0, range_high=1, value='friends_velocity_magnitude', integer=False, row=row); row += 1
s6 = CompountSlider(text='Closest friend velocity alignment', root=root, range_low=-1, range_high=1, value='closest_friend_velocity_alignment', integer=False, row=row); row += 1
s7 = CompountSlider(text='Closest friend velocity magnitude', root=root, range_low=0, range_high=1, value='closest_friend_velocity_magnitude', integer=False, row=row); row += 1

s8 = CompountSlider(text='Enemies number', root=root, range_low=0, range_high=100, value='enemies_number', integer=True, row=row); row += 1
s9 = CompountSlider(text='Enemies proximity', root=root, range_low=0, range_high=1, value='enemies_proximity', integer=False, row=row); row += 1
s10 = CompountSlider(text='Closest enemy proximity', root=root, range_low=0, range_high=1, value='closest_enemy_proximity', integer=False, row=row); row += 1
s11 = CompountSlider(text='Enemies velocity alignment', root=root, range_low=-1, range_high=1, value='enemies_velocity_alignment', integer=False, row=row); row += 1
s12 = CompountSlider(text='Enemies velocity magnitude', root=root, range_low=0, range_high=1, value='enemies_velocity_magnitude', integer=False, row=row); row += 1
s13 = CompountSlider(text='Closest enemy velocity alignment', root=root, range_low=-1, range_high=1, value='closest_enemy_velocity_alignment', integer=False, row=row); row += 1
s14 = CompountSlider(text='Closest enemy velocity magnitude', root=root, range_low=0, range_high=1, value='closest_enemy_velocity_magnitude', integer=False, row=row); row += 1

s15 = CompountSlider(text='Friends loudest message', root=root, range_low=0, range_high=15, value='friends_loudest_message', integer=True, row=row); row += 1
s16 = CompountSlider(text='Enemies loudest message', root=root, range_low=0, range_high=15, value='enemies_loudest_message', integer=True, row=row); row += 1

internal_label = ttk.Label(
    root,
    text='------ Internal intput ------'
)
internal_label.grid(
    row=row,
    column=0,
    # row=2,
    # columnspan=2,
    sticky='n'
)
row += 1

# a.x = 500
s17 = CompountSlider(text='x coordinate', root=root, range_low=0, range_high=constants.world_width, value='x', integer=False, row=row); row += 1
# a.y = 500
s18 = CompountSlider(text='y coordinate', root=root, range_low=0, range_high=constants.world_height, value='y', integer=False, row=row); row += 1
# a.food_level = 10 # 1
s19 = CompountSlider(text='Food level', root=root, range_low=0, range_high=200, value='food_level', integer=False, row=row); row += 1
# a.vx = 0.5 # 2
s20 = CompountSlider(text='x velocity', root=root, range_low=0, range_high=10, value='vx', integer=False, row=row); row += 1
# a.vy = 0.3 # 3
s21 = CompountSlider(text='y velocity', root=root, range_low=0, range_high=10, value='vy', integer=False, row=row); row += 1
# a.ax = 0.4 # 4
s22 = CompountSlider(text='x acceleration', root=root, range_low=0, range_high=1, value='ax', integer=False, row=row); row += 1
# a.ay = 0.6 # 5
s23 = CompountSlider(text='y acceleration', root=root, range_low=0, range_high=1, value='ay', integer=False, row=row); row += 1

ttk.Separator(root, orient=tk.VERTICAL).grid(column=3, row=0, rowspan=row, sticky='ns')

row = 0
output_label = ttk.Label(
    root,
    text='---------- Output ----------'
)
output_label.grid(
    row=row,
    column=4,
    # row=2,
    # columnspan=2,
    sticky='n'
)
class CustomLabel:
    def __init__(self, text='xxx', row=0):
        self.label = ttk.Label(
            root,
            text=text
        )
        self.label.grid(
            row=row,
            column=4,
            # row=2,
            # columnspan=2,
            sticky='n'
        )
    # end init
    def set_text(self, text):
        self.label.config(text = text)
    # end set_text
# end CustomLabel

row += 1
l1 = CustomLabel(text='accelerate to friends mean: 000', row=row); row+=1
l2 = CustomLabel(text='accelerate to closest friend: 000', row=row); row+=1
l3 = CustomLabel(text='align with velocity of friends: 000', row=row); row+=1
l4 = CustomLabel(text='accelerate to enemies mean: 000', row=row); row+=1
l5 = CustomLabel(text='accelerate to closest enemy', row=row); row+=1
l6 = CustomLabel(text='align with velocity of enemies: 000', row=row); row+=1
l7 = CustomLabel(text='accelerate towards walls: 000', row=row); row+=1
l8 = CustomLabel(text='message: 000', row=row); row+=1

def sliders2agent():
    global a
    a.friends_number = s1.current_value
    a.friends_proximity = s2.current_value
    a.closest_friend_proximity = s3.current_value
    a.friends_velocity_alignment = s4.current_value
    a.friends_velocity_magnitude = s5.current_value
    a.closest_friend_velocity_alignment = s6.current_value
    a.closest_friend_velocity_magnitude = s7.current_value
    a.enemies_number = s8.current_value
    a.enemies_proximity = s9.current_value
    a.closest_enemy_proximity = s10.current_value
    a.enemies_velocity_alignment = s11.current_value
    a.enemies_velocity_magnitude = s12.current_value
    a.closest_enemy_velocity_alignment = s13.current_value
    a.closest_enemy_velocity_magnitude = s14.current_value
    a.friends_loudest_message = s15.current_value
    a.enemies_loudest_message = s16.current_value
    # min( self.x , self.constants.world_width - self.x )/self.constants.agent_constants[self.category]['perception_radius'], #17
    # min( self.y , self.constants.world_height - self.y )/self.constants.agent_constants[self.category]['perception_radius'], #18
    a.x = s17.current_value
    a.y = s18.current_value
    a.food_level = s19.current_value
    a.vx = s20.current_value
    a.vy = s21.current_value
    a.ax = s22.current_value
    a.ay = s23.current_value



root.mainloop()