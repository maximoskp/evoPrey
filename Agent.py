import numpy as np
import auxilliary_functions as aux

np.random.seed(0)

class GenericAgent:
    category = 'generic'
    def __init__(self, genome=None, constants=None, environment=None, use_messages=True):
        self.use_messages = use_messages
        # External input:
        # 1. Number of friends.
        # 2. Friends average proximity (in [0,1], normalized on perception radius).
        # 3. Closest friend proximity (in [0,1], normalized on perception radius).
        # 4. Friends velocity alignement.
        # 5. Friends velocity magnitude.
        # 6. Closest friend velocity alignment.
        # 7. Closest friend velocity magnitude.
        # 8. Number of enemies.
        # 9. Enemies average proximity (in [0,1], normalized on perception radius).
        # 10. Closest enemy proximity (in [0,1], normalized on perception radius).
        # 11. Enemies velocity alignement.
        # 12. Enemies velocity magnitude.
        # 13. Closest enemy velocity alignment.
        # 14. Closest enemy velocity magnitude.
        # 15. Friend loudest messages (int from bits).
        # 16. Enemy loudest messages (int from bits).
        # 17. Distance from wall x. (in [0,1], normalized on perception radius).
        # 18. Distance from wall y. (in [0,1], normalized on perception radius).
        self.external_input_size = 18
        if not self.use_messages:
            self.external_input_size = 16
        # Internal input:
        # 1. Life level.
        # 2. Self velocity x.
        # 3. Self velocity y.
        # 4. Self acceleration x.
        # 5. Self acceleration y.
        self.internal_input_size = 5
        # Motion output:
        # 1. Accelerate to average friends location (percentage of max, in [-1,1])
        # 2. Accelerate to closest friend location (percentage of max, in [-1,1])
        # 3. Accelerate to align velocity with friends (what does negative mean?).
        # 4. Accelerate to average enemy location (percentage of max, in [-1,1]).
        # 5. Accelerate to closest enemy location (percentage of max, in [-1,1]).
        # 6. Accelerate to align velocity with enemies (what does negative mean?).
        # 7. Accelerate away from wall (percentage of max, in [-1,1]).
        # 8. Accelerate / deccelerate in current direction (percentage of current velocity, in [-1,1]).
        self.motion_output_size = 8
        # message information
        self.message_bits = 2
        if not self.use_messages:
            self.message_bits = 0
        # WEIGHTS
        self.latent_1_size = 20
        self.latent_2_size = 10
        self.init_weights_zero()
        # genome
        if genome is None:
            self.random_genome()
        else:
            self.genome = genome
            self.genome_size = self.genome.size
        self.genome2weights()
        # all constants
        self.get_constants(constants)
        self.environment = environment
        # position, velocity and acceleration
        self.init_random()
        self.is_alive = True
        self.death_iteration_number = 0
        self.food_level = self.constants.agent_constants[self.category]['food_level']
        self.message = 0
    # end __init__

    def init_weights_zero(self):
        self.weights = {
            # input to latent 1
            'w_in': np.zeros( (self.internal_input_size + self.external_input_size , self.latent_1_size) ),
            'bias_in': np.zeros( self.latent_1_size ).reshape( (1, self.latent_1_size) ),
            # latent 1 to latent 2
            'w_latent': np.zeros( (self.latent_1_size, self.latent_2_size) ),
            'bias_latent': np.zeros( self.latent_2_size ).reshape( (1, self.latent_2_size) ),
            # latent to:
            # spoken message
            'w_message': np.zeros( (self.latent_2_size , self.message_bits) ),
            'bias_message': np.zeros( self.message_bits ).reshape( (1,self.message_bits) ),
            # motion weights
            'w_motion': np.zeros( (self.latent_2_size , self.motion_output_size) ),
            'bias_motion': np.zeros( self.motion_output_size ).reshape( (1,self.motion_output_size) )
        }
        if not self.use_messages:
            self.weights = {
                # input to latent 1
                'w_in': np.zeros( (self.internal_input_size + self.external_input_size , self.latent_1_size) ),
                'bias_in': np.zeros( self.latent_1_size ).reshape( (1, self.latent_1_size) ),
                # latent 1 to latent 2
                'w_latent': np.zeros( (self.latent_1_size, self.latent_2_size) ),
                'bias_latent': np.zeros( self.latent_2_size ).reshape( (1, self.latent_2_size) ),
                # latent to:
                # motion weights
                'w_motion': np.zeros( (self.latent_2_size , self.motion_output_size) ),
                'bias_motion': np.zeros( self.motion_output_size ).reshape( (1,self.motion_output_size) )
            }
        self.weight_keys = self.weights.keys()
    # def end init_weights_zero

    def random_genome(self):
        self.genome_size = 0
        for k in self.weight_keys:
            self.genome_size += self.weights[k].size
        self.genome = 2*np.random.random( self.genome_size ) - 1
    # end random_genome

    def genome2weights(self):
        cutoff = 0
        for k in self.weight_keys:
            self.weights[k] = np.reshape( self.genome[cutoff:cutoff+self.weights[k].size] , self.weights[k].shape )
    # end genome2weights

    def get_constants(self, constants):
        self.constants = constants
    # end get_category_constants

    def init_random(self):
        # position
        self.x = np.random.rand()*self.constants.world_width
        self.y = np.random.rand()*self.constants.world_height
        # velocity
        vx = 2*np.random.rand() - 1
        vy = 2*np.random.rand() - 1
        self.vx , self.vy = aux.limit_xy( vx, vy, self.constants.agent_constants[self.category]['velocity_limit'] )
        # acceleration
        ax = 2*np.random.rand() - 1
        ay = 2*np.random.rand() - 1
        self.ax , self.ay = aux.limit_xy( ax, ay, self.constants.agent_constants[self.category]['acceleration_limit'] )
    # end init_random_position_velocity

    def update_friends_and_enemies( self, friends=None, enemies=None ):
        # friends
        perceived_friends = []
        friends_velocities = []
        self.friends_mean_location = []
        self.friends_mean_velocity = []
        self.friends_number = 0
        closest_friend_distance = np.inf
        self.closest_friend_location = []
        self.closest_friend_velocity = []
        if self.use_messages:
            friend_messages = []
        for f in friends:
            if aux.dist_2d_arrays( [self.x, self.y], [f.x, f.y] ) < self.constants.agent_constants[self.category]['perception_radius'] :
                perceived_friends.append( [f.x, f.y] )
                friends_velocities.append( [f.vx, f.vy] )
                if self.use_messages:
                    friend_messages.append( f.message )
                self.friends_number += 1
                if aux.dist_2d_arrays( [self.x, self.y], [f.x, f.y] ) < closest_friend_distance:
                    self.closest_friend_location = [f.x, f.y]
                    self.closest_friend_velocity = [f.vx, f.vy]
                closest_friend_distance = aux.dist_2d_arrays( [self.x, self.y], [f.x, f.y] )
        if len( perceived_friends ) > 0:
            self.friends_mean_location = np.mean( np.array( perceived_friends ).reshape((len(perceived_friends),2)), axis=0 )
            self.friends_mean_velocity = np.mean( np.array( friends_velocities ).reshape((len(friends_velocities),2)), axis=0 )
            self.friends_proximity = aux.dist_2d_arrays([self.x, self.y], self.friends_mean_location)/self.constants.agent_constants[self.category]['perception_radius']
            self.closest_friend_proximity = aux.dist_2d_arrays([self.x, self.y], self.closest_friend_location)/self.constants.agent_constants[self.category]['perception_radius']
            if self.use_messages:
                self.friends_loudest_message = np.bincount( friend_messages ).argmax()
        else:
            self.friends_mean_location = np.array( [self.x, self.y] )
            self.friends_mean_velocity = np.array( [self.vx, self.vy] )
            self.closest_friend_location = np.array( [self.x, self.y] )
            self.closest_friend_velocity = np.array( [self.vx, self.vy] )
            self.friends_proximity = 1.1
            self.closest_friend_proximity = 1.1
            if self.use_messages:
                self.friends_loudest_message = 0
        self.friends_velocity_alignment = aux.cos_dist([self.vx, self.vy], self.friends_mean_velocity)
        self.friends_velocity_magnitude = np.linalg.norm(self.friends_mean_velocity)
        self.closest_friend_velocity_alignment = aux.cos_dist([self.vx, self.vy], self.closest_friend_velocity)
        self.closest_friend_velocity_magnitude = np.linalg.norm(self.closest_friend_velocity)
        # enemies ---------------------------------------------------------------------------------------------
        perceived_enemies = []
        enemies_velocities = []
        self.enemies_mean_location = []
        self.enemies_mean_velocity = []
        self.enemies_number = 0
        closest_enemy_distance = np.inf
        self.closest_enemy = None
        self.closest_enemy_location = []
        self.closest_enemy_velocity = []
        if self.use_messages:
            enemy_messages = []
        for f in enemies:
            if aux.dist_2d_arrays( [self.x, self.y], [f.x, f.y] ) < self.constants.agent_constants[self.category]['perception_radius'] :
                perceived_enemies.append( [f.x, f.y] )
                enemies_velocities.append( [f.vx, f.vy] )
                if self.use_messages:
                    enemy_messages.append( f.message )
                self.enemies_number += 1
                if aux.dist_2d_arrays( [self.x, self.y], [f.x, f.y] ) < closest_enemy_distance:
                    self.closest_enemy = f
                    self.closest_enemy_location = [f.x, f.y]
                    self.closest_enemy_velocity = [f.vx, f.vy]
                    self.closest_enemy_distance = aux.dist_2d_arrays( [self.x, self.y], [f.x, f.y] )
                    closest_enemy_distance = self.closest_enemy_distance
        if len( perceived_enemies ) > 0:
            self.enemies_mean_location = np.mean( np.array( perceived_enemies ).reshape((len(perceived_enemies),2)), axis=0 )
            self.enemies_mean_velocity = np.mean( np.array( enemies_velocities ).reshape((len(enemies_velocities),2)), axis=0 )
            self.enemies_proximity = aux.dist_2d_arrays([self.x, self.y], self.enemies_mean_location)/self.constants.agent_constants[self.category]['perception_radius']
            self.closest_enemy_proximity = aux.dist_2d_arrays([self.x, self.y], self.closest_enemy_location)/self.constants.agent_constants[self.category]['perception_radius']
            if self.use_messages:
                self.enemies_loudest_message = np.bincount( enemy_messages ).argmax()
        else:
            self.enemies_mean_location = np.array( [self.x, self.y] )
            self.enemies_mean_velocity = np.array( [0, 0] )
            self.closest_enemy_location = np.array( [self.x, self.y] )
            self.closest_enemy_velocity = np.array( [0, 0] )
            if self.use_messages:
                self.enemies_loudest_message = 0
            self.enemies_proximity = 1.1
            self.closest_enemy_proximity = 1.1
        self.enemies_velocity_alignment = aux.cos_dist([self.vx, self.vy], self.enemies_mean_velocity)
        self.enemies_velocity_magnitude = np.linalg.norm(self.enemies_mean_velocity)
        self.closest_enemy_velocity_alignment = aux.cos_dist([self.vx, self.vy], self.closest_enemy_velocity)
        self.closest_enemy_velocity_magnitude = np.linalg.norm(self.closest_enemy_velocity)
    # end update_friends_and_enemies
    
    def run_network(self):
        if self.use_messages:
            network_input = np.array([
                self.friends_number, # 1
                self.friends_proximity, # 2
                self.closest_friend_proximity, # 3
                self.friends_velocity_alignment, # 4
                self.friends_velocity_magnitude, # 5
                self.closest_friend_velocity_alignment, # 6
                self.closest_friend_velocity_magnitude, # 7
                self.enemies_number, # 8
                self.enemies_proximity, # 9
                self.closest_enemy_proximity, # 10
                self.enemies_velocity_alignment, # 11
                self.enemies_velocity_magnitude, # 12
                self.closest_enemy_velocity_alignment, # 13
                self.closest_enemy_velocity_magnitude, # 14
                self.friends_loudest_message, #15
                self.enemies_loudest_message, #16
                min( min( self.x , self.constants.world_width - self.x )/self.constants.agent_constants[self.category]['perception_radius'], 1.1 ), #17
                min( min( self.y , self.constants.world_height - self.y )/self.constants.agent_constants[self.category]['perception_radius'], 1.1 ), #18
                self.food_level, # 1
                self.vx, # 2
                self.vy, # 3
                self.ax, # 4
                self.ay # 5
            ]).reshape( (1, self.external_input_size+self.internal_input_size) )
        else:
            network_input = np.array([
                self.friends_number, # 1
                self.friends_proximity, # 2
                self.closest_friend_proximity, # 3
                self.friends_velocity_alignment, # 4
                self.friends_velocity_magnitude, # 5
                self.closest_friend_velocity_alignment, # 6
                self.closest_friend_velocity_magnitude, # 7
                self.enemies_number, # 8
                self.enemies_proximity, # 9
                self.closest_enemy_proximity, # 10
                self.enemies_velocity_alignment, # 11
                self.enemies_velocity_magnitude, # 12
                self.closest_enemy_velocity_alignment, # 13
                self.closest_enemy_velocity_magnitude, # 14
                min( min( self.x , self.constants.world_width - self.x )/self.constants.agent_constants[self.category]['perception_radius'], 1.1 ), #15
                min( min( self.y , self.constants.world_height - self.y )/self.constants.agent_constants[self.category]['perception_radius'], 1.1 ), #16
                self.food_level, # 1
                self.vx, # 2
                self.vy, # 3
                self.ax, # 4
                self.ay # 5
            ]).reshape( (1, self.external_input_size+self.internal_input_size) )
        latent_1 = np.tanh( np.matmul( network_input , self.weights['w_in'] ) + self.weights['bias_in'] )
        latent_2 = np.tanh( np.matmul( latent_1 , self.weights['w_latent'] ) + self.weights['bias_latent'] )
        self.motion_output = np.tanh( np.matmul( latent_2 , self.weights['w_motion'] ) + self.weights['bias_motion'] )[0]
        if self.use_messages:
            self.message_output = np.tanh( np.matmul( latent_2 , self.weights['w_message'] ) + self.weights['bias_message'] )[0]
            binary_message = (self.message_output >= 0.0).astype(int)
            self.message = binary_message.dot( 1 << np.arange(binary_message.size)[::-1] )
    # end run_network
    
    def move(self):
        self.run_network()
        self.ax = 0
        self.ay = 0
        self.acceleration_array = np.zeros(2)
        self.location = np.array( [ self.x , self.y ] )
        # average friends acceleration
        if self.friends_number > 0:
            self.accelerate_to_location_with_multiplier( self.friends_mean_location , self.motion_output[0] )
        # closest friend acceleration
        if len(self.closest_friend_location) > 0:
            self.accelerate_to_location_with_multiplier( self.closest_friend_location, self.motion_output[1] )
        # average friends velocity acceleration
        if self.friends_number > 0:
            self.accelerate_to_align_with_multiplier( self.friends_mean_velocity, self.motion_output[2] )
        # average enemies acceleration
        if self.enemies_number > 0:
            self.accelerate_to_location_with_multiplier( self.enemies_mean_location , self.motion_output[3] )
        # closest enemy acceleration
        if self.closest_enemy is not None:
            self.accelerate_to_location_with_multiplier( self.closest_enemy_location, self.motion_output[4] )
        # average enemies velocity acceleration
        if self.enemies_number > 0:
            self.accelerate_to_align_with_multiplier( self.enemies_mean_velocity, self.motion_output[5] )
        # wall acceleration
        tmp_x = self.constants.world_width * int(self.x > self.constants.world_width - self.x)
        tmp_y = self.constants.world_height * int(self.y > self.constants.world_height - self.y)
        walls = np.array( [ self.x, self.y ] )
        hitting_wall = False
        if np.abs( tmp_x - self.x ) < self.constants.agent_constants[self.category]['perception_radius']:
            walls[0] = tmp_x
            hitting_wall = True
        if np.abs( tmp_y - self.y ) < self.constants.agent_constants[self.category]['perception_radius']:
            walls[1] = tmp_y
            hitting_wall = True
        if hitting_wall:
            self.accelerate_to_location_with_multiplier( walls, self.motion_output[6] )
        # accelerate / deccelerate to current direction
        # if not moving, start moving to random direction
        if np.abs( self.vx ) < 0.5 and np.abs( self.vy ) < 0.5:
            tmp_x = 2*np.random.rand() - 1
            tmp_y = 2*np.random.rand() - 1
        else:
            tmp_x = self.vx
            tmp_y = self.vy
        self.accelerate_to_align_with_multiplier( [tmp_x, tmp_y], self.motion_output[7] )
        self.ax , self.ay = aux.limit_xy( self.acceleration_array[0], self.acceleration_array[1], self.constants.agent_constants[self.category]['acceleration_limit'] )
        self.vx , self.vy = aux.limit_xy( self.vx + self.ax, self.vy + self.ay, self.constants.agent_constants[self.category]['velocity_limit'] )
        self.x += self.vx
        self.y += self.vy
        if self.x < 0:
            self.x = -self.x
            self.vx = -self.vx
        if self.x > self.constants.world_width:
            self.x = 2*self.constants.world_width - self.x
            self.vx = -self.vx
        if self.y < 0:
            self.y = -self.y
            self.vy = -self.vy
        if self.y > self.constants.world_height:
            self.y = 2*self.constants.world_height - self.y
            self.vy = -self.vy
    # end move
    
    def accelerate_to_location_with_multiplier( self, p, m ):
        tmp_acceleration = ( self.location - p )
        ax , ay = aux.limit_xy( tmp_acceleration[0], tmp_acceleration[1], self.constants.agent_constants[self.category]['acceleration_limit'] )
        self.acceleration_array += m*np.array([ ax, ay ])
    # end accelerate_to_location_with_multiplier
    
    def accelerate_to_align_with_multiplier( self, p, m ):
        tmp_acceleration = p
        ax , ay = aux.limit_xy( tmp_acceleration[0], tmp_acceleration[1], self.constants.agent_constants[self.category]['acceleration_limit'] )
        self.acceleration_array += m*np.array([ ax, ay ])
    # end accelerate_to_location_with_multiplier
    
    def restore_food_level(self):
        self.food_level = self.constants.agent_constants[self.category]['food_level']
    # end restore_food_level
    
    def update_food( self ):
        print('to be overriden')
    # end update_food
# end GenericAgent

class PredatorAgent(GenericAgent):
    category = 'predator'
    def __init__(self, genome=None, constants=None, environment=None, use_messages=True):
        super().__init__(genome, constants, environment=environment, use_messages=use_messages)
    # end init
    
    def update_food( self ):
        self.food_level -= 0.5*self.constants.agent_constants[self.category]['food_depletion']*np.linalg.norm( [self.vx, self.vy] )/self.constants.agent_constants[self.category]['velocity_limit'] + 0.5*self.constants.agent_constants[self.category]['food_depletion']
        agents2die = {
            'predator': [],
            'prey': []
        }
        if self.food_level < 0:
            self.is_alive = False
            agents2die['predator'].append(self)
        if self.closest_enemy is not None:
            if self.is_alive and self.closest_enemy.is_alive and aux.dist_2d_arrays( [self.x, self.y], self.closest_enemy_location ) < self.constants.agent_constants[self.category]['food_radius'] and self.food_level < self.constants.agent_constants[self.category]['food_replenishment'] :
                self.food_level = self.constants.agent_constants[self.category]['food_level']
                self.closest_enemy.is_alive = False
                agents2die['prey'].append(self.closest_enemy)
        return agents2die
    # end update_food

    def init_random(self):
        self.is_alive = True
        self.death_iteration_number = 0
        # position
        self.x = 0.5*np.random.rand()*self.constants.world_width
        self.y = np.random.rand()*self.constants.world_height
        # velocity
        vx = 2*np.random.rand() - 1
        vy = 2*np.random.rand() - 1
        self.vx , self.vy = aux.limit_xy( vx, vy, self.constants.agent_constants[self.category]['velocity_limit'] )
        # acceleration
        ax = 2*np.random.rand() - 1
        ay = 2*np.random.rand() - 1
        self.ax , self.ay = aux.limit_xy( ax, ay, self.constants.agent_constants[self.category]['acceleration_limit'] )
    # end init_random_position_velocity
# end PredatorAgent

class PreyAgent(GenericAgent):
    category = 'prey'
    def __init__(self, genome=None, constants=None, environment=None, use_messages=True):
        super().__init__(genome, constants, environment=environment, use_messages=use_messages)
    # end init
    def init_random(self):
        self.is_alive = True
        self.death_iteration_number = 0
        # position
        self.x = (0.5 + 0.5*np.random.rand())*self.constants.world_width
        self.y = np.random.rand()*self.constants.world_height
        # velocity
        vx = 2*np.random.rand() - 1
        vy = 2*np.random.rand() - 1
        self.vx , self.vy = aux.limit_xy( vx, vy, self.constants.agent_constants[self.category]['velocity_limit'] )
        # acceleration
        ax = 2*np.random.rand() - 1
        ay = 2*np.random.rand() - 1
        self.ax , self.ay = aux.limit_xy( ax, ay, self.constants.agent_constants[self.category]['acceleration_limit'] )
    # end init_random_position_velocity
# end PreyAgent
