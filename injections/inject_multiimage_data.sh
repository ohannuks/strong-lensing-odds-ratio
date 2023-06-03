INJECTION=$1

injectdata () {
  injection=$1
  # Get the 4 image filenames
  imagenumber=0
  fnameout="injection_${injection}_multiimage"
  fname0="injection_${injection}_image_0"
  fname1="injection_${injection}_image_1"
  fname2="injection_${injection}_image_2"
  fname3="injection_${injection}_image_3"
  # Now run golum_inject
  # Usage: golum_inject output m1 m2 chi1 chi2 dist tc phic inclination polarization ra dec imagetype snr
  golum_inject_multiimage $fnameout $fname0 $fname1 $fname2 $fname3
}
injectdata "${INJECTION}"

