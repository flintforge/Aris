'''
ARIS
Author:  𝓟𝓱𝓲𝓵.𝓔𝓼𝓽𝓲𝓿𝓪𝓵  @ 𝓕𝓻𝓮𝓮.𝓯𝓻
Date:<2018-05-18 15:52:50>
Released under the MIT License
'''
class DictMixins(object):
    ''' set a dictionnary as object attributes '''

    def __init__(other, dico, values=False):

        if values :
            for k,v in dico.items():
                setattr(other,k,v)
        else:
            for k in dico.keys():
                setattr(other,k,object())

            #other.__dict__[k] = object()


# test
if __name__ == '__main__':

    class MixedwithDic(DictMixins):
        def __init__(self, loadvalues=False):
            dico = {
                'attr1': 'x',
                'attr2': 1
            }
            DictMixins.__init__(self, dico, loadvalues)


    a = MixedwithDic()
    print(a.attr1, a.__dict__)
    a = MixedwithDic(True)
    print(a.attr1, a.__dict__)
    assert(a.attr1 is 'x')
    assert(a.attr2 is 1)
