def get_zeta_zeros_up_to_im(im_max):
    zeros = []
    n = 1
    while True:
        try:
            zero = mp.zetazero(n)
            im = float(mp.im(zero))
            if im <= im_max:
                zeros.append(im)
                n += 1
            else:
                break
        except:
            break
    return zeros