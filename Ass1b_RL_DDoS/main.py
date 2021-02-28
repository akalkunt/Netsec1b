import config
import components,attack
import environment

from stable_baselines import PPO2
from stable_baselines.common.policies import MlpPolicy


def initialize_env():
    ################ Creating Observation Space ############
    del components.observation_space[:] # Clear previous observation space if any
    utilization = config.LOW_LINK_UTILIZATION 
    
    #### TODO: DEFINE THE OBSERVATION SPACE ####
    '''
        Your observation space will consist of a list of the possible bandwidth 
        utilizations of the critical link. Add these to components.observation_space.

        The critical link bandwidth will not be more than 130%. This is defined in 
        config as MAX_LINK_UTILIZATION. Make sure that it matches the assignment 
        specification. Also, add an observation state to include all utilization 
        values greater than 130%. Refer to the assignment handout for more details.
    '''
    components.observation_space=[0, 0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4]
    ############# Creating Attack Action Space ################
    del components.attack_action_space[:] # Clear previous action space if any
    attack_id = 0
    #### TODO: DEFINE THE ACTION SPACE ####

    '''
        1. For every possible combination of botnet group, protocol, destination address and attacker
           traffic rate (that you defined in config.py), assign an attack_id (keep creating this on an
           incremental basis) and create an object of type attack_flow (refer to attack.py)
        2. Append each attack_flow object to the components.attack_action_space
    '''
    for i in range (1000):
        for group_id in range(5):
            for protocol_id in range(2):
                for destination_port in range (100):
                    for m in config.traffic_rate_multiplier:
                        a = attack.attack_flow(attack_id=i, group_id=group_id, protocol_id=protocol_id,  dest_port=destination_port, traffic_rate=m)
                        components.attack_action_space.append(a)


def run_agent():
    print("Start running the agent")
    ########## Creating the GYM environment ##########
    attack_env = environment.Attack_Env(components.observation_space,components.attack_action_space)
    #### TODO: CREATE THE AGENT/MODEL ####
    '''
        Create a PPO2 agent called attack_decision_agent and use MlpPolicy. Make sure to set the 
        environment as attack_env, and add cliprange, ent_coeff and learning_rate. 
    '''
    attack_decision_agent = PPO2(MlpPolicy, attack_env, ent_coef=0.01, learning_rate = 0.001, cliprange=0.02, verbose=1) # Define the agent here
 #   attack_decision_agent = PPO2(MlpPolicy, attack_env)    
    print("Agent created.\n")
    #### TODO: TRAIN THE AGENT ####
    '''
        Train the agent for config.TRAIN_ITERATIONS number of steps using the learn() function 
    '''
    attack_decision_agent.learn(total_timesteps = TRAIN_ITERATIONS)

    ################### Test the agent's decision-making #############
    print("Agent trained..\n") 
    # Test prediction on train defense policy
    config.OUT_LOG_POINTER = config.TEST_LOG_POINTER
    attack_env.TEST_RUNNING = True
    attack_env.file_index = 0
    attack_env.initial_defense_generation()
    config.TEST_LOG_POINTER.write("Result for initial allowed traffic rate\n")
    current_observation = attack_env.reset()
    if config.TAKE_DEFENSE_SNAPSHOT:
        config.write_configuration_files(attack_env.current_defense_allowed_traffic_rate,
                                         '%s_%s' % (config.DEFENSE_SNAPSHOT_FILE,1))
    for i in range(config.TEST_ITERATIONS):
        action, _ = attack_decision_agent.predict(current_observation)
        current_observation, reward, done, info = attack_env.step(action)
        if done:
            print("Test1 Complete!")
            break

    # Test prediction on test defense policy
    config.OUT_LOG_POINTER = config.TEST_LOG_POINTER
    attack_env.TEST_RUNNING = True
    attack_env.file_index = 1
    attack_env.initial_defense_generation()
    config.TEST_LOG_POINTER.write("Result for initial allowed traffic rate\n")
    current_observation = attack_env.reset()
    if config.TAKE_DEFENSE_SNAPSHOT:
        config.write_configuration_files(attack_env.current_defense_allowed_traffic_rate,
                                         '%s_%s' % (config.DEFENSE_SNAPSHOT_FILE,2))
    for i in range(config.TEST_ITERATIONS):
        action, _ = attack_decision_agent.predict(current_observation)
        current_observation, reward, done, info = attack_env.step(action)
        if done:
            print("Test2 Complete!")
            break


if __name__=='__main__':
    ########## Create Outout folder if no such folder exists ########
    try:
        import os
        os.makedirs('%s/Output'%(os.getcwd()))
        print(os.getcwd())
    except FileExistsError:
        print("File already exists")
        pass

    ############### CREATE LOG FILES ##############
    config.DETAILS_LOG_POINTER = open(config.DETAILS_LOG_FILE_NAME,'w')
    config.OUT_LOG_POINTER = open(config.OUT_LOG_FILE_NAME, 'w')
    config.TEST_LOG_POINTER = open(config.TEST_LOG_FILE_NAME, 'w')

    print("Starting the assignment")
    initialize_env()
    run_agent()

    ############## Close Log Files ###################
    config.DETAILS_LOG_POINTER.close()
    config.OUT_LOG_POINTER.close()
    config.TEST_LOG_POINTER.close()
