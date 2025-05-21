import turtle
import colorsys

# Set up the screen
t = turtle.Turtle()
s = turtle.Screen()
s.bgcolor("black")
t.speed(0)
turtle.colormode(255)

# Set up colors
h = 0  # hue
n = 36  # number of spirals

for i in range(360):
    c = colorsys.hsv_to_rgb(h, 1, 1)
    r, g, b = int(c[0]*255), int(c[1]*255), int(c[2]*255)
    t.pencolor(r, g, b)
    t.forward(i * 3 / n + i)
    t.left(59)
    t.circle(i * 0.1, 60)
    h += 0.005

t.hideturtle()
turtle.done()
