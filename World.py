#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  1 08:00:26 2022

@author: max
"""

import numpy as np
import Evolution
import matplotlib.pyplot as plt
import os
import auxilliary_functions as aux
import sys
if sys.version_info >= (3,8):
    import pickle
else:
    import pickle5 as pickle

np.random.seed(0)

class Constants:
    def __init__(self):
        self.make_agent_constants()
        self.make_world_constants()
    # end init
    
    def make_agent_constants(self):
        self.agent_constants = {
            'generic': {
                'velocity_limit': 1.0,
                'acceleration_limit': 1.0,
                'perception_radius': 11.0,
                'food_level': 1.0,
                'food_depletion': 0.1,
                'food_radius': 1.0,
                'food_replenishment': 70
            },
            'predator': {
                'velocity_limit': 12.0,
                'acceleration_limit': 1.2,
                'perception_radius': 200.0,
                'food_level': 200.0,
                'food_depletion': 1.0,
                'food_radius': 50.0,
                'food_replenishment': 100
            },
            'prey': {
                'velocity_limit': 10,
                'acceleration_limit': 1.0,
                'perception_radius': 200.0,
                'food_level': 1.0,
                'food_depletion': 1.0,
                'food_radius': 0.0,
                'food_replenishment': 70
            }
        }
    # end make_agent_constants
    
    def make_world_constants(self):
        self.world_width = 1920
        self.world_height = 1440
        self.total_predator_agents = 100
        self.total_prey_agents = 100
    # end make_world_constants
# end Constants

class Environment:
    def __init__(self, constants, session_name='test_session'):
        self.total_iterations = 0
        self.session_name = session_name
        self.constants = constants
        self.predator_agents = []
        self.prey_agents = []
        self.dead_predator_agents = []
        self.dead_prey_agents = []
        self.genetics = Evolution.Genetics()
        self.evoConst = Evolution.Constants()
    # end init
    
    def update(self):
        self.total_iterations += 1
        self.update_agents()
        self.compute_stats()
    # end update
    
    def update_agents(self):
        agents2die = {
            'predator': [],
            'prey': []
        }
        for a in self.prey_agents:
            a.update_friends_and_enemies( friends=self.prey_agents, enemies=self.predator_agents )
            a.move()
        for a in self.predator_agents:
            a.update_friends_and_enemies( friends=self.predator_agents, enemies=self.prey_agents )
            a.move()
            a2d = a.update_food()
            agents2die['predator'].extend( a2d['predator'] )
            agents2die['prey'].extend( a2d['prey'] )
        # kill agents
        for a in agents2die['predator']:
            self.dead_predator_agents.append( a )
            self.predator_agents.remove( a )
        for a in agents2die['prey']:
            self.dead_prey_agents.append( a )
            self.prey_agents.remove( a )
    # end update_agents
    
    def evolve(self):
        # evolve prey
        # set iterations of death to alive agents
        for i in range( len(self.prey_agents) ):
            self.prey_agents[i].death_iteration_number = self.total_iterations
        self.prey_agents = self.genetics.evolve_population(self.prey_agents + self.dead_prey_agents, self.constants.total_prey_agents)
        # randomise position, velocity and acceleration - reset is_alive
        for p in self.prey_agents:
            p.init_random()
        # evolve predators
        # set iterations of death to alive agents
        for i in range( len(self.predator_agents) ):
            self.predator_agents[i].death_iteration_number = self.total_iterations
        self.predator_agents = self.genetics.evolve_population(self.predator_agents + self.dead_predator_agents, self.constants.total_predator_agents)
        # restore food levels and randomise position, velocity and acceleration - reset is_alive
        for p in self.predator_agents:
            p.restore_food_level()
            p.init_random()
        self.dead_predator_agents = []
        self.dead_prey_agents = []
        # reset iterations
        self.total_iterations = 0
    # end evolve
    
    def set_predator_agents(self, agents):
        self.predator_agents = agents
    # end set_predator_agents
    
    def set_prey_agents(self, agents):
        self.prey_agents = agents
    # end set_prey_agents
    
    def compute_stats(self):
        if len( self.predator_agents ) > 0:
            self.predator_food_levels = np.zeros( len( self.predator_agents ) )
            for i, p in enumerate(self.predator_agents):
                self.predator_food_levels[i] = p.food_level
            self.mean_predator_food_level = np.mean( self.predator_food_levels )
            self.median_predator_food_level = np.median( self.predator_food_levels )
            self.std_predator_food_level = np.std( self.predator_food_levels )
            self.max_predator_food_level = np.max( self.predator_food_levels )
            self.min_predator_food_level = np.min( self.predator_food_levels )
        else:
            self.predator_food_levels = np.zeros( 1 )
            self.mean_predator_food_level = np.mean( self.predator_food_levels )
            self.median_predator_food_level = np.median( self.predator_food_levels )
            self.std_predator_food_level = np.std( self.predator_food_levels )
            self.max_predator_food_level = np.max( self.predator_food_levels )
            self.min_predator_food_level = np.min( self.predator_food_levels )
    # end compute_stats

    def save_weights(self, generation=0):
        weights = {
            'predator': [],
            'prey': []
        }
        for p in self.predator_agents:
            weights['predator'].append( p.genome )
        for p in self.prey_agents:
            weights['prey'].append( p.genome )
        with open('weights/' + self.session_name + '/weights_' + "{:05d}".format(generation), 'wb') as handle:
            pickle.dump(weights, handle, protocol=pickle.HIGHEST_PROTOCOL)
    # end save_weights
    
    def plot_iteration(self, generation=0):
        if not os.path.exists('figs/' + self.session_name + '/generation_' + "{:05d}".format(generation)):
            os.makedirs('figs/' + self.session_name + '/generation_' + "{:05d}".format(generation))
        plt.clf()
        for p in self.prey_agents:
            plt.plot(p.x, p.y, 'g.')
        for p in self.predator_agents:
            plt.plot(p.x, p.y, 'r.')
            if p.closest_enemy is not None:
                if aux.dist_2d_arrays([p.x, p.y], [p.closest_enemy.x, p.closest_enemy.y]) <= self.constants.agent_constants['predator']['food_radius']:
                    plt.plot([p.x, p.closest_enemy.x],[p.y, p.closest_enemy.y], '-',c='red', alpha=0.9)
                else:
                    plt.plot([p.x, p.closest_enemy.x],[p.y, p.closest_enemy.y], '-',c='white', alpha=0.2)
            if p.food_level <= self.constants.agent_constants['predator']['food_replenishment']:
                # plt.text(p.x, p.y, "{:.2f}".format(p.food_level), c='red', alpha=0.3)
                plt.text(p.x, p.y, str(int(p.food_level)), c='red', alpha=0.7)
            else:
                # plt.text(p.x, p.y, "{:.2f}".format(p.food_level), c='white', alpha=0.3)
                plt.text(p.x, p.y, str(int(p.food_level)), c='white', alpha=0.3)
        plt.xticks([])
        plt.yticks([])
        plt.xlim([0, self.constants.world_width])
        plt.ylim([0, self.constants.world_height])
        # frame1 = plt.gca()
        # frame1.axes.xaxis.set_ticklabels([])
        # frame1.axes.yaxis.set_ticklabels([])
        ax = plt.gca()
        ax.set_facecolor('black')
        plt.savefig('figs/' + self.session_name + '/generation_' + "{:05d}".format(generation) + '/iteration_' + "{:05d}".format(self.total_iterations) )
    # end plot_iteration
    
    def save_video(self, generation=0):
        if not os.path.exists('figs/' + self.session_name + '/generation_' + "{:05d}".format(generation)):
            print('ERROR: no folder named figs/' + self.session_name + '/generation_' + "{:05d}".format(generation))
        else:
            os.system('ffmpeg -r 24 -f image2 -pattern_type glob -i "' + 'figs/' + self.session_name + '/generation_' + "{:05d}".format(generation) +'/*?png" -vcodec libx264 -crf 20 -pix_fmt yuv420p ' + 'videos/' + self.session_name + '/generation_' + "{:05d}".format(generation) + '.mp4')
        os.system('rm -r figs/' + self.session_name + '/generation_' + "{:05d}".format(generation))
# end Environment
