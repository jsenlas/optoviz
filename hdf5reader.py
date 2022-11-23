import h5py
import re
#h5py.run_tests()
PATH = './data/das-merania/sweep_p1intensity_2021-08-31T17_22_39+0100/'
FILENAME = 'sweep_p1intensity_2021-08-31T162239Z.h5'

# with h5py.File(f'{PATH}{FILENAME}', 'r', driver=None) as f:
f = h5py.File(f'{PATH}{FILENAME}', 'r', driver=None)
print(f.__dict__)
print(f.name)
print(f.filename)
if f:
    print("file is open")
else:
    print("file is closed")

dataset = f.get('/Acquisition/Raw[0]/RawData')
# def get_keys():
# f.keys()  # prints keys
# if match := re.match("^.+'(.+)'.+", str(f.keys())):
#     print(match[1]) # 0 whole string 1 just the match group
#     print(f[match[1]])

