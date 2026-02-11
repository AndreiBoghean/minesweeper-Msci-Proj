import gac
import rac

# moving to separate file so the individual modules are smaller and less confusing to navigate

def generalizedArcConsistency(*args, **kwargs):
    return gac.generalizedArcConsistency(*args, **kwargs)

def relationalArcConsistency(*args, **kwargs):
    return rac.relationalArcConsistency(*args, **kwargs)
