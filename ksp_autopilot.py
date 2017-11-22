import os
import time
import krpc
import math
import geopy
import pyttsx
import datetime
import csv
import winsound
from geopy.distance import VincentyDistance

# [ from geo_helper.py
abe_values = {
    'wgs84': [6378137.0, 6356752.3141, -1],
    'osgb': [6377563.396, 6356256.91, -1],
    'osie': [6377340.189, 6356034.447, -1]
}
earths_radius = (abe_values['wgs84'][0] + abe_values['wgs84'][1]) / 2.0



def calculate_distance_and_bearing(from_lat_dec, from_long_dec, to_lat_dec, to_long_dec):
    """Uses the spherical law of cosines to calculate the distance and bearing between two positions"""

    # Turn them all into radians
    from_theta = float(from_lat_dec) / 360.0 * 2.0 * math.pi
    from_landa = float(from_long_dec) / 360.0 * 2.0 * math.pi
    to_theta = float(to_lat_dec) / 360.0 * 2.0 * math.pi
    to_landa = float(to_long_dec) / 360.0 * 2.0 * math.pi

    d = math.acos(
            math.sin(from_theta) * math.sin(to_theta) +
            math.cos(from_theta) * math.cos(to_theta) * math.cos(to_landa-from_landa)
        ) * earths_radius

    bearing = math.atan2(
            math.sin(to_landa-from_landa) * math.cos(to_theta),
            math.cos(from_theta) * math.sin(to_theta) -
            math.sin(from_theta) * math.cos(to_theta) * math.cos(to_landa-from_landa)
        )
    bearing = bearing / 2.0 / math.pi * 360.0

    return d, bearing
# ]


def earth_rotation_speed(latitude):
    a = (2 * geocentric_radius(latitude) * math.pi * math.cos(math.radians(latitude))) / float(23.943372)
    return a/float(3600)


def geocentric_radius(latitude):
    a = float(6378137.0) 
    b = float(6356750.0)
    x1 = math.pow(math.pow(a, 2) * math.cos(math.radians(latitude)), 2)
    x2 = math.pow(math.pow(b, 2) * math.sin(math.radians(latitude)), 2)
    y1 = math.pow(a * math.cos(math.radians(latitude)), 2)
    y2 = math.pow(b * math.sin(math.radians(latitude)), 2)
    r = math.sqrt((x1+x2) / (y1+y2))
    return r


def dd_to_dms(dd):
    is_positive = dd >= 0
    dd = abs(dd)
    minutes, seconds = divmod(dd*3600, 60)
    degrees, minutes = divmod(minutes, 60)
    degrees = degrees if is_positive else -degrees
    return degrees, minutes, seconds


def dms_to_dd(d, m, s):
    dd = d + float(m)/60 + float(s)/3600
    return dd


def parse_gps(coords):
    a = coords.lower().split(', ')
    lat = a[0]
    lon = a[1]
    lat_neg = a[0].endswith('s')
    lon_neg = a[1].endswith('w')

    if "'" in coords: # sexagesimal
        lat_d = float(lat.split('\xb0')[0])
        lat_m = float(lat[lat.find('\xb0')+1:lat.find("'")])
        lat_s = lat[lat.find("'")+1:lat.find('.')]
        lat_x = lat[lat.find(".")+1:lat.find('"')]
        lat_s = float(lat_s + '.' + lat_x)
        lat = dms_to_dd(lat_d,lat_m,lat_s)

        lon_d = float(lon.split('\xb0')[0])
        lon_m = float(lon[lon.find('\xb0')+1:lon.find("'")])
        lon_s = lon[lon.find("'")+1:lon.find('.')]
        lon_x = lon[lon.find(".")+1:lon.find('"')]
        lon_s = float(lon_s + '.' + lon_x)
        lon = dms_to_dd(lon_d,lon_m,lon_s)
        
    else: # decimal
        if lat.find('\xb0')>=0: lat = float(lat[:lat.find('\xb0')])
        if lon.find('\xb0')>=0: lon = float(lon[:lon.find('\xb0')])

    if lat_neg: lat = lat*-1
    if lon_neg: lon = lon*-1
    return round(lat,6), round(lon,6)


def vincenty_distance(lat, lon, bear, dist):
    origin = geopy.Point(lat, lon)
    destination = VincentyDistance(meters=dist).destination(origin, bear)
    return destination


def cls():
    os.system("cls")


def cross_product(x, y):
    return (x[1]*y[2] - x[2]*y[1], x[2]*y[0] - x[0]*y[2], x[0]*y[1] - x[1]*y[0])


def dot_product(x, y):
    return x[0]*y[0] + x[1]*y[1] + x[2]*y[2]


def magnitude(x):
    return math.sqrt(x[0]**2 + x[1]**2 + x[2]**2)


def angle_between_vectors(x, y):
    """ Compute the angle between vector x and y """
    dp = dot_product(x, y)
    if dp == 0:
        return 0
    xm = magnitude(x)
    ym = magnitude(y)
    return math.acos(dp / (xm*ym)) * (180. / math.pi)


def angle_between_vector_and_plane(x, n):
    """ Compute the angle between a vector x and plane with normal vector n """
    dp = dot_product(x,n)
    if dp == 0:
        return 0
    xm = magnitude(x)
    nm = magnitude(n)
    return math.asin(dp / (xm*nm)) * (180. / math.pi)


def speak(something):
    global engine
    engine.say(something)
    engine.runAndWait()


def fdr_save():
    global fdata_alt
    global fdata_galt
    global fdata_lat
    global fdata_lon
    global fdata_gs
    global fdata_vs
    global fdata_mach
    global fdata_tas
    global fdata_eas
    global fdata_aoa
    global fdata_ssa
    global fdata_stall
    global fdata_pitch
    global fdata_hdg
    global fdata_roll
    global fdata_thr
    global fdata_thrav
    global fdata_fuel
    global fdata_ec


print 'Initiating'
engine = pyttsx.init()

tgt_heading = 0
tgt_roll = 0
tgt_alt = 8500
tgt_speed = 275
tgt_coordinates = (dms_to_dd(0, 0, 0),
                      dms_to_dd(0, 0, 0))

command_p = 4
command_r = tgt_roll
command_h = tgt_heading

conn = krpc.connect(name='Autopilot',
                    address = '127.0.0.1',
                    rpc_port = 50000,
                    stream_port = 50001)
vessel = conn.space_center.active_vessel
vessel.auto_pilot.rotation_speed_multiplier = 5
csvfile = open(str(datetime.datetime.now()).split('.')[0].replace(' ','_').replace(':','')+'.csv', 'wb')
fdrwrite = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)

fdata_alt = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
fdata_galt = conn.add_stream(getattr, vessel.flight(), 'surface_altitude')
fdata_lat = conn.add_stream(getattr, vessel.flight(), 'latitude')
fdata_lon = conn.add_stream(getattr, vessel.flight(), 'longitude')
fdata_mach = conn.add_stream(getattr, vessel.flight(), 'mach')
fdata_tas = conn.add_stream(getattr, vessel.flight(), 'true_air_speed')
fdata_eas = conn.add_stream(getattr, vessel.flight(), 'equivalent_air_speed')
fdata_aoa = conn.add_stream(getattr, vessel.flight(), 'angle_of_attack')
fdata_ssa = conn.add_stream(getattr, vessel.flight(), 'sideslip_angle')
fdata_stall = conn.add_stream(getattr, vessel.flight(), 'stall_fraction')
fdata_pitch = conn.add_stream(getattr, vessel.flight(), 'pitch')
fdata_hdg = conn.add_stream(getattr, vessel.flight(), 'heading')
fdata_roll = conn.add_stream(getattr, vessel.flight(), 'roll')

parts = vessel.parts.all
end = False
delay = float(0.2)
delayrate = float(1)/delay

vessel.auto_pilot.target_pitch_and_heading(fdata_pitch(), fdata_hdg())
vessel.auto_pilot.target_roll = fdata_roll()
vessel.auto_pilot.engage()
winsound.PlaySound('Autopilot disconnect.wav', winsound.SND_FILENAME)
speak('Autopilot engaged')

timers = [0, 0, 0, 0, 0, 0, 0, 0]

try:
    while not end:

        fc0 = fdata_fuel
        p0 = pitch
        h0 = heading
        r0 = roll

        pitch = fdata_pitch()
        yaw = fdata_hdg()
        roll = fdata_roll()
        alt = fdata_alt()
        altft = alt*float(3.28084)
        lat = fdata_lat()
        lon = fdata_lon()
        
        fdata_vs = vessel.flight(vessel.orbit.body.reference_frame).vertical_speed
        fdata_gs = vessel.flight(vessel.orbit.body.reference_frame).speed
        fdata_thr = vessel.thrust
        fdata_thrav = vessel.available_thrust
        fdata_fuel = vessel.resources.amount('LiquidFuel')
        fdata_ec = vessel.resources.amount('ElectricCharge')
        fdata_throt = vessel.control.throttle
        fdata_sas = vessel.auto_pilot.sas
        fdata_angles = (fdata_pitch()/float(90),
                        fdata_hdg()/float(360),
                        fdata_roll()/float(180))
        fdata_inputs = (vessel.control.pitch,
                       vessel.control.yaw,
                       vessel.control.roll)
        fdata_aptgt = (vessel.auto_pilot.target_pitch,
                      vessel.auto_pilot.target_heading,
                      vessel.auto_pilot.target_roll)
        fdata_aperr = (vessel.auto_pilot.pitch_error,
                      vessel.auto_pilot.heading_error,
                      vessel.auto_pilot.roll_error)

        pitchrate = (p0-pitch)*delayrate
        hdgrate = (h0-heading)*delayrate
        rollrate = (r0-roll)*delayrate
        fcons = (fc0-fdata_fuel)*delayrate
        tdir = vessel.auto_pilot.target_direction
        error = vessel.auto_pilot.error

        # vessel.auto_pilot.pitch_error
        # vessel.auto_pilot.heading_error
        # vessel.auto_pilot.roll_error
        alterror = tgt_alt - alt
        speederror = fdata_gs() - tgt_speed

        if (alt < (tgt_alt-100)) and (alt > (tgt_alt-7000)):
            command_p = 15
            pitchok = False
        elif alt < (tgt_alt-7000):
            command_p = 25
            pitchok = False
        elif alt > (tgt_alt+100):
            command_p = 5
            pitchok = False
        else:
            command_p = 7.5
            pitchok = True
        
        if heading < (tgt_heading-2):
            command_r = -5
            command_h = (tgt_heading+5)
            oncourse = False
            hdgok = False
        elif heading > (tgt_heading+2):
            command_r = 5
            command_h = (tgt_heading-5)
            oncourse = False
            hdgok = False
        else:
            command_r = 0
            command_h = tgt_heading
            oncourse = True
            hdgok = True
            
        if (roll < (tgt_roll-2)) and oncourse:
            command_r = tgt_roll+20
            rollok = False
        elif (roll > (tgt_roll+2)) and oncourse:
            command_r = tgt_roll-20
            rollok = False
        elif (roll < (tgt_roll-0.5)) and oncourse:
            command_r = tgt_roll+5
            rollok = False
        elif (roll > (tgt_roll+0.5)) and oncourse:
            command_r = tgt_roll-5
            rollok = False
        else:
            command_r = 0
            rollok = True

        if pitchok and hdgok and rollok and oncourse:
            flightmode = 'NOMINAL'
        else:
            flightmode = 'CORRECTION'
        
        vessel.auto_pilot.target_pitch_and_heading(command_p, command_h)
        vessel.auto_pilot.target_roll = command_r

        print ''
        print 'ALT\t\t', int(alt), 'M'
        print 'VERTSPEED\t', fdata_vs(), 'M/S'
        print ''
        print 'PITCH\t\t', pitch
        print 'ROLL\t\t', roll
        print 'HEADING\t\t', heading
        print ''
        print 'MODE\t\t', flightmode
        print 'ONCOURSE\t', oncourse
        print 'DIRERROR\t', error
        print ''
        print 'AP-PITCH', command_p
        print 'AP-HDNG', command_h
        print 'AP-ROLL', command_r
        print ''
        print 'PITCHRATE\t', pitchrate, 'DEG/S'
        print 'YAWRATE\t\t', hdgrate, 'DEG/S'
        print 'ROLLRATE\t', rollrate, 'DEG/S'

        fdrwrite.writerow([fdata_alt(),
                  fdata_galt(),
                  fdata_lat(),
                  fdata_lon(),
                  fdata_gs,
                  fdata_vs,
                  fdata_mach(),
                  fdata_tas(),
                  fdata_eas(),
                  fdata_aoa(),
                  fdata_ssa(),
                  fdata_stall(),
                  fdata_pitch(),
                  fdata_hdg(),
                  fdata_roll(),
                  fdata_thr,
                  fdata_thrav,
                  fdata_fuel,
                  fdata_ec,
                  fdata_throt,
                  fdata_sas,
                  fdata_angles,
                  fdata_inputs,
                  fdata_aptgt,
                  fdata_aperr])
        
        time.sleep(delay)
        cls()

except IOError:
    vessel.auto_pilot.disengage()
    end = True

