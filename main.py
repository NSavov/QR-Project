# Main file 
# QR project
# Nedko en Diede
# 14/10/16

# GLOBAL VARIABLES
zp = ['zero','plus']
zpm = ['zero','plus','max']
derivs = ['-','0','+']

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
VC_list = [VC1]+[VC2]+[VC3]+[VC4]

I1 = [INFLOW_Q, 'zero', VOLUME_D, '+']
I2 = [OUTFLOW_Q, 'zero', VOLUME_D, '-']
I_list = [I1]+[I2]

P1 = [VOLUME_D, OUTFLOW_D]
P_list = [P1]

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
    else:
        return True

def set_states():
    all_states = []
    
    #getting all permutations
    for i in zp:
        for j in zpm:
            for k in zpm:
                for l in derivs:
                    for m in derivs:
                        for n in derivs:
                            all_states.append([i,l,j,m,k,n])
    all_val_states = []
    for state in all_states:
        if valid(state):
            all_val_states.append(state)

    for state in all_val_states:
        print state
    print len(all_val_states)

#START PROGRAM
if __name__ == "__main__":
    set_states()