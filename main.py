# Main file 
# QR project
# Nedko en Diede
# 14/10/16
import copy
import itertools
import networkx as nx
import matplotlib.pyplot as plt
from networkx_viewer import Viewer
import pprint

#this algorithm only works with correct models

# GLOBAL VARIABLES
#! all of the global variable except for the const part should go

#quantity spaces - const (not part of the input)
zp = ['zero','plus']
zpm = ['zero','plus','max']
derivs = ['-','0','+']

landmarks = ['zero', 'max']

#exogenous types - const
exogenous_types = ['decreasing','stable', 'increasing', 'random']
#quantities format -> ['name', quantity_space]
QSPACE_IND = 0
EXOGENOUS_IND = 1
quantities = {'inflow': [zp, 'increasing'], 'volume': [zpm, ''],'outflow': [zpm, '']}

#these constraints are not part of the input - they are part of the algorithm
C1 = ['zero','-']
C2 = ['max', '+'] 
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

def get_state_string(state):
    str = ""
    for key, value in state.items():
        str += key+" " + value[0] + " " + value[1] + '\n'
    return str

def get_next_derivs_exogenous(quantity_vals, exog):
    type = quantities[exog][EXOGENOUS_IND]
    possible_derivs = []
    if type == 'decreasing':
        if quantity_vals[0]==quantities[exog][QSPACE_IND][0]:
            possible_derivs = ['0']
        else:
            possible_derivs = ['-']
            
    elif type=='stable':
        possible_derivs = ['0']
        
    elif type =='increasing':
        if quantity_vals[0]=='max':
            possible_derivs = ['0']
        else:
            possible_derivs = ['+']
            
    elif type == 'random':
        possible_derivs = derivs
    return possible_derivs

def get_arrow(all_states, new_state, exogenous):
    children = []
    flag = False
    #quantity filtering
    for state in all_states:
        
        for key, value in new_state.items():
            if value[0] != state[key][0]:
                flag = False
                break
        
        if not flag:
            flag = True
            continue
        
        for exog in exogenous:
            possible_derivs = get_next_derivs_exogenous(new_state[exog], exog)
            if state[exog][1] not in possible_derivs:
                flag = False
                break
                
        if not flag:
            flag = True
            continue
        
        for key, value in state.items():
            if abs(derivs.index(state[key][1]) - derivs.index(new_state[key][1])) > 1:
                flag = False
                break
        
        if not flag:
            flag = True
            continue        
        children.append(all_states.index(state))
    return children
    
def subtract_one(state, quantity):
    new_state = state.copy()
    index = quantities[quantity][QSPACE_IND].index(state[quantity][0])
    if index != 0:
        new_state[quantity][0] = quantities[quantity][QSPACE_IND][index-1] 
    if new_state[quantity][0] == quantities[quantity][QSPACE_IND][0] :
        new_state[quantity][1] = '0'
    return new_state
    
def add_one(state, quantity):
    new_state = state.copy()
    index = quantities[quantity][QSPACE_IND].index(state[quantity][0])
    if index != len(quantities[quantity][QSPACE_IND])-1:
        new_state[quantity][0] = quantities[quantity][QSPACE_IND][index+1]
    return new_state
       
def alter_quantities(state, combinations):
    new_states = []
    for comb in combinations:
        new_state = copy.deepcopy(state)
        for quantity in comb:
            if state[quantity][1] == '+':
                new_state = add_one(new_state, quantity)
            else:
                new_state = subtract_one(new_state, quantity)
        new_states.append(new_state)
        
    return new_states
    
def get_changeable_combinations(list_of_indices):
    combinations = []
    for m in range(1, len(list_of_indices)+1):
        combinations.extend(list(set(itertools.combinations(list_of_indices, m))))
    return combinations
             
    
def get_changable_quantities(state):
    quants = []
    instant_quants = []
    for key, value in state.items():
        if value[1] != '0':
        #if quantity is equal  the last value from q space and if the derivative is +, then we don't add it
           if not (value[0]==quantities[key][QSPACE_IND][-1] and value[1] == '+') and not (value[0]==quantities[key][QSPACE_IND][0] and value[1] == '-'):
                if value[0] in landmarks:
                    instant_quants.append(key)
                else:
                    quants.append(key)
    return quants, instant_quants

def get_start_derivs_exogenous(exog):
    type = quantities[exog][EXOGENOUS_IND]
    possible_derivs = []
    if type == 'decreasing':
        possible_derivs = ['-']
            
    elif type=='stable':
        possible_derivs = ['0']
        
    elif type =='increasing':
        possible_derivs = ['+']
            
    elif type == 'random':
        possible_derivs = derivs
    return possible_derivs
    
def get_inferred_derivs():
    inferred_derivs = []
    for i in I_list:
        inferred_derivs.append(i[1])
    inferred_derivs = list(set(inferred_derivs))
    for p in P_list:
        if p[0] in inferred_derivs:
            inferred_derivs.append(p[1])
    inferred_derivs = list(set(inferred_derivs))
    return inferred_derivs #list of derivs indices which can change

def get_exogenous():
    exogenous = []
    for key, value in quantities.items():
        if value[EXOGENOUS_IND] in exogenous_types:
            exogenous.append(key) 
    return exogenous
    
def get_connections(all_states):
    exogenous = get_exogenous()
    inferred_derivs = get_inferred_derivs()
    non_changable_derivs = list(set(quantities.keys()) - set(inferred_derivs) - set(exogenous))
    
    for derivative in non_changable_derivs:
        quantities[derivative][EXOGENOUS_IND] = 'random'
        exogenous.append(derivative)
    
    current_states = []
    for state in all_states:
        for exog in exogenous:
            if state[exog][1] in get_start_derivs_exogenous(exog):
                current_states.append(state)
    neighbours_list = [[i] for i in range(len(all_states)+1) ]
    neighbours_list[-1].extend([all_states.index(current_state) for current_state in current_states ])
    for state in current_states:
        quants, insant_quants = get_changable_quantities(state)
        if not insant_quants:
            combinations = get_changeable_combinations(quants)
            new_states = alter_quantities(state, combinations)
        else:
            # instant_combinations = get_changeable_combinations(insant_quants)
            new_states = alter_quantities(state, [insant_quants])
        
        for new_state in new_states:
            children = get_arrow(all_states, new_state, exogenous)
            for child_ind in children:
                if all_states[child_ind] not in current_states:
                    current_states.append(all_states[child_ind])
            if len(children)>0 :
                neighbours_list[all_states.index(state)].extend(children)
    return neighbours_list

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

    return all_val_states
    
def start():
    all_states = set_states()
    neighbours_list = get_connections(all_states)
    
    neighbours_list_str = []
    for neghbours in neighbours_list:
        neighs = []
        for ind in neghbours:
            if ind == len(all_states):
                neighs.append('Start')
            else:
                neighs.append(str(all_states[ind]))
        neighbours_list_str.append(neighs)
    
    pprint.pprint(neighbours_list_str)
    
    G=nx.DiGraph()
    
    G.add_nodes_from([get_state_string(state) for state in all_states ])
    G.add_node('Start')
    for neghbours in neighbours_list[:-1]:
        G.add_edges_from([(get_state_string(all_states[neghbours[0]]), get_state_string(all_states[neghbours[i]])) for i in range(1,len(neghbours))])

    G.add_edges_from([('Start', get_state_string(all_states[neighbours_list[-1][i]])) for i in range(1,len(neighbours_list[-1]))])
    G.remove_nodes_from(nx.isolates(G))
    
    # nx.write_gexf(G, 'graph.gexf')
    # labels = {}
    # for i in range(len(all_states)):
        # labels[i] = '$' + (str(all_states[i])) + '$'
    
    # pprint.pprint(labels)
    # print labels
    # nx.draw(G)
    # nx.draw_networkx_labels(G,nx.spring_layout(G), labels, font_size=16)
    # plt.show()
    app = Viewer(G)
    app.mainloop()
    

#START PROGRAM
if __name__ == "__main__":
    start()