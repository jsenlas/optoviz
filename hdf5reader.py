import h5py

#h5py.run_tests()
PATH = './data/das-merania/sweep_p1intensity_2021-08-31T17_22_39+0100/'
FILENAME = 'sweep_p1intensity_2021-08-31T162239Z.h5'

f = h5py.File(f'{PATH}{FILENAME}', 'r', driver=None)
print(f.__dict__)
print(f.name)
print(f.filename)
if f:
    print("file is open")
else:
    print("file is closed")


print(f.attrs.__dict__)


print("closing file...")
f.close()

if f:
    print("file is open")
else:
    print("file is closed")
