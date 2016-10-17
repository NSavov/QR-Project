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

def subtract_one(state, quantity):
    # print state[quantity]
    new_state = state.copy()
    index = quantities[quantity][QSPACE_IND].index(state[quantity][0])
    if index != 0:
        new_state[quantity][0] = quantities[quantity][QSPACE_IND][index-1] 
    return new_state
    
def add_one(state, quantity):
    new_state = state.copy()
    index = quantities[quantity][QSPACE_IND].index(state[quantity][0])
    if index != len(quantities[quantity][QSPACE_IND])-1:
        new_state[quantity][0] = quantities[quantity][QSPACE_IND][index+1]
    return new_state
        
def alter_quantities(state, combinations):
    new_state = state.copy()
    new_states = []
    for comb in combinations:
        # print comb
        for quantity in list(comb):
            # print quantity
            if state[quantity][1] == '+':
                new_states.append(add_one(new_state, quantity))
            else:
                new_states.append(subtract_one(new_state, quantity))
    return new_states
    
def get_changeable_combinations(list_of_indices):
    combinations = []
    for m in range(1, len(list_of_indices)+1):
        combinations.extend(list(set(itertools.combinations(list_of_indices, m))))
    return combinations
             
    
def get_changable_quantities(state):
    quants = []
    for key, value in state.items():
        if value[1] != '0':
           #if quantity is equal  the last value from q space and if the derivative is +, then we don't add it
           if not (value[0]==quantities[key][QSPACE_IND][-1] and value[1] == '+') and not (value[0]==quantities[key][QSPACE_IND][0] and value[1] == '-'):
                quants.append(key)
    return quants
    
def get_changable_derivs():
    changable_derivs = []
    for i in I_list:
        changable_derivs.append(i[1])
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
        combinations = get_changeable_combinations(quants)
        new_states = alter_quantities(state, combinations)
        print state
        print new_states
        print ''

def valid_constraints(state):
    for c in C_list:
        for key, value in state.items():
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

    # for state in all_val_states:
        # print state    
    # print len(all_val_states)
    return all_val_states

def start():
    all_states = set_states()
    get_connections(all_states)
    

#START PROGRAM
if __name__ == "__main__":
    start()