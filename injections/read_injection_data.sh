

output=$(python3 read_injection_data.py detectable_lensed_event_parameters_resampled_TLU.txt 3 3)
echo $output
outputarray=($output)
mass1=${outputarray[0]}
mass2=${outputarray[1]}
a1=${outputarray[2]}
a2=${outputarray[3]}
effective_luminosity_distance=${outputarray[4]}
effective_geocent_time=${outputarray[5]}
effective_phase=${outputarray[6]}
iota=${outputarray[7]}
psi=${outputarray[8]}
ra=${outputarray[9]}
dec=${outputarray[10]}
snr_opt_snr_net=${outputarray[11]}

echo "mass_1 mass_2 a_1 a_2 effective_luminosity_distance effective_geocent_time effective_phase iota psi ra dec snr_opt_snr_net"
echo $mass1 $mass2 $a1 $a2 $effective_luminosity_distance $effective_geocent_time $effective_phase $iota $psi $ra $dec $snr_opt_snr_net


