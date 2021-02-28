#### TODO: DEFINE THE CONFIGURATIONS ####
'''
    Set the following parameters as per assignment specifications
'''
NUMBER_GROUP = 5
NUMBER_PROTOCOL = 2
NUMBER_DEST_INDEX = 100

LINK_BANDWIDTH = 6 ######### In Gb
MIN_TRAFFIC_RATE = 1 ##### Min Traffic Rate of attack bots (In Mbps)
MAX_TRAFFIC_RATE = 12 ########## Max Traffic Rate of attack bots (In Mbps)
ATTACK_START_WITH_MINIMUM = 1 ########## Initial attack traffic rate (In Mbps)
LOW_LINK_UTILIZATION = 3 ############ all links utilizations under this value is considered same
MAX_LINK_UTILIZATION = 7.8 ######## This is the naximum link utilization, the attacker wants to achieve
BACKGROUND_TRAFFIC_MIN = 2.4 ######### In Gb
BACKGROUND_TRAFFIC_MAX = 3.6 ######### In Gb

#### TODO: DEFINE THE ATTACK TRAFFIC RATES ####
'''
        We define our action space as four possible actions - 
        1. Increase traffic rate by 2 times
        2. Increase traffic rate by 4 times
        3. Decrease traffic rate by 2 times
        4. Decrease traffic rate by 4 times

        Create a list of traffic rate multiplying factors that we will use to create the action space
    '''
traffic_rate_multiplier = [2.0, 4.0, 0.5, 0.25] # Create the multiplier list here

#### INCENTIVES/PENALIZATIONS ####
'''
    These will be used to calculate the reward at each step.
    We are giving you some initial values, but feel free to
    play around with these as you deem fit!
'''
INCENTIVE_INCREASED_LINK_UTILIZATION = 30
INCENTIVE_WITHIN_GOAL = 10 #Changed this.
PENALTY_OVER_UTILIZATION = 1
PENALTY_LESS_PREV = 2 ##Added this.

TRAIN_ITERATIONS = 2500 # No of training iterations
TEST_ITERATIONS = 20000 # No of test iterations

TAKE_DEFENSE_SNAPSHOT = True ######### Set True when to take the status of current defense allowed rate
DEFENSE_SNAPSHOT_FILE = 'Input/defense_policy_snapshot'


###### NAMES OF LOG FILES ######

DETAILS_LOG_FILE_NAME = 'Output/details_log'
OUT_LOG_FILE_NAME =  'Output/result_log'
TEST_LOG_FILE_NAME = 'Output/result_test_log'

DETAILS_LOG_POINTER = None
OUT_LOG_POINTER = None
TEST_LOG_POINTER = None

GIVEN_INIT_DEFENSE_POLICY_FLAG = True # If true, take the initial defense traffic allowed rate from the following file
GIVEN_INIT_DEFENSE_POLICY_FILE_NAME = ['Input/train_defense_policy', 'Input/test_defense_policy'] 
ATTACK_SNAPSHOT_FILE_NAME = 'Output/attack_rate_snap' ###### Save the attack configurations of all combinations in the file ######


###### HELPER METHODS ######

def write_configuration_files(policy_conf, file_name, file_mode='w', file_index=None,
                              wr_bf=False, util=None, benign_traffic=None):
    file_pointer = open(file_name,file_mode)
    if wr_bf:
        file_pointer.write("New Attack Snapshot\n")
    if file_index is None:
        file_pointer.write("Group ID, Protocols, Destination Ports, Traffic Rate\n")
    else:
        file_pointer.write("%s\n" % (file_index))
        file_pointer.write("%s\n" % (util))
        if benign_traffic is None:
            file_pointer.write("Group ID, Protocols, Destination Ports, Traffic Rate\n")
        else:
            file_pointer.write('%s\n'%(benign_traffic))
    for group in policy_conf:
        for protocol in policy_conf[group]:
            for dst_port in policy_conf[group][protocol]:
                file_pointer.write('%s,%s,%s,%s\n'%(group,protocol,dst_port,policy_conf[group][protocol][dst_port]))
    file_pointer.write('\n')
    file_pointer.close()

def read_from_configuration_file(policy_conf,file_name):
    for group in range(NUMBER_GROUP):
        policy_conf[group] = {}
        for protocol in range(NUMBER_PROTOCOL):
            policy_conf[group][protocol] = {}
            for dst_port in range(NUMBER_DEST_INDEX):
                policy_conf[group][protocol][dst_port] = {}

    file_pointer = open(file_name, 'r+')
    for line in file_pointer:
        if "Group" in line:
            continue
        line = line.replace('\n','')
        if line=='':
            continue
        line = line.split(',')
        policy_conf[int(line[0])][int(line[1])][int(line[2])] = float(line[3])
    file_pointer.close()







