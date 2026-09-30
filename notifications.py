# -------------------------
# Notification Manager
# -------------------------

_speak_function = None


def set_speak_function(function):
    global _speak_function
    _speak_function = function


def notify(message):

    print(f"\n🔔 {message}")

    if _speak_function is not None:
        _speak_function(message)
