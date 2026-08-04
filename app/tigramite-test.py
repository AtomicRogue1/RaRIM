import msvcrt
import time

running = True

while running:
    print("Loop running...")

    # Check if a key was pressed
    if msvcrt.kbhit():
        key = msvcrt.getch()
        print("Force stopping article collection...")
        break

    time.sleep(1)

print("Loop ended")