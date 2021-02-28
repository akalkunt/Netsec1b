import config
import gym
import random,math

Gb_TO_Mb = 1024

class Attack_Env(gym.Env):
    metadata = {'render.modes': [
        'human']}  #### Define possible types for render function (can be commented out if no render function)
    def __init__(self,observation_list,action_list):
        self.observation_list = observation_list
        self.attack_action_list = action_list

        ################### Properties of RL Algorithms ###########
        self.observation_space = gym.spaces.Discrete(len(self.observation_list))
        self.action_space = gym.spaces.Discrete(len(self.attack_action_list))

        ################ Properties of the environment #############
        self.init_attack_traffic_rate = {}
        self.current_attack_traffic_rate = {}
        self.init_defense_allowed_traffic_rate = {}
        self.current_defense_allowed_traffic_rate = {}
        self.risk_score_sorted = None
        self.TEST_RUNNING = False
        self.current_change = -1

        self.current_utilization = random.uniform(config.BACKGROUND_TRAFFIC_MIN,config.BACKGROUND_TRAFFIC_MAX) * config.LINK_BANDWIDTH * Gb_TO_Mb ######
        self.background_traffic = self.current_utilization/(config.LINK_BANDWIDTH * Gb_TO_Mb)
        self.previous_utilization = None
        self.attack_traffic_induced = None
        self.current_observation = None
        self.time_sequence = 1
        self.defend_risk_score_list = []
        self.file_index = 0

        ############ Initalize the Gym Environment ###########
        self.initial_defense_generation()
        self.initial_attack_generation()


    def reset(self):
        ''' This is the mandatory function for a GYM environment that initiates the environment '''
        print("########## Reset the Environment ##########")
        self.time_sequence = 1
        if self.TEST_RUNNING:
            print("########## Test Environment ##########")
        self.init_env() # --> Initialize the environment

        self.current_observation = self.get_observation()

        return self.current_observation ###### intial observation for your training at this environment


    def step(self,action):
        ''' This is another mandatory the function that executes the action on the environment and return the impact of the action'''
        #### TODO: DEFINE STEP FUNCTION ####
        '''
            You have to do the following steps in this function - 
            1. Pick the action from the action space (attack_action_list) and call attack_impact()
               with the current attack traffic rate
            2. Get the current observation by calling get_observation() 
            3. Calculate the reward using reward_calculation()
            4. Check if the attacker goal has been achieved and set done accordingly
               If done is True, write the attack snapshot on the output file 
               (config.ATTACK_SNAPSHOT_FILE_NAME) using config.write_configuration_files() 
               and call initial_defense_generation() to reset the defense files.
            5. Increment time step by 1
            6. Return in order - observation, reward, done, info (We will keep info empty)
        '''
        
        #Pick action from action space
        # TODO here
        self.attack_action_list[action].attack_impact(self.current_attack_traffic_rate)
#        action.attack_impact(self.current_attack_traffic_rate)
        # Update current observation from the action taken 
        self.current_observation = None
        self.current_observation = get_observation(self)
        # Calculate the reward
        reward = 0
        reward = reward_calculation()
        config.DETAILS_LOG_POINTER.write("Reward Achieved %s\n"%(reward))

        # Check if goal has been reached and set done flag
        done = False
        print("Current observation :",self.current_observation)
        if config.observation_list[self.current_observation] >=1.0 and config.observation_list[self.current_observation] <=1.3:
            done = True
            config.write_configuration_files(util = self.current_utilization, benign_traffic = self.background_traffic, file_name=config.ATTACK_SNAPSHOT_FILE_NAME)
            initial_defense_generation()
        # Keep info empty (Nothing to do here)
        info = {}

        # Increment time step by 1
        # TODO here
        self.time_sequence = self.time_sequence + 1
        return self.current_observation,reward,done,info ##### observation, reward, done, info


    def reward_calcualtion(self):
        #### TODO: DEFINE HOW YOU WANT TO REWARD YOUR AGENT ####
        reward = 0
        '''
            Hint: You want to give your agent positive reward for increasing the link utilization, and give
                  negative reward (penalize) for exceeding the maximum link utilization or if bot traffic is
                  dropped. You may characterize your reward on the basis of the increase in link utilization 
                  (current - previous util). You can also give more reward when the desired goal is achieved.
                  Please refer to the assignment handout for more details.

            Feel free to use incentive/penalty values defined in config.py to calculate your reward. You may
            also experiment with different values for incentive/penalty based on your understanding.
        '''
        # 4 conditions to check.
        if self.current_utilization >= 1.0 and self.current_utilization <=1.3:
            #highest positive reward
            reward = config.INCENTIVE_INCREASED_LINK_UTILIZATION
        if self.current_utilization <1.0:
            if self.current_utilization < self.previous_utilization:
                #Traffic dropped. So penalize.
                reward = config.PENALTY_LESS_PREV
            if self.current_utilization > self.previous_utilization:
                #Going in the right direction. SO reward.
                reward = config.INCENTIVE_WITHIN_GOAL
        if self.current_utilization > 1.3:
            reward = config.PENALTY_OVER_UTILIZATION
            #Penalty because over utilization. 
        return reward


    def init_env(self):
        ''' Inialize the environment. This is called when you want to reset the environment '''
        self.time_sequence = 1 # Setting initial time to 1, this is incremented at every step
        config.DETAILS_LOG_POINTER.write("Initialize the environment\n")
        
        # Clearing all data structures 
        # current_attack_traffic_rate structure - {group: {protocol: {destination: {traffic rate}}}}
        # current_defense_allowed_traffic_rate structure - {group: {protocol: {destination: {traffic rate}}}}
        self.current_attack_traffic_rate.clear()
        self.current_defense_allowed_traffic_rate.clear()

        # Setting the current defense and attack rate traffic to the initial values as per defense policy and
        # initial attack rate respectively

        ########## Reset to the initalize settings #########
        for i in range(config.NUMBER_GROUP):
            self.current_defense_allowed_traffic_rate[i] = {}
            self.current_attack_traffic_rate[i] = {}
            for j in range(config.NUMBER_PROTOCOL):
                self.current_defense_allowed_traffic_rate[i][j] = {}
                self.current_attack_traffic_rate[i][j] = {}
                for k in range(config.NUMBER_DEST_INDEX):
                    self.current_defense_allowed_traffic_rate[i][j][k] = self.init_defense_allowed_traffic_rate[i][j][k]
                    self.current_attack_traffic_rate[i][j][k] = self.init_attack_traffic_rate[i][j][k]


    def get_observation(self):
        ''' This function is called at every time-sequence to define how the environment changes due to the attack and defense actions'''
        ######### Save the previous utilization value ############
        self.previous_utilization = self.current_utilization

        ############# Initialize the current utilization with background traffic that fluctuates within 40-60% of the link bandwidth #########
        self.current_utilization = random.uniform(config.BACKGROUND_TRAFFIC_MIN,config.BACKGROUND_TRAFFIC_MAX) * config.LINK_BANDWIDTH * Gb_TO_Mb ### Taking consideration of background traffic
        self.background_traffic = self.current_utilization/(config.LINK_BANDWIDTH * Gb_TO_Mb)

        self.attack_traffic_induced = 0 # to compute the total attack traffic induced in a step

        #### TODO: DEFINE THE ENVIRONMENT BEHAVIOUR BASED ON ACTION ####
        '''
            Iterate through self.current_traffic_rate (group, protocol, destination, traffic rate combination)
            For each attack traffic rate - 
                If attack traffic rate is less than or equal to what is allowed by the defense policy 
                (current_defense_allowed_traffic_rate) - 
                    Update the current utilization accordingly and add traffic rate to attack_traffic_induced
                Else 
                    Drop the attack traffic
        '''

        for i in range(config.NUMBER_GROUP):
            for j in range(config.NUMBER_PROTOCOL):
                for k in range(config.NUMBER_DEST_INDEX):
                    if self.current_attack_traffic_rate[i][j][k] <= self.current_defense_allowed_traffic_rate[i][j][k]:
                        self.current_utilization = self.current_utilization + self.current_attack_traffic_rate[i][j][k]
                        self.attack_traffic_induced = self.current_attack_traffic_rate


        self.current_utilization = self.current_utilization/(config.LINK_BANDWIDTH * Gb_TO_Mb)

        config.DETAILS_LOG_POINTER.write("Link utilization %s and Current State %s\n"%(self.current_utilization,self.current_observation))

        # Check if the attacker goal is met
        if self.current_utilization >= 1.0 and self.current_utilization <= config.MAX_LINK_UTILIZATION:
            config.OUT_LOG_POINTER.write("**** Goal Achieived at Time Steps : %s\n"%(self.time_sequence))

        #### TODO: CHARACTERIZE THE OBSERVATION ####
        '''
            1. Iterate through self.observation_list (Recall: you defined this while creating the observation space)
            2. Pick the index of the observation that matches current_utilization
            3. Save in self.current_observation
        '''
        for i in range (len(self.observation_list)-1):
            if (self.current_utilization>self.observation_list[i]) & (self.current_utilization < self.observation_list[i+1]):
                self.current_observation = i
                break
        if i >= len(self.observation_list):
            self.current_observation = len(self.observation_list)

        return self.current_observation


    def initial_attack_generation(self):
        ''' Geneate the initial traffic rate at the start of the emvironment '''
        for i in range(config.NUMBER_GROUP):
            self.init_attack_traffic_rate[i] = {}
            for j in range(config.NUMBER_PROTOCOL):
                self.init_attack_traffic_rate[i][j] = {}
                for k in range(config.NUMBER_DEST_INDEX):
                    self.init_attack_traffic_rate[i][j][k] = config.ATTACK_START_WITH_MINIMUM
        return


    def initial_defense_generation(self):
        if config.GIVEN_INIT_DEFENSE_POLICY_FLAG:
            file_name = config.GIVEN_INIT_DEFENSE_POLICY_FILE_NAME[self.file_index]
            self.init_defense_allowed_traffic_rate.clear()
            config.read_from_configuration_file(self.init_defense_allowed_traffic_rate, file_name)
        return





