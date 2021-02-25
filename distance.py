import math


def lonlat_distance(a, b):

    degree_to_meters_factor = 111 * 1000  # 111 километров в метрах
    a_lon, a_lat = list(map(float, a))
    b_lon, b_lat = list(map(float, b))

    # Берем среднюю по широте точку и считаем коэффициент для нее.
    radians_lattitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_lattitude)

    # Вычисляем смещения в метрах по вертикали и горизонтали.
    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor

    # Вычисляем расстояние между точками.
    distance = math.sqrt(dx * dx + dy * dy)

    return round(distance)


def lonlat_coords(a, dx, dy):



    # degree_to_meters_factor = 111 * 1000
    # a_lon, a_lat = list(map(float, a))
    #
    # b_lat = abs(dy / degree_to_meters_factor - a_lat)
    #
    # # Берем среднюю по широте точку и считаем коэффициент для нее.
    # radians_lattitude = math.radians((a_lat + b_lat) / 2.)
    # lat_lon_factor = math.cos(radians_lattitude)
    #
    # b_lon = abs(dx / degree_to_meters_factor / lat_lon_factor - a_lon)

    return b_lon, b_lat


if __name__ == '__main__':
    print(lonlat_coords((50, 50), 500, 0))
    print(lonlat_distance((50, 50), (49.99299223501414, 50.0)))