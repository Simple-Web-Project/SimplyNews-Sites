from . import gameinformer
from . import makeuseof
# from . import androidauthority
from . import heise
from . import theverge
# from . import itsfoss
from . import decentralizetoday
# from . import nypost
from . import theguardian
from . import shacknews
# from . import androidpolice
# from . import lefigaro
from . import franceinfo
from . import developpez
# from . import mediapart

from . import aljazeeranet

sites = {
    "gaming": {

        "shacknews.com": shacknews,
        "www.shacknews.com": shacknews,

        "gameinformer.com": gameinformer,
        "www.gameinformer.com": gameinformer,
    },
    "tech": {
        "makeuseof.com": makeuseof,
        "www.makeuseof.com": makeuseof,

        "heise.de": heise,
        "www.heise.de": heise,

        "theverge.com": theverge,
        "www.theverge.com": theverge,

        "dt.gl": decentralizetoday,

        "www.developpez.com": developpez,
        "developpez.com": developpez,
    },
    "news": {
        "theguardian.com": theguardian,
        "www.theguardian.com": theguardian,

        "aljazeera.net": aljazeeranet,
        "www.aljazeera.net": aljazeeranet,

        "www.francetvinfo.fr": franceinfo,
        "francetvinfo.fr": franceinfo,
        "www.franceinfo.fr": franceinfo,
        "franceinfo.fr": franceinfo,
    }


    # "androidauthority.com": androidauthority,
    # "www.androidauthority.com": androidauthority,

    # "www.androidpolice.com": androidpolice,
    # "androidpolice.com": androidpolice,

    # "itsfoss.com": itsfoss,
    # "www.itsfoss.com": itsfoss,

    # "nypost.com": nypost,
    # "www.nypost.com": nypost,

    # "lefigaro.fr": lefigaro,
    # "www.lefigaro.fr": lefigaro,

    # "www.mediapart.fr": mediapart,
    # "mediapart.fr": mediapart

}
