sm_size = [22.5, 23, 23.5, 24,   24.5,   25,   25.5, 26,   26.5, 27, 27.5, 28, 28.5, 29, 29.5, 30.5, 31]
ru_size = [35,   36, 37,   38,   38.5,   39,   40,   40.5, 41,   42, 43, 43.5, 44, 45, 46, 47, 48]
eu_size = [35.5, 36.5, 37, 38, 38.5, 39.5, 40, 41, 41.5, 42.5, 43, 44, 45.5, 45.5, 46, 47.5, 48.5]
uk_size = [3.5, 4, 4.5, 5.5, 6, 6.5, 7, 7.5, 8.5, 9, 9.5, 10, 10.5, 11, 12, 13, 13.5]
us_size = [5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9.5, 10, 10.5, 11, 11.5, 12, 13, 14, 14.5]

sizes = {"sm": sm_size, "ru": ru_size, "eu": eu_size, "uk": uk_size, "us": us_size}

def sm_to_size(size_type, size_sm):
    sm_ind = sizes["sm"].index(size_sm)
    return sizes[size_type][sm_ind]

def size_to_sm(size_type, size):
    size_ind = sizes[size_type].index(size)
    return sizes["sm"][size_ind]

def convert(size_from, size_to, size):
    sm_size = size_to_sm(size_from, size)
    return sm_to_size(size_to, sm_size)
