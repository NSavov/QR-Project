# Main file 
# QR project
# Nedko en Diede
# 14/10/16

import itertools

#this algorithm only works with correct models

# GLOBAL VARIABLES
#! all of the global variable except for the const part should go

#quantity spaces - const (not part of the input)
zp = ['zero','plus']
zpm = ['zero','plus','max']
derivs = ['-','0','+']

#quantities format -> ['name', quantity_space]
QSPACE_IND = 0
quantities = {'inflow': [zp], 'volume': [zpm],'outflow': [zpm]}

quantity_spaces = [zp, zpm, zpm]
INFLOW_Q = 0
INFLOW_D = 1
VOLUME_Q = 2
VOLUME_D = 3
OUTFLOW_Q = 4
OUTFLOW_D = 5

#these constraints are not part of the input - they are part of the algorithm
C1 = ['zero','-']
C2 = ['max', '+'] # think about this constraint
C_list = [C1]+[C2]

#variable correspondances - [from_qname, value, to_qname, value]
VC1 = ['volume', 'max', 'outflow', 'max']
VC2 = ['outflow', 'max', 'volume', 'max']
VC3 = ['volume', 'zero', 'outflow', 'zero']
VC4 = ['outflow', 'zero', 'volume', 'zero']
VC_list = [VC1]+[VC2]+[VC3]+[VC4]

#influences - [qname, dname]
I1 = ['inflow', 'volume', '+']
I2 = ['outflow', 'volume', '-']
I_list = [I1]+[I2]

#proportionalities(positive) - [dname, dname]
P1 = ['volume', 'outflow']
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
        for key, value in state.items(): # this is ugly
            if (value[0] == c[0]) and (value[1] == c[1]):
                return False
    return True

def valid_proportionalities(state):
    for p in P_list:
        if state[p[0]] != state[p[1]]:
            return False
    return True

def valid_influences(state):
    influences = {}
    possible_derivs = {}
    
    for i in I_list:
        if i[1] not in influences.keys():
            influences[i[1]] = []
        #if the current quantity is not zero
        if (state[i[0]][0] != quantities[i[0]][QSPACE_IND][0]):
            influences[i[1]].append(i[2])
        else: # if quantity is zero
            influences[i[1]].append(quantities[i[0]][QSPACE_IND][0])
            
    for key in state.keys(): 
        if key not in influences.keys():
            influences[key] = []    
        if key not in possible_derivs.keys():
            possible_derivs[key] = []  

        if ('+' in influences[key] and '-' in influences[key]) or not influences[key] :
            possible_derivs[key].extend(['+','0','-'])
        elif '+' in influences[key]:
            possible_derivs[key].append('+')
        elif '-' in influences[key]:
            possible_derivs[key].append('-')
        else: # if 0 in subset
            possible_derivs[key].append('0')
    
    for key, value in possible_derivs.items():
        if state[key][1] not in value:
            return False
    return True

def valid_vcs(state):
    for vc in VC_list:
        if (state[vc[0]][0] == vc[1]) and (state[vc[2]][0] != vc[3]):
            # print 'no', state
            return False
        # else:
            # print 'yes', state
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

def convert_to_states(comb_lst):
    all_states = []
    q_keys = list(quantities.keys())
    for comb in comb_lst:
        state = {}
        for i in range(0, len(comb), 2):
            state[q_keys[i/2]] = [comb[i], comb[i+1]]
        all_states.append(state)	
    return all_states

def set_states():
    all_states = []
    perm_sets = []
    for name, quantity in quantities.items():
        perm_sets.append(quantity[QSPACE_IND])
        perm_sets.append(derivs)

    all_combinations = list(itertools.product(*perm_sets))
    all_combinations_lst = [list(elem) for elem in all_combinations]
    all_states = convert_to_states(all_combinations_lst)

    
    all_val_states = []
    for state in all_states:
        if valid(state):
            all_val_states.append(state)

    for state in all_val_states:
        print state    
    print len(all_val_states)
    return all_val_states

def start():
    all_states = set_states()
    # get_connections(all_states)
    

#START PROGRAM
if __name__ == "__main__":
    start()