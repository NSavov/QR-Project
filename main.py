# Main file 
# QR project
# Nedko en Diede
# 14/10/16

#class Quantity():

#class State(params):
#    def __init__(self, name):
#        inflow_q = params  
#                          
#class Influence():
#    def __init__(self, name):

# GLOBAL VARIABLES
zp = ['zero','plus']
zpm = ['zero','plus','max']
derivs = ['-','0','+']



I1 = ['inflow', 'plus', 'volume', '+']
I2 = ['outflow', 'plus', 'volume', '-']
I = [I1]+[I2]

P = ['volume', '+', 'outflow', '+']

INFLOW_Q = 0
INFLOW_D = 1
VOLUME_Q = 2
VOLUME_D = 3
OUTFLOW_Q = 4
OUTFLOW_D = 5

VC1 = [VOLUME_Q, 'max', OUTFLOW_Q, 'max']
VC2 = [OUTFLOW_Q, 'max', VOLUME_Q, 'max']
VC3 = [VOLUME_Q, 'zero', OUTFLOW_Q, 'zero']
VC4 = [OUTFLOW_Q, 'zero', VOLUME_Q, 'zero']
VCS = [VC1]+[VC2]+[VC3]+[VC4]
        
def set_initial_states():
    all_states = []
    #getting all permutations
    for i in zp:
        for j in zpm:
            for k in zpm:
                for l in derivs:
                    for m in derivs:
                        for n in derivs:
                            all_states.append([i,l,j,m,k,n])
    print len(all_states)
    for i in range(len(all_states)):
        for vc in VCS:
#            print vc
#            print state
#            print state[vc[0]] == vc[1]
#            print state[vc[2]] != vc[3]
            state = all_states[i]
            if (state[vc[0]] == vc[1]) and (state[vc[2]] != vc[3]):
#                print 'removed'
                all_states.remove(state)
                break
#            else: 
#                print 'NOTNOTNOTNOTNOT'
                
#    print len(all_states)
    for state in all_states:
        print state
#                



#    state = State(params)
#    if state.inflow_q == zpm[1]: # if inflow is plus
#        volume_d = derivs[2] # the derivative of the volume is +
   
#START PROGRAM
if __name__ == "__main__":
    set_initial_states()