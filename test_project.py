from project import get_name
from project import get_email
from project import voice_to_text
from pytest import MonkeyPatch
import pytest
def test_valid_name():
    with MonkeyPatch.context() as m:
        m.setattr('builtins.input', lambda _: 'John')
        assert get_name() == 'John'

def test_empty_name():
    # Test when an empty name is provided
    with MonkeyPatch.context() as m:
        m.setattr('builtins.input', lambda _: '')
        with pytest.raises(ValueError):
            get_name()

def test_invalid_name():
    # Test when a non-alphabetic name is provided
    with MonkeyPatch.context() as m:
        m.setattr('builtins.input', lambda _: '123')
        with pytest.raises(ValueError):
            get_name()
            
            
            
def test_valid_email():
    # Test when a valid email is provided
    with MonkeyPatch.context() as m:
        m.setattr('builtins.input', lambda _: 'john@example.com')
        assert get_email() == 'john@example.com'
        
@pytest.mark.filterwarnings("ignore:distutils:DeprecationWarning")       
def test_voice_to_text():
    class MockRecognizer:
        def listen(self, source, timeout):
            return "dummy audio"

        def recognize_google(self, audio):
            return "dummy text"

    result = voice_to_text(prompt="Speak something:", recognizer=MockRecognizer())

    assert result == "dummy text"