# Add-on for Anki
# License: AGPLv3
# Copyright: 2020- ijgnd


from aqt import mw
from aqt.qt import *
from aqt.utils import tooltip


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
            return
        additional = sl.get("additional search term", None)
        if not (additional and isinstance(additional, str)):
            tooltip('Invalid entry no {} in "mirror all decks as filtered"-"additional search term"'.format(idx))
            return
        order = sl.get("selected by/order", False)
        if not (order and isinstance(order, int)):
            tooltip('Invalid entry no {} in "mirror all decks as filtered"-"selected by/order"'.format(idx))
            return
        parent = sl.get("parent deck name", False)
        if not (parent and isinstance(parent, str)):
            tooltip('Invalid entry no {} in "mirror all decks as filtered"-"parent deck name"'.format(idx))
            return
        resched = sl.get("reschedule based on answers")
        if not isinstance(resched, bool):
            tooltip('Invalid entry no {} in "mirror all decks as filtered"-"reschedule based on answers"'.format(idx))
            return            
        maxcards = sl.get("max cards", 9999)
        if not (maxcards and isinstance(maxcards, int)):
            maxcards = 9999
        steps = False # gc("steps")
        previewDelay = 0
            
        ## build
        for did in regDeckIds:
            odeck = mw.col.decks.get(did)
            name = parent.rstrip("::") + "::" + odeck['name']
            searchtext = 'deck:"{}"'.format(odeck['name']) + " " + additional
            CreateFilteredDeckWithoutGUI(name, searchtext, maxcards, order, resched, steps, previewDelay)
        mw.reset()
        mw.moveToState("deckBrowser")
        mw.progress.finish()


abf = QAction("Batch create filtered decks", mw)
abf.triggered.connect(batch_create_filtered_decks)
mw.form.menuTools.addAction(abf)
