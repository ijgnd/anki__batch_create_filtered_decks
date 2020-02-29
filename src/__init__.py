# Add-on for Anki
# License: AGPLv3
# Copyright: 2020- ijgnd

from pprint import pprint as pp

from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo, tooltip


def gc(arg, fail=False):
    conf = mw.addonManager.getConfig(__name__)
    if conf:
        return conf.get(arg, fail)
    return fail


#adapted from saveConf from dyndeckconf.py
def CreateFilteredDeckWithoutGUI(name, searchtext, limitvalue, order, resched, steps, previewDelay):
    if name in mw.col.decks.allNames():
        return name
    did = mw.col.decks.newDyn(name)
    d = mw.col.decks.current()

    d['resched'] = resched
    d["delays"] = None
    if mw.col.schedVer() == 1 and steps:
        if steps:
            d["delays"] = steps
        else:
            d["delays"] = None
    d["terms"] = [[searchtext, limitvalue, order]]
    if resched:
        d["previewDelay"] = 0
    else:
        d["previewDelay"] = previewDelay    
    mw.col.decks.save(d)
    mw.col.sched.rebuildDyn(did)
    return did


def batch_create_filtered_decks():
    mirrorlist = gc("mirror all decks as filtered")
    if not (mirrorlist and isinstance(mirrorlist, list)):
        tooltip('Invalid value for "mirror all decks as filtered". Aborting ...')
    regDeckIds = [d["id"] for d in mw.col.decks.all() if not d["dyn"]]
    mw.progress.start()
    for idx, sl in enumerate(mirrorlist):
        ## verify
        if not isinstance(sl, dict):
            tooltip('Invalid entry no {} in "mirror all decks as filtered"'.format(idx))
            mw.progress.finish()
            return
        additional = sl.get("additional search term", None)
        if not (additional and isinstance(additional, str)):
            tooltip('Invalid entry no {} in "mirror all decks as filtered"-"additional search term"'.format(idx))
            mw.progress.finish()
            return
        order = sl.get("selected by/order", False)
        if not (order and isinstance(order, int)):
            tooltip('Invalid entry no {} in "mirror all decks as filtered"-"selected by/order"'.format(idx))
            mw.progress.finish()
            return
        parent = sl.get("parent deck name", False)
        if not (parent and isinstance(parent, str)):
            tooltip('Invalid entry no {} in "mirror all decks as filtered"-"parent deck name"'.format(idx))
            mw.progress.finish()
            return
        resched = sl.get("reschedule based on answers")
        if not isinstance(resched, bool):
            tooltip('Invalid entry no {} in "mirror all decks as filtered"-"reschedule based on answers"'.format(idx))
            mw.progress.finish()
            return            
        maxcards = sl.get("max cards", 9999)
        if not (maxcards and isinstance(maxcards, int)):
            maxcards = 9999
        steps = False # gc("steps")
        previewDelay = 0

        ## abort if parent exists
        if mw.col.decks.byName(parent):
            showInfo("The add-on doesn't work in the parent deck already exists. Aborting ...")
            mw.progress.finish()
            return

        ## make sure to build most nested decks first
        nestedlevels = {}
        for did in regDeckIds:
            deck = mw.col.decks.get(did)
            n = deck['name'].count("::")
            nestedlevels.setdefault(n, []).append(str(did))

        ## actually build them
        for level in sorted(nestedlevels.keys(), reverse=True):
            for did in nestedlevels[level]:
                odeck = mw.col.decks.get(did)
                # check for subdecks:
                hassubdecks = False
                for d in mw.col.decks.all(): 
                    if d["name"].startswith(odeck['name'] + "::"):
                        hassubdecks = True
                        continue
                # check if it has cards that are not in subdecks:
                cids = mw.col.findCards(f'''deck:"{odeck['name']}" -deck:"{odeck['name']}::*"''')
                if hassubdecks and cids:
                    # I need to create a special subdeck for cards that are only in the parent
                    # since a filterd deck can't have other filtered decks
                    filtered_name = parent.rstrip("::") + "::" + odeck['name'] + "::" + "!!cards that are only in parent"
                else:
                    filtered_name = parent.rstrip("::") + "::" + odeck['name']
                searchtext = 'deck:"{}"'.format(odeck['name']) + " " + additional
                CreateFilteredDeckWithoutGUI(filtered_name, searchtext, maxcards, order, resched, steps, previewDelay)
        mw.reset()
        mw.moveToState("deckBrowser")
        mw.progress.finish()


abf = QAction("Batch create filtered decks", mw)
abf.triggered.connect(batch_create_filtered_decks)
mw.form.menuTools.addAction(abf)
