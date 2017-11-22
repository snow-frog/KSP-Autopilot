import os
import time
import krpc
import datetime
import csv


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


print 'Initiating Black Box'
conn = krpc.connect(name='Flight Data Recorder',
                    address='127.0.0.1',
                    rpc_port=50000,
                    stream_port=50001)
csvfile = open(str(datetime.datetime.now()).split('.')[0].replace(' ','_').replace(':','')+'.csv', 'wb')
fdrwrite = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)

vessel = conn.space_center.active_vessel
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
fdrwrite.writerow(['alt','galt','lat','lon','gs','vs','mach','tas','eas','aoa','sideslip',
                   'stall','pitch','hdg','roll','thrust','thrustavail','fuel','ec','throt',
                   'sas','angles(pyr)','controlinputs(p,y,r)','autoptargets(p,hdg,r)',
                   'autoperror(p,hdg,r)'])
end = False
delay = float(1)
print 'Recording'
try:
    while not end:
        
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
except:
    print 'Recording stopped'
    end = True

csvfile.close()
