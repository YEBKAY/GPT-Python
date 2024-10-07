from vpython import box, vector, rate

# Create a box object
my_box = box(pos=vector(0, 0, 0), size=vector(2, 2, 2), color=vector(1, 0, 0))

# Rotation parameters
rotation_speed = 0.05  # radians per frame

# Animation loop
while True:
    rate(60)  # Limit the loop to 60 iterations per second
    my_box.rotate(angle=rotation_speed, axis=vector(0, 1, 0))
