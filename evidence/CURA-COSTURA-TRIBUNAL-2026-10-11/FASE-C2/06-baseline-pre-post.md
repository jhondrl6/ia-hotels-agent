comando: grep -rE "^\s*def test_" tests --include=*.py | wc -l
PRE (medido en HEAD=cea999a, sin tocar arbol): 5309
POST (arbol de trabajo con la bateria nueva): 5321
delta: 12
