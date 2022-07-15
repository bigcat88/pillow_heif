from PIL import Image, ImageMath


def assert_image_equal(a, b):
    assert a.mode == b.mode
    assert a.size == b.size
    assert a.tobytes() == b.tobytes()


def convert_to_comparable(a, b):
    new_a, new_b = a, b
    if a.mode == "P":
        new_a = Image.new("L", a.size)
        new_b = Image.new("L", b.size)
        new_a.putdata(a.getdata())
        new_b.putdata(b.getdata())
    elif a.mode == "I;16":
        new_a = a.convert("I")
        new_b = b.convert("I")
    return new_a, new_b


def assert_image_similar(a, b, epsilon=0):
    assert a.mode == b.mode
    assert a.size == b.size
    a, b = convert_to_comparable(a, b)
    diff = 0
    for ach, bch in zip(a.split(), b.split()):
        ch_diff = ImageMath.eval("abs(a - b)", a=ach, b=bch).convert("L")
        diff += sum(i * num for i, num in enumerate(ch_diff.histogram()))
    ave_diff = diff / (a.size[0] * a.size[1])
    assert epsilon >= ave_diff
