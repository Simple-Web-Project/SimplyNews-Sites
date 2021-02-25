from . import gameinformer
from . import makeuseof
from . import androidauthority
from . import heise
from . import theverge
from . import itsfoss
from . import decentralizetoday
from . import nypost
from . import theguardian
from . import shacknews
from . import androidpolice
from . import lefigaro
from . import franceinfo

sites = {
    "shacknews.com": shacknews,
    "www.shacknews.com": shacknews,

    "gameinformer.com": gameinformer,
    "www.gameinformer.com": gameinformer,

    "makeuseof.com": makeuseof,
    "www.makeuseof.com": makeuseof,

    "androidauthority.com": androidauthority,
    "www.androidauthority.com": androidauthority,

    "www.androidpolice.com": androidpolice,
    "androidpolice.com": androidpolice,

    "heise.de": heise,
    "www.heise.de": heise,

    "theverge.com": theverge,
    "www.theverge.com": theverge,

    "itsfoss.com": itsfoss,
    "www.itsfoss.com": itsfoss,

    "dt.gl": decentralizetoday,

    "nypost.com": nypost,
    "www.nypost.com": nypost,

    "theguardian.com": theguardian,
    "www.theguardian.com": theguardian,

    "lefigaro.fr": lefigaro,
    "www.lefigaro.fr": lefigaro,


    #TODO: Fix franceinfo parsing
    #"www.francetvinfo.fr": franceinfo,
    #"francetvinfo.fr": franceinfo,
    #"www.franceinfo.fr": franceinfo,
    #"franceinfo.fr": franceinfo,

}
