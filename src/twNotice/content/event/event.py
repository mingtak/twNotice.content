# -*- coding: utf-8 -*-

def moveContentToTop(item, event):
    """ Moves Item to the top of its folder """
    folder = item.getParentNode()
    if hasattr(folder, 'moveObjectsToTop'):
        folder.moveObjectsToTop(item.id)
