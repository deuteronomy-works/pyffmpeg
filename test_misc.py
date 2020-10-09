import pytest
from pyffmpeg.misc import fix_splashes

@pytest.mark.parametrize('case,exp',
[
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

    assert ret == exp
