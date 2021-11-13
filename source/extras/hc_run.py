import pyautogui as pag
import time


pag.alert('Ready VS Code Window')
pag.hotkey('ctrl', 'shift', 'p')
pag.typewrite('vcsb')
pag.press('enter')

pag.press('f5')
time.sleep(2)
pag.press(['1', 'enter', 'enter'])

for _ in range(2):
    pag.press('f5')
    time.sleep(1)
    pag.press('y')
    time.sleep(2)
    pag.press(['2', 'enter', 'enter'])
    pag.write('5050')
    pag.press('enter')
    time.sleep(0.2)


loc = pag.locateOnScreen('source/handcricket/debug/tt.png')
x0, y0 = loc.left+90, loc.top+45
t1y, t2y = y0+25, y0+50


dx, dy = 180, t2y+100

pag.moveTo(x0, t2y)
pag.dragTo(dx, dy, 0.3, button='left')

pag.moveTo(x0, t1y)
pag.dragTo(dx, dy, 0.3, button='left')
