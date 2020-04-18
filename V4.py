##Authors: Kai Zhang; Christophe Duwig.
##Contact: Kai.Zhang.1@city.ac.uk; duwig@mech.kth.se

def Equilibrium(data_name, specifier, mech, T_inlet, P_inlet,func_):

    fuel_list, ER, original_data, fuel_data = call_data_reader(specifier, data_name)
    gas = ct.Solution(mech)
    species_names = [i + '_b' for i in gas.species_names]
    x, tad, co, nox, no_no2, no, no2  = list_creator(func_)
    for i in range(len(fuel_list)):
        gas.TP  = float(T_inlet), float(P_inlet)
        gas.set_equivalence_ratio(ER[i], fuel_list[i] , 'O2:0.21, N2:0.79')
        gas.equilibrate('HP')
        x.append(gas.X)
        tad.append(gas.T)
        CO_ppmvd,NOx_ppmvd,NO_NO2_ppmvd, NO_ppmvd, NO2_ppmvd = X_ppmvd(gas, gas)
        co.append(CO_ppmvd)
        nox.append(NOx_ppmvd)
        no_no2.append(NO_NO2_ppmvd)
        no.append(NO_ppmvd)   
        no2.append(NO2_ppmvd) 

    csv_file   = "Equilibrium.csv"   
    excel_file = "Equilibrium.xlsx"
    header     = list(original_data.columns.values) + ["T_b (K)"] + ["CO_ppmvd"] + ["NO_ppmvd"] + ["NO2_ppmvd"] + ["NOx_ppmvd"] + ["NO/NO2_ppmvd"] + species_names
    solution   = [list(original_data.values[i]) + [tad[i]] + [co[i]] + [no[i]] + [no2[i]] + [nox[i]] + [no_no2[i]] + list(x[i]) for i in range(len(original_data))]
    write(original_data, csv_file, excel_file, header, solution)

def General(data_name, specifier, mech, T_inlet, P_inlet,func_):

    fuel_list, ER, original_data, fuel_data = call_data_reader(specifier, data_name)
    df_LHV_mixture = get_LHV_mixture(original_data, fuel_data)
    df_LHV_mixture.to_csv("General.csv", index = False)
    if input('csv output done! Convert to excel? [yes/no)] ') == 'yes':
        df_LHV_mixture.to_excel("General.xlsx", index = False)
        print ('xlsx output done!')
    else:
        print ('csv output done!')

def get_flame_speed(data_name, specifier, mech, T_inlet, P_inlet, func_):

    fuel_list, ER, original_data, fuel_data = call_data_reader(specifier, data_name)
    # setup parameters

    Lx=0.02
    tol_ss      = [1.0e-6, 1.0e-14]        # [rtol atol] for steady-state problem
    tol_ts      = [1.0e-5, 1.0e-13]        # [rtol atol] for time stepping
    loglevel    = 0                        # amount of diagnostic output (0
    refine_grid = True                     # True to enable refinement
    ###############################
    gas = ct.Solution(mech)
    species_names = [i + '_b' for i in gas.species_names]
    x, temp, delta, SL, co, nox, no_no2, no, no2 = list_creator(func_)
    os.system('mkdir flame')

    for i in range(len(fuel_list)):
        print ("Doing calculation for data {}.".format(i+1))
        gas.TP  = float(T_inlet), float(P_inlet)
        gas.set_equivalence_ratio(ER[i], fuel_list[i] , 'O2:0.21, N2:0.79')
        f = ct.FreeFlame(gas, width=Lx)
        f.transport_model = 'Multi'
        f.soret_enabled=True

        f.flame.set_steady_tolerances(default=tol_ss)
        f.flame.set_transient_tolerances(default=tol_ts)
        f.set_refine_criteria(ratio=3, slope=0.01, curve=0.01)

        f.solve(loglevel=loglevel, refine_grid=refine_grid, auto=True)
        idx_OH = get_flame_front_index(gas, f)
        print ("Flame front sits at position {}, evaluated with max OH".format(idx_OH))

        x.append([f.X[gas.species_index(species)][idx_OH] for species in gas.species_names])
        temp.append(f.T[-1])
        delta.append(get_thermal_thickness(f))
        SL.append(f.u[0])
        CO_ppmvd,NOx_ppmvd,NO_NO2_ppmvd, NO_ppmvd, NO2_ppmvd = X_ppmvd(f, gas)
        co.append(CO_ppmvd)
        nox.append(NOx_ppmvd)
        no_no2.append(NO_NO2_ppmvd)
        no.append(NO_ppmvd)   
        no2.append(NO2_ppmvd) 

        f.write_csv('./flame/flame{}.csv'.format(i+1), species='X')

    csv_file   = "1D_flame.csv"   
    excel_file = "1D_flame.xlsx"
    header     = list(original_data.columns.values) + ["T_b (K)"] + ["SL (m/s)"] + ["delta (m)"] + ["CO_ppmvd"] + ["NO_ppmvd"] + ["NO2_ppmvd"] + ["NOx_ppmvd"] + ["NO/NO2_ppmvd"] + species_names
    solution   = [list(original_data.values[i]) + [temp[i]]+ [SL[i]] + [delta[i]] + [co[i]] + [no[i]] + [no2[i]] + [nox[i]] + [no_no2[i]] + list(x[i]) for i in range(len(original_data))]
    write(original_data, csv_file, excel_file, header, solution)

def zeroD_extinction(data_name, specifier, mech, T_inlet, P_inlet, func_):

    fuel_list, ER, original_data, fuel_data = call_data_reader(specifier, data_name)
    gas = ct.Solution(mech)
    species_names = [i + '_b' for i in gas.species_names]
    tau, x, temp, co, nox, no_no2, no, no2, cnt, hrr, data_values = list_creator(func_)
    os.system('mkdir 0D_extinction')
    ###############################complex save data
    print ("*************")
    for i in range(len(fuel_list)):
        print ("Doing calculation for data {}.".format(i+1))
        gas.TP  = float(T_inlet), float(P_inlet)
        gas.set_equivalence_ratio(ER[i], fuel_list[i] , 'O2:0.21, N2:0.79')

        t1 = ct.Reservoir(contents = gas, name = 'inlet')     #tank1/inlet
        t2 = ct.Reservoir(contents = gas, name = 'exhaust')   #tank2/exhaust

        residence_time_r1 = 0.001
        gas.equilibrate('HP')
        r1 = ct.IdealGasReactor(contents = gas, name = 'PSR', energy='on')

        def mdot_inlet(t):
            return r1.mass / residence_time_r1

        inlet_to_PSR   = ct.MassFlowController(t1, r1, mdot=mdot_inlet)
        PSR_to_exhaust = ct.PressureController(r1, t2, master = inlet_to_PSR, K=0.01)

        sim = ct.ReactorNet([r1])

        # Run a loop over decreasing residence times, until the reactor is extinguished,
        # saving the state after each iteration.
        states = ct.SolutionArray(gas, extra=['tres', 'HRR', 'CO_ppmvd', 'NOx_ppmvd', 'NO_ppmvd', 'NO2_ppmvd', 'NO_NO2_ppmvd'])
        sim.advance_to_steady_state()

        while abs(r1.T - float(T_inlet)) <= 100:
            print ("No combustion at tres = {}s, T = {}K,\nScaling...".format(residence_time_r1, r1.T))
            #automatic update residence_time to increase speed by 10 times.
            residence_time_r1, r1, t1, t2 = update(residence_time_r1, gas, T_inlet, P_inlet, ER, fuel_list, i)
            inlet_to_PSR   = ct.MassFlowController(t1, r1, mdot=mdot_inlet)
            PSR_to_exhaust = ct.PressureController(r1, t2, master = inlet_to_PSR, K=0.01)
            sim = ct.ReactorNet([r1])
            sim.advance_to_steady_state()

        print ("Combustion activated at tres = {}s, T = {}K,\nLooking for extinction time...".format(residence_time_r1, r1.T))

        while r1.T > float(T_inlet)+200:
            sim.set_initial_time(0.0)  # reset the integrator
            sim.advance_to_steady_state()
            CO_ppmvd,NOx_ppmvd,NO_NO2_ppmvd, NO_ppmvd, NO2_ppmvd = X_ppmvd(r1, gas)
            states.append(r1.thermo.state, tres=residence_time_r1, HRR = get_heat_release(r1), CO_ppmvd = CO_ppmvd, NOx_ppmvd = NOx_ppmvd, NO_ppmvd = NO_ppmvd, NO2_ppmvd = NO2_ppmvd, NO_NO2_ppmvd = NO_NO2_ppmvd)
            residence_time_r1 *= 0.99

        # Heat release rate [W/m^3]
        #Q = - np.sum(states.net_production_rates * states.partial_molar_enthalpies, axis=1)
        print ('Extinction time for data {} = {}s'.format(i+1, states.tres[-2]))

        tau.append(states.tres[-2])
        x.append(states.X[-2,:])
        temp.append(states.T[-2])
        co.append(states.CO_ppmvd[-2])
        nox.append(states.NOx_ppmvd[-2])
        no_no2.append(states.NO_NO2_ppmvd[-2])
        no.append(states.NO_ppmvd[-2])   
        no2.append(states.NO2_ppmvd[-2]) 
        hrr.append(states.HRR[-2])   

        #states.write_csv('somefile.csv', cols=('T','P','X','net_rates_of_progress'))

        print('Solution written for data {}\n*************'.format(i+1))
        dir1 = './0D_extinction/reactor{}.csv'.format(i+1)

        states.write_csv(dir1, cols=('tres', 'HRR', 'T','P','X'))

    csv_file   = "0D_extinction.csv"   
    excel_file = "0D_extinction.xlsx"
    header     = list(original_data.columns.values) + ["T_b (K)"] + ["tres (s)"] + ["HRR (W/m-3)"] + ["CO_ppmvd"] + ["NO_ppmvd"] + ["NO2_ppmvd"] + ["NOx_ppmvd"] + ["NO/NO2_ppmvd"] + species_names
    solution   = [list(original_data.values[i]) + [temp[i]] + [tau[i]] + [hrr[i]] + [co[i]] + [no[i]] + [no2[i]] + [nox[i]] + [no_no2[i]] + list(x[i]) for i in range(len(original_data))]
    write(original_data, csv_file, excel_file, header, solution)

    ##############################simplified save data
    if input('Choose wheter to export a simplified datasets [yes/no)] ') == 'yes':
        base_tau = tau.copy()
        tau, x, temp, co, nox, no_no2, no, no2, cnt, hrr, data_values = list_creator(func_)

        for i in range(len(fuel_list)):
            gas.TP  = float(T_inlet), float(P_inlet)
            gas.set_equivalence_ratio(ER[i], fuel_list[i] , 'O2:0.21, N2:0.79')

            t1 = ct.Reservoir(contents = gas, name = 'inlet')     #tank1/inlet
            t2 = ct.Reservoir(contents = gas, name = 'exhaust')   #tank2/exhaust

            residence_time_r1 = 128 * base_tau[i]
            final_residence_time = base_tau[i] / 2

            gas.equilibrate('HP')
            r1 = ct.IdealGasReactor(contents = gas, name = 'PSR', energy='on')

            def mdot_inlet2(t):
                return r1.mass / residence_time_r1

            inlet_to_PSR   = ct.MassFlowController(t1, r1, mdot=mdot_inlet2)
            PSR_to_exhaust = ct.PressureController(r1, t2, master = inlet_to_PSR, K=0.01)

            sim = ct.ReactorNet([r1])

            # Run a loop over increasing residence times, until the reactor reach final residence time,
            # saving the state after each iteration.

            count = 128
            while residence_time_r1 > final_residence_time:
                sim.set_initial_time(0.0)  # reset the integrator
                sim.advance_to_steady_state()

                CO_ppmvd,NOx_ppmvd,NO_NO2_ppmvd, NO_ppmvd, NO2_ppmvd = X_ppmvd(r1, gas)

                tau.append(residence_time_r1)
                temp.append(r1.thermo.T)
                co.append(CO_ppmvd)
                nox.append(NOx_ppmvd)
                no_no2.append(NO_NO2_ppmvd)   
                no.append(NO_ppmvd)   
                no2.append(NO2_ppmvd)   
                cnt.append(count)
                hrr.append(get_heat_release(r1))   
                data_values.append(original_data.values[i])

                residence_time_r1 *= 0.5
                count *= 0.5

        csv_file   = "0D_extinction_simplified.csv"      
        excel_file = "0D_extinction_simplified.xlsx"
        header     = list(original_data.columns.values) + ["T_b (K)"] + ["cnt"] + ["tres (s)"] + ["HRR (W/m-3)"] + ["CO_ppmvd"] + ["NO_ppmvd"] + ["NO2_ppmvd"] + ["NOx_ppmvd"] + ["NO/NO2_ppmvd"]
        solution   = [list(data_values[i]) + [temp[i]] + [cnt[i]] + [tau[i]] + [hrr[i]] + [co[i]] + [no[i]] + [no2[i]] + [nox[i]] + [no_no2[i]] for i in range(len(data_values))]
        write(data_values, csv_file, excel_file, header, solution)
    else:
        exit ()

##########################################################################
#def zeroD_extinction():
#def zeroD_ignition():

########################################################################
if __name__ == '__main__':

    import sys
    import os
    import cantera as ct
    #from tools import *
    from tools import *
    try:
        func_, data_name, specifier, T_inlet, P_inlet, mech = variables
    except:
      print("Program Quit!")
      exit()

    mech = "./Mechanisms/" + mech
    if func_ == "Equilibrium":
        Equilibrium(data_name, specifier, mech, T_inlet, P_inlet, func_)
    elif func_ =="1D_flame":
        get_flame_speed(data_name, specifier, mech, T_inlet, P_inlet, func_)
    elif func_ =="0D_extinction":
        zeroD_extinction(data_name, specifier, mech, T_inlet, P_inlet, func_)
    elif func_ =="General":
        General(data_name, specifier, mech, T_inlet, P_inlet, func_)
    else:
        print ()
        print ("Non-existing .exe program!!")
        exit()

