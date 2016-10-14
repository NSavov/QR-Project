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
                    
    for state in all_states:
        print state
    
    
    
                       
#    state = State(params)
#    if state.inflow_q == zpm[1]: # if inflow is plus
#        volume_d = derivs[2] # the derivative of the volume is +
   
#START PROGRAM
if __name__ == "__main__":
    set_initial_states()