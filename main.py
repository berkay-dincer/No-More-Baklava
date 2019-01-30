import argparse
import subprocess
import time
from ctypes import CDLL
from FaceRecognizer import FaceRecognize


def idleTime():
    '''Return idle time in seconds'''

    # Get the output from
    # ioreg -c IOHIDSystem
    # /usr/sbin/ioreg -c IOHIDSystem | /usr/bin/awk '/HIDIdleTime/ {print int($NF/1000000000)}'
    io_stats = subprocess.Popen(["ioreg", "-c", "IOHIDSystem"], stdout=subprocess.PIPE)
    result = subprocess.Popen(["grep", "HIDIdleTime"], stdin=io_stats.stdout, stdout=subprocess.PIPE)

    io_stats.stdout.close()
    out, err = result.communicate()
    out = out.decode('utf-8')
    lines = out.split('\n')

    raw_line = ''
    for line in lines:
        if 'HIDIdleTime' in line:
            raw_line = line
            break

    nano_seconds = int(raw_line.split('=')[-1])
    seconds = nano_seconds / 10 ** 9
    return seconds


def lock_screen():
    CDLL('/System/Library/PrivateFrameworks/login.framework/Versions/Current/login').SACLockScreenImmediate()


def main(mode, image_count, name):
    recognizer = FaceRecognize()
    if mode == 'train':
        recognizer.capture_images(name=name, image_count=image_count)
        recognizer.train()
    else:
        while True:
            time.sleep(1)
            print("Baklava check...")
            if idleTime() > 10:
                print("Computer is idle we will not eat baklava today..")
                detected_face = recognizer.infer()[0]
                print(detected_face)
                if detected_face not in name:
                    lock_screen()
                recognizer.close_camera()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add some integers.')
    parser.add_argument('mode', type=str, help='mode of execution - train, no-more-baklava')
    parser.add_argument('count', type=int, default=10, help='number of pictures to take for training session.')
    parser.add_argument('name', type=str, help='name of the person in picture.')
    args = parser.parse_args()
    main(args.mode, args.count, args.name)
