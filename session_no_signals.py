#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  1 09:20:09 2022

@author: max
"""

import World
import Agent
import Evolution
import csv
import os

session_name = 'door1_no_signals'

# initialize constants and environment
constants = World.Constants()
environment = World.Environment( constants, session_name=session_name )

evoConst =  Evolution.Constants()

# initialize some predators and prey
a = []
b = []
for i in range(constants.total_predator_agents):
    a.append( Agent.SinglePredator( constants=constants, environment=environment, use_messages=False ) )
for i in range(constants.total_prey_agents):
    b.append( Agent.PreyAgent( constants=constants, environment=environment, use_messages=False ) )

# append agents in environment
environment.set_predator_agents(a)
environment.set_prey_agents(b)

current_generation = 0

if not os.path.exists('figs'):
    os.makedirs('figs')
if not os.path.exists('videos'):
    os.makedirs('videos')
if not os.path.exists('data'):
    os.makedirs('data')
if not os.path.exists('weights'):
    os.makedirs('weights')

if not os.path.exists('figs/' + session_name):
    os.makedirs('figs/' + session_name)
if not os.path.exists('videos/' + session_name):
    os.makedirs('videos/' + session_name)
if not os.path.exists('data/' + session_name):
    os.makedirs('data/' + session_name)
if not os.path.exists('weights/' + session_name):
    os.makedirs('weights/' + session_name)

fields=['generation', 'iteration', 'predator_food', 'prey_alive', 'prey_dead', 'prey_escaped']
with open('data/' + session_name + '/_summary.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(fields)

while current_generation < evoConst.total_generations_number:
    print('generation: ' + str(current_generation) + '-----------------')
    with open('data/' + session_name + '/details_generation_' + "{:05d}".format(current_generation) + '.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(fields)
    environment.save_weights( generation=current_generation )
    while len(environment.predator_agents) > evoConst.minPopulationSize and len(environment.prey_agents) > evoConst.minPopulationSize:
        environment.update()
        environment.plot_iteration(generation=current_generation)
        print( str(current_generation) + '-' + str(environment.total_iterations) +'| predator_food: ' + "{:.2f}".format(environment.min_predator_food_level) + '\t - prey alive|dead|escaped: ' + str(len(environment.prey_agents)) + '|' + str(len(environment.dead_prey_agents)) + '|' + str(len(environment.escaped_prey_agents)) )
        # print( str(environment.total_iterations) + '|' + str(len(environment.predator_agents)) + '|' + str(len(environment.prey_agents)), end='---' )
        with open('data/' + session_name + '/details_generation_' + "{:05d}".format(current_generation) + '.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow([ current_generation, environment.total_iterations, environment.min_predator_food_level, environment.mean_predator_food_level, environment.median_predator_food_level, environment.max_predator_food_level ])
    environment.save_video( generation=current_generation )
    with open('data/' + session_name + '/_summary.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow([ current_generation, environment.total_iterations, environment.min_predator_food_level, len(environment.prey_agents), len(environment.dead_prey_agents), len(environment.escaped_prey_agents) ])
    environment.evolve()
    current_generation += 1
