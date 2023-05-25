import h5py

def list_attr(obj):
    [print(i) for i in obj.attrs]
    return list(obj.attrs)

filename = "/Users/jsencak/Documents/running_2023-04-17T122413+0100.h5"
with h5py.File(filename, 'r+') as f:
    # get path from .h5 file
    print(f["Acquisition"].attrs.items())
    print("GLobal file attributes", f.attrs.items())
    print()
    print("Acquisition")
    for i in f["Acquisition"].attrs.items():
        print(i)
    print()
    
    print("/Acquisition/Raw[0]/")
    for i in f["/Acquisition/Raw[0]"].items():
        print(i)
    for i in f["/Acquisition/Raw[0]"].attrs.items():
        print(i)
    
    print("/Acquisition/Raw[0]/RawData")

    for i in f["/Acquisition/Raw[0]/RawData"].attrs.items():
        print(i)
    
    print()
    acquisition_attrs = list_attr(f["Acquisition"])
    print()
    for i in f['Acquisition'].items():
        print(i)
    for i in f['Acquisition'].values():
        print(i)
    for i in f["/Acquisition/Raw[0]"].items():
        print(i)
    print("VALUES",f["/Acquisition/Raw[0]"].values())
    for i in f["/Acquisition/Raw[0]"].values():
        print(i)
    for i in f["/Acquisition/Raw[0]"].attrs:
        print("Attributes: ", i)
    print(f.get("/Acquisition/Raw[0]NumberO"))
    print(f["/Acquisition/Raw[0]/RawData"])
