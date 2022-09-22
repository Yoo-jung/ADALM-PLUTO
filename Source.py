#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Broadcast FM
# Author: moon
# Description: Broadcast FM rcvr
# GNU Radio version: 3.8.1.0

from distutils.version import StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

from PyQt5 import Qt
from PyQt5.QtCore import QObject, pyqtSlot
from gnuradio import analog
from gnuradio import audio
from gnuradio import blocks
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio.qtgui import Range, RangeWidget
import iio
from gnuradio import qtgui

class Source(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Broadcast FM")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Broadcast FM")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "Source")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Variables
        ##################################################
        self.volume = volume = 0.3
        self.tuning = tuning = 103500000
        self.samp_rate = samp_rate = 1920000
        self.rf_decim = rf_decim = 5
        self.interp = interp = 1
        self.deviation = deviation = 75000
        self.audio_decim = audio_decim = 8

        ##################################################
        # Blocks
        ##################################################
        self._volume_range = Range(0, 1, 0.05, 0.3, 200)
        self._volume_win = RangeWidget(self._volume_range, self.set_volume, 'Volume', "counter_slider", float)
        self.top_grid_layout.addWidget(self._volume_win)
        # Create the options list
        self._tuning_options = (103500000, 93900000, 97300000, 107700000, )
        # Create the labels list
        self._tuning_labels = ('SBS', 'CBS', 'KBS', 'SBSPFM', )
        # Create the combo box
        self._tuning_tool_bar = Qt.QToolBar(self)
        self._tuning_tool_bar.addWidget(Qt.QLabel('Station' + ": "))
        self._tuning_combo_box = Qt.QComboBox()
        self._tuning_tool_bar.addWidget(self._tuning_combo_box)
        for _label in self._tuning_labels: self._tuning_combo_box.addItem(_label)
        self._tuning_callback = lambda i: Qt.QMetaObject.invokeMethod(self._tuning_combo_box, "setCurrentIndex", Qt.Q_ARG("int", self._tuning_options.index(i)))
        self._tuning_callback(self.tuning)
        self._tuning_combo_box.currentIndexChanged.connect(
            lambda i: self.set_tuning(self._tuning_options[i]))
        # Create the radio buttons
        self.top_grid_layout.addWidget(self._tuning_tool_bar)
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=1,
                decimation=5,
                taps=None,
                fractional_bw=None)
        self.iio_pluto_source_0 = iio.pluto_source('ip:192.168.2.1', tuning, 1920000, 500000, 16384, True, True, True, 'fast_attack', 64, '', True)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_ff(volume)
        self.audio_sink_0 = audio.sink(48000, 'pulse', True)
        self.analog_fm_demod_cf_0 = analog.fm_demod_cf(
        	channel_rate=384000,
        	audio_decim=8,
        	deviation=75000,
        	audio_pass=16000,
        	audio_stop=20000,
        	gain=1,
        	tau=0.000075,
        )



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_fm_demod_cf_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.audio_sink_0, 0))
        self.connect((self.iio_pluto_source_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.analog_fm_demod_cf_0, 0))

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "Source")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_volume(self):
        return self.volume

    def set_volume(self, volume):
        self.volume = volume
        self.blocks_multiply_const_vxx_0.set_k(self.volume)

    def get_tuning(self):
        return self.tuning

    def set_tuning(self, tuning):
        self.tuning = tuning
        self._tuning_callback(self.tuning)
        self.iio_pluto_source_0.set_params(self.tuning, 1920000, 500000, True, True, True, 'fast_attack', 64, '', True)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate

    def get_rf_decim(self):
        return self.rf_decim

    def set_rf_decim(self, rf_decim):
        self.rf_decim = rf_decim

    def get_interp(self):
        return self.interp

    def set_interp(self, interp):
        self.interp = interp

    def get_deviation(self):
        return self.deviation

    def set_deviation(self, deviation):
        self.deviation = deviation

    def get_audio_decim(self):
        return self.audio_decim

    def set_audio_decim(self, audio_decim):
        self.audio_decim = audio_decim



def main(top_block_cls=Source, options=None):

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()
    tb.start()
    tb.show()

    def sig_handler(sig=None, frame=None):
        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    def quitting():
        tb.stop()
        tb.wait()
    qapp.aboutToQuit.connect(quitting)
    qapp.exec_()


if __name__ == '__main__':
    main()
