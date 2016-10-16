# Main file 
# QR project
# Nedko en Diede
# 14/10/16


import itertools

# GLOBAL VARIABLES
zp = ['zero','plus']
zpm = ['zero','plus','max']
derivs = ['-','0','+']

quantity_spaces = [zp, zpm, zpm]
INFLOW_Q = 0
INFLOW_D = 1
VOLUME_Q = 2
VOLUME_D = 3
OUTFLOW_Q = 4
OUTFLOW_D = 5

C1 = ['zero','-']
C2 = ['max', '+'] # think about this constraint
C_list = [C1]+[C2]

VC1 = [VOLUME_Q, 'max', OUTFLOW_Q, 'max']
VC2 = [OUTFLOW_Q, 'max', VOLUME_Q, 'max']
VC3 = [VOLUME_Q, 'zero', OUTFLOW_Q, 'zero']
VC4 = [OUTFLOW_Q, 'zero', VOLUME_Q, 'zero']
VC_list = [VC1]+[VC2]+[VC3]+[VC4]

I1 = [INFLOW_Q, 'zero', VOLUME_D, '+']
I2 = [OUTFLOW_Q, 'zero', VOLUME_D, '-']
I_list = [I1]+[I2]

P1 = [VOLUME_D, OUTFLOW_D]
P_list = [P1]


def alter_quantities(state, list_of_indices, derivs):
    combinations = []
    for m in range(len(list_of_indices)):
        combinations.append(list(set(itertools.combinations(list_of_indices, m))))
    return combinations
#    print combinations
             
    
def get_changable_quantities(state):
    quants = []
    for deriv in range(1,6,2):
        quantity = deriv-1
        if state[deriv] != '0':
#            if not (state[quantity] == quantity_spaces[deriv/2][-1] and state[deriv] == '+'):
            quants.append(quantity)
    return quants
    
def get_changable_derivs():
    changable_derivs = []
    for i in I_list:
        changable_derivs.append(i[2])
    changable_derivs = list(set(changable_derivs))
    for p in P_list:
        if p[0] in changable_derivs:
            changable_derivs.append(p[1])
    changable_derivs = list(set(changable_derivs))
    return changable_derivs #list of derivs indices which can change

def get_connections(all_states):
    changable_derivs = get_changable_derivs()
    for state in all_states:
        quants = get_changable_quantities(state)
#        print state
#        print quants
        combinations = alter_quantities(state, quants, changable_derivs) # 
        

def valid_constraints(state):
    for c in C_list:
        for i in range(0,6,2): # this is ugly
            if (state[i] == c[0]) and (state[i+1] == c[1]):
                return False
    return True

def valid_proportionalities(state):
    for p in P_list:
        if state[p[0]] != state[p[1]]:
            return False
    return True

def valid_influences(state):
    influences = [[],[],[]]
    possible_derivs = [[],[],[]]
    
    for i in I_list:
        if (state[i[0]] != i[1]):
            influences[i[2]/2].append(i[3])
        else: # if quantity is zero
            influences[i[2]/2].append('0')
            
    for i in range(len(influences)): 
        if ('+' in influences[i] and '-' in influences[i]) or not influences[i] :
            possible_derivs[i].extend(['+','0','-'])
        elif '+' in influences[i]:
            possible_derivs[i].append('+')
        elif '-' in influences[i]:
            possible_derivs[i].append('-')
        else: # if 0 in subset
            possible_derivs[i].append('0')
            
    for i in range(len(possible_derivs)):
        if state[i*2+1] not in possible_derivs[i]:
            return False
    return True

def valid_vcs(state):
    for vc in VC_list:
        if (state[vc[0]] == vc[1]) and (state[vc[2]] != vc[3]):
            return False
    return True

def valid(state): 
    if not valid_vcs(state):
        return False
    elif not valid_influences(state):
        return False
    elif not valid_proportionalities(state):
        return False
    elif not valid_constraints(state):
        return False
    else:
        return True

def set_states():
    all_states = []
    
    #getting all permutations
    for in_q in quantity_spaces[0]:
        for vol_q in quantity_spaces[1]:
            for out_q in quantity_spaces[2]:
                for in_d in derivs:
                    for vol_d in derivs:
                        for out_d in derivs:
                            all_states.append([in_q,in_d,vol_q,vol_d,out_q,out_d])
    
    all_val_states = []
    for state in all_states:
        if valid(state):
            all_val_states.append(state)

    for state in all_val_states:
        print state
    
    return all_val_states

#START PROGRAM
if __name__ == "__main__":
    all_states = set_states()
    get_connections(all_states)