import config
class attack_flow:
    def __init__(self,attack_id,group_id=None,protocol_id=None,
                 dest_port=None,traffic_rate=None):
        self.attack_id = attack_id
        self.group_id = group_id
        self.protocol = protocol_id
        self.dest_port = dest_port
        self.traffic_rate = traffic_rate

    def attack_impact(self,attack_rate):
        print("attack impact called.\n")
        ''' This function changes the attack traffic rate '''
        config.DETAILS_LOG_POINTER.write("ID %s\n Set Traffic Rate %s of Group %s of Protocol %s of Destination Port %s\n" %(
            self.attack_id,self.traffic_rate,self.group_id,self.protocol,self.dest_port))

        #### TODO: ASSIGN TRAFFIC RATE TO THE ATTACK FLOW ####
        '''
            attack_rate is a nested dictionary. Its structure is as follows:
            {group id: {protocol: {destination port: {traffic rate}}}}

            For the botnet group id, protocol and destination port of the attack_flow object, assign the attack traffic rate.

        '''
        # The attack rate argument being passed to attack_impact is a nested dictionary in itself. 
        # We have to modify the traffic rate based on the multiplier in the attack_flow object (Note: traffic_rate in attack_flow holds the multiplier).
        #for i in range(config.NUMBER_GROUP):
        #    for j in range(config.NUMBER_PROTOCOL):
         #       for k in range(config.NUMBER_DEST_INDEX):
          #          if attack_rate[i][j][k]*self.traffic_rate <= MAX_TRAFFIC_RATE:
        attack_rate[self.group_id][self.protocol][self.dest_port] = attack_rate[self.group_id][self.protocol][self.dest_port]*self.traffic_rate
                 #   else:
                  #    attack_rate[i][j][k]=0
                ##Check if the traffic is greater than max/min. If it is, make it MAX/MIN
        print("Attack impact successful\n")
    def printProperties(self):
        print("Attack ID : %s"%(self.attack_id))
        print("Group %s Protocol %s Destination Port %s --> Traffic Rate %s"%
              (self.group_id,self.protocol,self.dest_port,self.traffic_rate))
