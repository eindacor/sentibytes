from sb_sentibyte import sentibyte

def generateSentibyte(sb_file, the_truth):
    file = open(sb_file, 'r')
    lines = file.readlines()
    file.close()
    lines = [line.replace(' ', '') for line in lines if '$' not in line]
    lines = [line.replace('\n', '') for line in lines]
    name = "--" + lines[0].replace('Name=', '') + "--"
    lines.pop(0)
    
    personal_traits = {}
    interpersonal_traits = {}
    desired_traits = {}
    
    for line in lines:
        array = line.partition('=')
    
        trait = array[0]
        trait_type = None
        
        if trait[0] == 'p':
            trait_type = 'personal'
        elif trait[0] == 'i':
            trait_type = 'interpersonal'
        elif trait[0] == 'd':
            trait_type = 'desired'
        
        trait = trait[2:]
        
        values = array[2]
        lower = int(values[:2])
        base = int(values[3:5])
        upper = int(values[6:])
    
        if trait_type == 'personal':
            personal_traits[trait] = [lower, base, upper]
            
        elif trait_type == 'interpersonal':
            interpersonal_traits[trait] = [lower, base, upper]
            
        elif trait_type == 'desired':
            desired_traits[trait] = [lower, base, upper]
            
    new_sb = sentibyte(name, the_truth)
    
    for trait in personal_traits.keys():
        new_sb.p_traits[trait].params['lower'] = personal_traits[trait][0]
        new_sb.p_traits[trait].params['base'] = personal_traits[trait][1]
        new_sb.p_traits[trait].params['current'] = personal_traits[trait][1]
        new_sb.p_traits[trait].params['upper'] = personal_traits[trait][2]
        new_sb.p_traits[trait].update()
        
    for trait in interpersonal_traits.keys():
        new_sb.i_traits[trait].params['lower'] = interpersonal_traits[trait][0]
        new_sb.i_traits[trait].params['base'] = interpersonal_traits[trait][1]
        new_sb.i_traits[trait].params['current'] = interpersonal_traits[trait][1]
        new_sb.i_traits[trait].params['upper'] = interpersonal_traits[trait][2]
        new_sb.i_traits[trait].update()
        
    for trait in desired_traits.keys():
        new_sb.d_traits[trait].params['lower'] = desired_traits[trait][0]
        new_sb.d_traits[trait].params['base'] = desired_traits[trait][1]
        new_sb.d_traits[trait].params['current'] = desired_traits[trait][1]
        new_sb.d_traits[trait].params['upper'] = desired_traits[trait][2]
        new_sb.d_traits[trait].update()
        
    return new_sb