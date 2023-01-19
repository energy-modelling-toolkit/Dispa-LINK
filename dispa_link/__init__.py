from .common import *
from .search import *
from .constants import *
from .preprocessing.get_timeseries_energyscope import *
from .preprocessing.get_capacities_energyscope import *
from .postprocessing.plots import *
from .dispa_link_functions import *

def get_git_revision_tag():
    """Get version of Dispa-LINK used for this run. tag + commit hash"""
    from subprocess import check_output
    try:
        return check_output(["git", "describe", "--tags", "--always"]).strip()
    except:
        return 'NA'

__gitversion__ = get_git_revision_tag()

# if somebody does "from dispaset_sidetools import *", this is what they will be able to access:
__all__ = ['commons',
           'search',
           'constants',
          ]