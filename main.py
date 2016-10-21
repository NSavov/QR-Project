# Main file 
# QR project
# Nedko en Diede
# 14/10/16
import copy
import itertools
import pprint

#this algorithm only works with correct models

# GLOBAL VARIABLES

trace = True
tc = 0
tab = '    '
trace_iter2 = True
trace_iter3 = True

#quantity spaces - const (not part of the input)
zp = ['zero','plus']
zpm = ['zero','plus','max']
derivs = ['-','0','+']

landmarks = ['zero', 'max']

#exogenous types - const
exogenous_types = ['decreasing','stable', 'increasing', 'random']


#these constraints are not part of the input - they are part of the algorithm
C1 = ['zero','-']
C2 = ['max', '+'] 
C_list = [C1]+[C2]

#quantities format -> ['name', quantity_space]
QSPACE_IND = 0
EXOGENOUS_IND = 1
quantities = {}

#variable correspondances - [from_qname, value, to_qname, value]
VC_list = []

#influences - [qname, dname]
I_list = []

#proportionalities(positive) - [dname, dname]
P_list = []

def get_string(state):
    string_state = state.replace('],',']\n').replace('{','').replace('}','').replace("'",'')
    return string_state

def get_state_string(state, eol):
    str = ""
    for key, value in state.items():
        str += key+" "+ value[0] + " "+ value[1] + eol
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

def get_arrow(all_states, new_state, exogenous, non_changable_derivs):
    global tc
    global trace_iter3
    children = []
    flag = False
    tc += 1
    if trace and trace_iter3:
                tfile.write( tc*tab + "Filter the possible matching children from all valid states:" + '\n')
    
    tc += 1
    if trace and trace_iter3:
                tfile.write( tc*tab + "Filter out all the states not matching the new quantities" + '\n')
                tfile.write( tc*tab + "Filter out all the states with different derivatives defined as non-changable" + '\n')
                tfile.write( tc*tab + "Filter out all the states which doesn't match an exogenous change" + '\n')
    #quantity filtering
    for state in all_states:
        for key, value in new_state.items():
            if value[0] != state[key][0]:
                flag = False
                break
        
        if not flag:
            flag = True
            continue
        
        
        for deriv_index in non_changable_derivs:
            if new_state[deriv_index][1] != state[deriv_index][1]:
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
    tc -= 1
    tc -= 1
    trace_iter3 = False
    return children
    
def subtract_one(state, quantity):
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
    
def get_const_landmark_quants(state):
    landmark_quants = []
    for key, value in state.items():
            if value[0] in landmarks and value[1] == '0':
                landmark_quants.append(key)
    return landmark_quants
    
def get_connections(all_states):
    global tc
    global trace_iter2
    
    exogenous = get_exogenous()
    if trace:
        tfile.write( tc*tab + "Find all exogenous quantities:" + str(exogenous) + '\n')
    
    inferred_derivs = get_inferred_derivs()
    if trace:
        tfile.write( tc*tab + "Find all derivatives that can be inferred from influences and proportionalities: " + str(inferred_derivs) + '\n')
    
    
    non_changable_derivs = list(set(quantities.keys()) - set(inferred_derivs) - set(exogenous))
    if trace:
        tfile.write( tc*tab + "Based on these find all the derivatives that cannot change from influences and proportionalities: "  + str(non_changable_derivs) + '\n')
    
    if trace:
        tfile.write( tc*tab + "Assume these non-changable derivatives to be random exogenous" + '\n')
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
    
    if trace:
        tfile.write( tc*tab + "For every state (example values are for first state only):" + '\n')
    tc +=1
    trace_iter = True
    for state in current_states:

        const_landmark_quants = get_const_landmark_quants(state)
        # print const_landmark_quants
        
        if trace and trace_iter:
            tfile.write( tc*tab + "Example state: " + get_state_string(state, ' ') + '\n')
            tfile.write( tc*tab + "Get the quantities that can change in the next step: " + str(const_landmark_quants) + '\n')
        
        if trace and trace_iter:
            tfile.write( tc*tab + "If there are no instantaneous changes: get a list of valid states with changes in every possible combination of changable quantities" + '\n')
        
        if trace and trace_iter:
            tfile.write( tc*tab + "If there are instantaneous changes - get one state with all of them applied" + '\n')
            
        quants, instant_quants = get_changable_quantities(state)
        if not instant_quants:
            combinations = get_changeable_combinations(quants)
            new_states = alter_quantities(state, combinations)
            new_states.append(state)
            if trace and trace_iter:
                tfile.write( (tc+1)*tab + "Example: Non-instantaneous transition, possible changed quantities: " + '\n')
                for new_state in new_states:
                    tfile.write( (tc+2)*tab + get_state_string(new_state,' ') + '\n')
        else:
            new_states = alter_quantities(state, [instant_quants])
            if trace and trace_iter:
                if not new_states:
                    tfile.write( (tc+1)*tab + "Example: Instantenious transition - no possible next state" + '\n')
                else:
                    tfile.write( (tc+1)*tab + "Example: Instantenious transition, next state (only magnitutes changed):" + get_state_string(new_states[0], ' ') + '\n')
        
        if trace and trace_iter2:
            tfile.write( tc*tab + "For all states with changed quantities:" + '\n')
        tc +=1
        for new_state in new_states:
            if trace and trace_iter2:
                tfile.write( tc*tab + "In case of instant change - find the next state with least amount of derivative changes" + '\n')
                tfile.write( tc*tab + "Otherwise: find all possible children without restrictions" + '\n')
            if not not instant_quants:
                children = get_arrow(all_states, new_state, exogenous, state.keys())
                if not children:
                    const_inst_derivs = []
                    for inst_quant in instant_quants:
                        if new_state[inst_quant][0] not in landmarks:
                            const_inst_derivs.append(inst_quant)
                    children = get_arrow(all_states, new_state, exogenous, const_inst_derivs)
                    if not not children:
                        children = [children[0]]
                
            else:
                children = get_arrow(all_states, new_state, exogenous, [])
            
            if trace and trace_iter2:
                tfile.write( tc*tab + "Connect the state with the found new states" + '\n')
            
            if trace and trace_iter2:
                    if not not children:
                        tfile.write( (tc+1)*tab + "Example: " + str(len(children)) + " found children: " + '\n')
                    for child in children:
                        tfile.write( (tc+2)*tab + get_state_string(all_states[child], ' ') + '\n')
            for child_ind in children:
                if all_states[child_ind] not in current_states:
                    current_states.append(all_states[child_ind])
            if len(children)>0 :
                ind = all_states.index(state)
                if ind in children:
                    children.remove(ind)
                neighbours_list[ind].extend(children)
            trace_iter2 = False
        trace_iter = False
        tc -= 1
    tc -= 1
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
    global tc
    all_states = []
    perm_sets = []
    
    if trace:
        tfile.write( tc*tab + "Generating all possible (valid and invalid) states" + '\n')
    
    
    for name, quantity in quantities.items():
        perm_sets.append(quantity[QSPACE_IND])
        perm_sets.append(derivs)
        
    all_combinations = list(itertools.product(*perm_sets))
    all_combinations_lst = [list(elem) for elem in all_combinations]
    all_states = convert_to_states(all_combinations_lst)
    if trace:
        tfile.write( tc*tab + str(len(all_states)) + " possible (valid and invalid) states found" + '\n')
        
    if trace:
        tfile.write( tc*tab + "Select only the valid states. For every state:" + '\n')
    
    tc += 1
    
    if trace:
        tfile.write( tc*tab + "Check if the VCs are satisfied" + '\n')
        tfile.write( tc*tab + "Check if the influences are satisfied" + '\n')
        tfile.write( tc*tab + "Check if the proportionalities are satisfied" + '\n')
        tfile.write( tc*tab + "Check if the algorithm constraints are satisfied" + '\n')
    all_val_states = []
    for state in all_states:
        if valid(state):
            all_val_states.append(state)
    tc -= 1
    
    if trace:
        tfile.write( tc*tab + str(len(all_val_states)) + " possible valid states found" + '\n')
        
    return all_val_states
    
def start():
    global tc
    if trace:
        tfile.write( tc*tab + "Find all states that are possible for this input\n")
    tc += 1
    all_states = set_states()
    tc -= 1
    
    if trace:
        tfile.write( tc*tab + "Find the edges of the graph" + '\n')
    
    tc += 1
    neighbours_list = get_connections(all_states)
    tc -= 1
    
    neighbours_list_str = []
    for neghbours in neighbours_list:
        neighs = []
        for ind in neghbours:
            if ind == len(all_states):
                neighs.append('Start')
            else:
                neighs.append(str(all_states[ind]))
        neighbours_list_str.append(neighs)
    
    f = open('../state-graph-as-list.txt','w')    
    for parent_list in neighbours_list_str:
        if len(parent_list) > 1:
            f.write('\nparent:\n\n')
            parentstate = get_string(parent_list[0])
            f.write("%s\n" % parentstate)
            f.write('\nchildren: ('+str(len(parent_list)-1)+')\n\n')
            for state in range(1,len(parent_list)):
                state = get_string(parent_list[state])
                f.write("%s\n\n" % state)
                
            f.write('\n====================\n')
    f.close()
    
    
    
#################################################
# below code is used for the graph
# decomment if pygraphiz package is installed only
#################################################
    
    neighbours_list_str = []
    for neghbours in neighbours_list:
        neighs = []
        for ind in neghbours:
            if ind == len(all_states):
                neighs.append('Start')
            else:
                neighs.append(str(all_states[ind]))
        neighbours_list_str.append(neighs)
     
    from graphviz import Digraph
    from string import ascii_lowercase

    dot = Digraph(comment='State-Graph')
    existent_nodes = {}
    unique_id = 0

    for sequence in range(len(neighbours_list_str)):
        if len(neighbours_list_str[sequence])>1:
            parentname = neighbours_list_str[sequence][0]
            if parentname not in existent_nodes:
                unique_id += 1
                parentid = ascii_lowercase[unique_id].upper()
                existent_nodes[parentname] = parentid
                plabelpart1 = parentid + '\n' 
                plabelpart2 = get_string(parentname)
                parentlabel = plabelpart1 + plabelpart2
                dot.node(parentid, parentlabel)
            for child in range(1, len(neighbours_list_str[sequence])):
                childname = neighbours_list_str[sequence][child]
                if childname not in existent_nodes:
                    unique_id += 1
                    childid = ascii_lowercase[unique_id].upper()
                    existent_nodes[childname] = childid
                    clabelpart1 = childid + '\n'
                    clabelpart2 = get_string(childname)
                    childlabel = clabelpart1 + clabelpart2
                    dot.node(childid, childlabel)
                dot.edge(existent_nodes[parentname], existent_nodes[childname])

    dot.render('../stategraph.gv', view=True)

        
    
def define_problem_1():
    global quantities
    global VC_list
    global I_list
    global P_list
    quantities = {'inflow': [zp, user_input], 'volume': [zpm, ''],'outflow': [zpm, ''], 'height': [zpm, ''], 'pressure': [zpm, '']}
    
    #variable correspondances - [from_qname, value, to_qname, value]
    VC1 = ['volume', 'max', 'outflow', 'max']
    VC2 = ['outflow', 'max', 'volume', 'max']
    VC3 = ['volume', 'zero', 'outflow', 'zero']
    VC4 = ['outflow', 'zero', 'volume', 'zero']
    
    VC5 = ['pressure', 'max', 'outflow', 'max']
    VC6 = ['outflow', 'max', 'pressure', 'max']
    VC7 = ['pressure', 'zero', 'outflow', 'zero']
    VC8 = ['outflow', 'zero', 'pressure', 'zero']
    
    VC9 = ['height', 'max', 'outflow', 'max']
    VC10 = ['outflow', 'max', 'height', 'max']
    VC11 = ['height', 'zero', 'outflow', 'zero']
    VC12 = ['outflow', 'zero', 'height', 'zero']
    VC_list = [VC1]+[VC2]+[VC3]+[VC4] +[VC5]+[VC6]+[VC7]+[VC8] + [VC9]+[VC10]+[VC11]+[VC12] 
    
    #influences - [qname, dname]
    I1 = ['inflow', 'volume', '+']
    I2 = ['outflow', 'volume', '-']
    I_list = [I1]+[I2]
    
    #proportionalities(positive) - [dname, dname]
    P3 = ['pressure', 'outflow']
    P1 = ['volume', 'height']
    P2 = ['height', 'pressure']
    P_list = [P1, P2, P3]
    
def define_problem_2():
    #quantities format -> ['name', quantity_space]
    global quantities
    global VC_list
    global I_list
    global P_list
    quantities = {'inflow': [zp, 'increasing'], 'volume': [zpm, ''],'outflow': [zpm, '']}
    
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

#START PROGRAM
if __name__ == "__main__":
    print '\n####\nQR-project Nedko Savov & Diede Rusticus. \n####\n\nCode for creating the graph is put in comments assuming the you do not have the proper pygraphviz package installed. If you do want to run the code and create the statediagram then decomment the code in the start() function.\n\nThe extended model is used to execute the program.'
    user_input = raw_input('\n\n>>>> Choose the exogonous value for inflow (i=increasing, d=decreasing, s=stable, r=random): ')
    if user_input == 'i':
        user_input = 'increasing'
    elif user_input == 'd':
        user_input = 'decreasing'
    elif user_input == 's':
        user_input = 'stable'
    elif user_input == 'r':
        user_input = 'random'
    else:
        print 'sorry no valid input was found, please try to execute the program one more time and enter a valid input.'
    print '\nYou chose '+user_input+' as the exogonous value for inflow. \nThe state-graph will be saved in a textfile in your directory and if the code is active, also in a pdf file.\n'
    global tfile
    tfile = open('trace.txt', 'w')
    define_problem_1()
    start()