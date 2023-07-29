import taichi as ti
import taichi.math as tm


WIDTH, HEIGHT = 1600, 850
AGENTS_NUM = 100000
MOVE_SPEED = 1
EVAPORATE_SPEED = 0.002
DEFUSE_SPEED = 0.5
SENSOR_SIZE = 3
SENSOR_OFFSET_DST = 10
SENSOR_ANGLE_SPACING = 1
TURN_SPEED = tm.pi / 2
RADIUS = 100

ti.init(ti.cpu)

trailMap = ti.Vector.field(3, dtype=float, shape=(WIDTH, HEIGHT))
agents = ti.Struct.field({
    'angle': float,
    'position': tm.vec2
}, shape=(AGENTS_NUM,))


@ti.kernel
def setup():
    for x in agents:
        x1 = RADIUS * ti.random() * tm.cos(float(x))
        y1 = RADIUS * ti.random() * tm.sin(float(x))
        agents[x].angle = x - tm.pi
        agents[x].position = (WIDTH / 2 + x1, HEIGHT / 2 + y1)


gui = ti.GUI("Slime simulation", (WIDTH, HEIGHT))


@ti.func
def lerp(x, y, a):
    return x * (1 - a) + y * a


@ti.func
def RGB2Grayscale(rgb):
    return 0.299 * rgb.x + 0.587 * rgb.y + 0.114 * rgb.z


@ti.kernel
def proceedTrailMap():
    for x, y in trailMap:
        if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
            continue

        orignalValue = trailMap[x, y]
        summ = tm.vec3(0, 0, 0)
        for i in range(-1, 2):
            for j in range(-1, 2):
                sampleX = x + i
                sampleY = y + j

                if sampleX >= 0 and sampleX < WIDTH and sampleY >= 0 and sampleY < HEIGHT:
                    summ += trailMap[x + i, y + j]

        blurValue = summ / 9
        diffusedValue = lerp(orignalValue, blurValue, DEFUSE_SPEED)
        difusedAndEvaporatedValue = ti.max(
            0, diffusedValue - EVAPORATE_SPEED)

        trailMap[x, y] = difusedAndEvaporatedValue


@ti.func
def sense(agent, sensorAngleOffset):
    sensorAngle = agent.angle + sensorAngleOffset
    sensorDir = tm.vec2(tm.cos(sensorAngle), tm.sin(sensorAngle))
    sensorCentre = agent.position + sensorDir * SENSOR_OFFSET_DST
    summ = 0

    for offsetX in range(-SENSOR_SIZE, SENSOR_SIZE + 1):
        for offsetY in range(-SENSOR_SIZE, SENSOR_SIZE + 1):
            pos = sensorCentre + tm.vec2(offsetX, offsetY)
            if pos.x >= 0 and pos.x < WIDTH and pos.y >= 0 and pos.y < HEIGHT:
                summ += RGB2Grayscale(trailMap[int(pos.x), int(pos.y)])
    return summ


@ ti.kernel
def update():
    for x in agents:
        random = ti.random()

        weightForward = sense(agents[x], 0)
        weightRight = sense(agents[x], -SENSOR_ANGLE_SPACING)
        weightLeft = sense(agents[x], SENSOR_ANGLE_SPACING)

        randomSteerStrengh = random

        if weightForward > weightLeft and weightForward > weightRight:
            agents[x].angle += 0
        elif weightForward < weightLeft and weightForward < weightRight:
            agents[x].angle += (randomSteerStrengh - 0.5) * 2 * TURN_SPEED
        elif weightRight > weightLeft:
            agents[x].angle -= randomSteerStrengh * TURN_SPEED
        elif weightLeft > weightRight:
            agents[x].angle += randomSteerStrengh * TURN_SPEED
        direction = tm.vec2(tm.cos(agents[x].angle), tm.sin(agents[x].angle))
        newPos = agents[x].position + direction * MOVE_SPEED

        if newPos.x < 0 or newPos.x >= WIDTH or newPos.y < 0 or newPos.y >= HEIGHT:
            newPos.x = ti.min(WIDTH - 0.01, ti.max(0, newPos.x))
            newPos.y = ti.min(HEIGHT - 0.01, ti.max(0, newPos.y))
            agents[x].angle = random * tm.pi * 2
        agents[x].position = newPos
        trailMap[int(newPos.x), int(newPos.y)] = [1, 1, 1]


setup()

while gui.running:
    update()
    proceedTrailMap()

    gui.set_image(trailMap)
    gui.show()
