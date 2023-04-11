
injectdata () {
  injection=$1
  imagenumber=$2
  output=$(python3 read_injection_data.py detectable_lensed_event_parameters_resampled_TLU.txt ${injection} ${imagenumber})
  echo "injecting injection ${injection} image ${imagenumber}"
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
  # Now run flowmc_inject to inject and run the injection with flowmc
  # Usage: flowmc_inject output m1 m2 chi1 chi2 dist tc phic inclination polarization ra dec
  # Usage: XLA_PYTHON_CLIENT_PREALLOCATE=false flowmc_inject pe1 35 30 0.3 -0.4 400 0.02 0.1 0.5 0.2 1.2 0.3
  XLA_PYTHON_CLIENT_PREALLOCATE=false flowmc_inject pe${injection}_${imagenumber} ${mass1} ${mass2} ${a1} ${a2} ${effective_luminosity_distance} ${effective_geocent_time} ${effective_phase} ${iota} ${psi} ${ra} ${dec}
  echo ""
}
injectdata "3" "0"
injectdata "3" "1"
injectdata "3" "2"
injectdata "3" "3"

