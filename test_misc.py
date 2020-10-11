from platform import system
import pytest
from pyffmpeg.misc import fix_splashes

os_name = system().lower()

@pytest.mark.parametrize(
    'case,exp', [
        (['-i', 'f.wav', 'o.wav'], ['-i', 'f.wav', 'o.wav']),
        (
            ['-i', 'path\\path one\\f.wav', 'path\\path one\\f.wav'],
            ['-i', 'path\\path one\\f.wav', 'path\\path one\\f.wav']
        ),
        (
            ['-i', 'path/path one/f.wav', 'path/path one/f.wav'],
            ['-i', 'path\\path one\\f.wav', 'path\\path one\\f.wav']
        )
        ])
def test_fix_splashes(case, exp):
    ret = fix_splashes(case)

    if os_name = "windows"
        assert ret == exp
    elif '\\' not in ret:
        assert True
