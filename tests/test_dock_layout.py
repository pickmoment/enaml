# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import os
import pytest
from utils import is_qt_available

pytestmark = pytest.mark.skipif(not is_qt_available(),
                                reason='Requires a Qt binding')

from enaml.layout.api import HSplitLayout, DockLayoutWarning
from enaml.widgets.api import DockArea, DockItem

from utils import compile_source, wait_for_window_displayed

DOCK_AREA_TEMPLATE =\
"""from enaml.widgets.api import Window, Container, DockArea, DockItem
from enaml.layout.api import VSplitLayout

enamldef Main(Window):

    alias area: dock_area

    Container:
        DockArea: dock_area:
            layout = VSplitLayout('item1', 'item2')

            DockItem:
                name = 'item1'
            DockItem:
                name = 'item2'

"""


@pytest.mark.filterwarnings('error')
def test_validation_dock_layout1(enaml_qtbot, enaml_sleep):
    """Test that the validation of a layout.

    We check in particular that the proper warnings are raised and that doing
    so does not corrupt the globals.

    """
    win = compile_source(DOCK_AREA_TEMPLATE, 'Main')()
    win.show()
    wait_for_window_displayed(enaml_qtbot, win)
    enaml_qtbot.wait(enaml_sleep)
    win.area.layout = HSplitLayout('item1', 'item2')
    enaml_qtbot.wait(enaml_sleep)


def test_validation_dock_layout2(enaml_qtbot, enaml_sleep):
    """Test that the validation of a layout.

    We check in particular that the proper warnings are raised and that doing
    so does not corrupt the globals.

    """
    win = compile_source(DOCK_AREA_TEMPLATE, 'Main')()
    win.show()
    wait_for_window_displayed(enaml_qtbot, win)
    enaml_qtbot.wait(enaml_sleep)
    glob = globals().copy()
    with pytest.warns(DockLayoutWarning):
        win.area.layout = HSplitLayout('item1', 'item2', 'item3')
    assert globals() == glob
    enaml_qtbot.wait(enaml_sleep)
    
    
def test_dock_area_interactions(enaml_qtbot, enaml_sleep):
    """Test interations with the dock area.

    """
    # Since timers are used the sleep must be greater than the default
    enaml_sleep = max(300, enaml_sleep)
    from enaml.qt.QtCore import Qt, QPoint
    from enaml.qt.QtWidgets import QWidget
    from enaml.layout.api import FloatItem, InsertTab
    with open(os.path.join('examples', 'widgets', 'dock_area.enaml')) as f:
        source = f.read()
    
    win = compile_source(source, 'Main')()
    win.show()
    
    wait_for_window_displayed(enaml_qtbot, win)
    enaml_qtbot.wait(enaml_sleep)
    _children = win.children[0].children
    btn_save, btn_restore, btn_add, cmb_styles, cbx_evts, dock = _children
        
    # Enable dock events
    enaml_qtbot.mouseClick(cbx_evts.proxy.widget, Qt.LeftButton)
    enaml_qtbot.wait(enaml_sleep)
    
    with pytest.warns(DockLayoutWarning):
        # Change styles
        cmb_styles.proxy.widget.setFocus()
        enaml_qtbot.keyClick(cmb_styles.proxy.widget, Qt.Key_Up)
        
        # Save layout
        enaml_qtbot.mouseClick(btn_save.proxy.widget, Qt.LeftButton)
        enaml_qtbot.wait(enaml_sleep)
        
        # Toggle closable
        di = dock.find('item_2')
        di.closable = False
        enaml_qtbot.wait(enaml_sleep)
        di.closable = True
        
        # Check alert
        di.alert('info')
        
        # Maximize it
        tb = di.proxy.widget.titleBarWidget()
        enaml_qtbot.mouseClick(tb._max_button, Qt.LeftButton)
        enaml_qtbot.wait(enaml_sleep)
        
        # Minimize it
        enaml_qtbot.mouseClick(tb._restore_button, Qt.LeftButton)
        enaml_qtbot.wait(enaml_sleep)
    
        # Pin it
        enaml_qtbot.mouseClick(tb._pin_button, Qt.LeftButton)
        enaml_qtbot.wait(enaml_sleep)
        
        # TODO: Open and close it using clicks
        dock_area = dock.proxy.widget
        for c in dock_area.dockBarContainers():
            dock_bar = c[0]
            dock_area.extendFromDockBar(dock_bar)
            enaml_qtbot.wait(enaml_sleep)
            dock_area.retractToDockBar(dock_bar)
            enaml_qtbot.wait(enaml_sleep)
        
        # Unpin
        enaml_qtbot.mouseClick(tb._pin_button, Qt.LeftButton)
        enaml_qtbot.wait(enaml_sleep)
        
        # Note the location of the dock item title
        title = tb._title_label
        ref = win.proxy.widget
        
        # Maximize and minimize it by double clicking
        pos = title.mapTo(tb, title.pos())
        enaml_qtbot.mouseDClick(tb, Qt.LeftButton, pos=pos)
        enaml_qtbot.wait(enaml_sleep)
        enaml_qtbot.mouseDClick(tb, Qt.LeftButton, pos=pos)
        enaml_qtbot.wait(enaml_sleep)
        
        # Float it
        op = FloatItem(item=di.name)
        dock.update_layout(op)
        enaml_qtbot.wait(enaml_sleep)
        
        # Link it
        enaml_qtbot.mouseClick(tb._link_button, Qt.LeftButton)
        enaml_qtbot.wait(enaml_sleep)
        
        # Unlink it
        enaml_qtbot.mouseClick(tb._link_button, Qt.LeftButton)
        enaml_qtbot.wait(enaml_sleep)
        
        # Restore it
        op = InsertTab(item=di.name, target='item_1')
        dock.update_layout(op)
        enaml_qtbot.wait(enaml_sleep)
        
        # TODO: Drag it around
        
        # Add items
        enaml_qtbot.mouseClick(btn_add.proxy.widget, Qt.LeftButton)
        enaml_qtbot.wait(enaml_sleep)
        
        # Close all added items
        for i in range(10, 15):
            di = dock.find('item_%i'%i)
            if di:
                enaml_qtbot.mouseClick(
                    di.proxy.widget.titleBarWidget()._close_button, 
                    Qt.LeftButton)
        
        # Restore layout
        enaml_qtbot.mouseClick(btn_restore.proxy.widget, Qt.LeftButton)
        enaml_qtbot.wait(enaml_sleep)
    
    enaml_qtbot.wait(enaml_sleep)
