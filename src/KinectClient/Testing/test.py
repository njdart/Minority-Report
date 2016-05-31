x = 720
y = 800

ratioX = 686 / 512
ratioY = 567 / 424
offsetX = 137
offsetY = -19

xf = x * ratioX + offsetX
yf = y * ratioY + offsetY

print("({}, {})".format(xf, yf))