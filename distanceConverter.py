def meterstoyards(d):
    return d*1.09361
def meterstofeet(d):
    return d//.3048
def feettoinches(d):
    return d*12
 

def convert(m:float):
    
    if m < 20.0:
        
        if (m%.3048) == 0:
            m_in_ft = meterstofeet(m)
            return str(m_in_ft) + "ft."
        else:
            m_in_ft = round(meterstofeet(m))
            inches = m / .3048 % 1 * 12
            
            inches_round = round(inches)
            return str(m_in_ft) + " ft "+ str(inches_round)+" in."
    else:
        #Convert to yards
        m_to_yds =  round(meterstoyards(m))
        return str(m_to_yds)+" yds"
     