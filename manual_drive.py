from motion_controller import MotionController


motion_controller = MotionController()

while 1:
    try:
        key = input('enter command\n')
        print(key)
        if key == 'f':
            motion_controller.go_forward()
        elif key == 'r':
            motion_controller.turn_right()
        elif key == 'l':
            motion_controller.turn_left()
        elif key == 'v':
            motion_controller.turn_90()
        elif key == 'b':
            motion_controller.go_backward()
    except KeyboardInterrupt:
        motion_controller.close()
        exit(0)

