all: injectiondata

injectiondata: injections/detectable_lensed_event_parameters_resampled_TLU.txt

# Create injections
injections/detectable_lensed_event_parameters_resampled_TLU.txt: injections/create_lensed_injections.py
	cd injections && python3 create_lensed_injections.py && touch *.txt
	cd ..



# Note: Make sure that LeR and quintet are installed; tested with the 'base' conda environment
