#! /usr/bin/env python

from numpy.testing import TestCase, assert_equal, assert_almost_equal
from aubio import fvec, source
from numpy import array
from utils import list_all_sounds
from nose2.tools import params

list_of_sounds = list_all_sounds('sounds')
samplerates = [0, 44100, 8000, 32000]
hop_sizes = [512, 1024, 64]

path = None

all_params = []
for soundfile in list_of_sounds:
    for hop_size in hop_sizes:
        for samplerate in samplerates:
            all_params.append((hop_size, samplerate, soundfile))


class aubio_source_test_case_base(TestCase):

    def setUp(self):
        if not len(list_of_sounds): self.skipTest('add some sound files in \'python/tests/sounds\'')

class aubio_source_test_case(aubio_source_test_case_base):

    def test_close_file(self):
        samplerate = 0 # use native samplerate
        hop_size = 256
        for p in list_of_sounds:
            f = source(p, samplerate, hop_size)
            f.close()

    def test_close_file_twice(self):
        samplerate = 0 # use native samplerate
        hop_size = 256
        for p in list_of_sounds:
            f = source(p, samplerate, hop_size)
            f.close()
            f.close()

class aubio_source_read_test_case(aubio_source_test_case_base):

    def read_from_source(self, f):
        total_frames = 0
        while True:
            vec, read = f()
            total_frames += read
            if read < f.hop_size: break
        result_str = "read {:.2f}s ({:d} frames in {:d} blocks at {:d}Hz) from {:s}"
        result_params = total_frames / float(f.samplerate), total_frames, int(total_frames/f.hop_size), f.samplerate, f.uri
        print (result_str.format(*result_params))
        return total_frames

    @params(*all_params)
    def test_samplerate_hopsize(self, hop_size, samplerate, soundfile):
        try:
            f = source(soundfile, samplerate, hop_size)
        except RuntimeError as e:
            self.skipTest('failed opening with hop_s = {:d}, samplerate = {:d} ({:s})'.format(hop_size, samplerate, e))
        assert f.samplerate != 0
        self.read_from_source(f)

    @params(*list_of_sounds)
    def test_samplerate_none(self, p):
        f = source(p)
        assert f.samplerate != 0
        self.read_from_source(f)

    @params(*list_of_sounds)
    def test_samplerate_0(self, p):
        f = source(p, 0)
        assert f.samplerate != 0
        self.read_from_source(f)

    @params(*list_of_sounds)
    def test_wrong_samplerate(self, p):
        try:
            f = source(p, -1)
        except ValueError as e:
            pass
        else:
            self.fail('negative samplerate does not raise ValueError')

    @params(*list_of_sounds)
    def test_wrong_hop_size(self, p):
        try:
            f = source(p, 0, -1)
        except ValueError as e:
            pass
        else:
            self.fail('negative hop_size does not raise ValueError')

    @params(*list_of_sounds)
    def test_zero_hop_size(self, p):
        f = source(p, 0, 0)
        assert f.samplerate != 0
        assert f.hop_size != 0
        self.read_from_source(f)

    @params(*list_of_sounds)
    def test_seek_to_half(self, p):
        from random import randint
        f = source(p, 0, 0)
        assert f.samplerate != 0
        assert f.hop_size != 0
        a = self.read_from_source(f)
        c = randint(0, a)
        f.seek(c)
        b = self.read_from_source(f)
        assert a == b + c

    @params(*list_of_sounds)
    def test_duration(self, p):
        total_frames = 0
        f = source(p)
        duration = f.duration
        while True:
            vec, read = f()
            total_frames += read
            if read < f.hop_size: break
        self.assertEqual(duration, total_frames)

class aubio_source_readmulti_test_case(aubio_source_read_test_case):

    def read_from_source(self, f):
        total_frames = 0
        while True:
            vec, read = f.do_multi()
            total_frames += read
            if read < f.hop_size: break
        result_str = "read {:.2f}s ({:d} frames in {:d} channels and {:d} blocks at {:d}Hz) from {:s}"
        result_params = total_frames / float(f.samplerate), total_frames, f.channels, int(total_frames/f.hop_size), f.samplerate, f.uri
        print (result_str.format(*result_params))
        return total_frames

if __name__ == '__main__':
    from nose2 import main
    main()
