from time import sleep
from servo_control import (
    arm_home, pick_object, lift_object,
    place_left_light, place_left_heavy,
    place_right_light, place_right_heavy,
    cleanup as servo_cleanup
)
from camera_vision import detect_shape, cleanup as camera_cleanup
from weight_sensor import get_weight, set_zero, cleanup as weight_cleanup

try:
    # Set arm to home
    arm_home()

    # Set empty platform as zero
    set_zero()

    while True:
        # Step 1: Detect object shape
        shape = detect_shape()
        if shape == "No Object":
            continue

        print("Object detected:", shape)
        weight = get_weight()
        print("Measured weight:", round(weight, 2), "g")
        sleep(10)
        # Step 2: Pick the object
        pick_object()
        lift_object()

        # Step 3: Place object on load cell
        # (Your arm motion should already place it there)
           # VERY IMPORTANT: allow weight to settle

        # Step 5: Decision logic
        if shape == "Circle" and weight <= 20:
            place_left_light()

        elif shape == "Circle" and weight > 20:
            place_left_heavy()

        elif shape == "Rectangle" and weight <= 20:
            place_right_light()

        else:
            place_right_heavy()

        # Step 6: Return to home position
        arm_home()
        sleep(1)

except KeyboardInterrupt:
    pass

finally:
    servo_cleanup()
    camera_cleanup()
    weight_cleanup()
