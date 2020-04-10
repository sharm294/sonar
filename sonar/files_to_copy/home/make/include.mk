ifndef SONAR_REPO
$(error SONAR_PATH not set in env -- did you activate this repository?)
endif

# ifndef SHOAL_HLS_PATH
# $(error SHOAL_HLS_PATH not set in env -- must be set to the absolute path of \
# of the Vivado HLS directory. Did you source init.sh?)
# endif

ifndef SONAR_PART
$(error SONAR_PART not set in env -- did you activate a board?)
endif

# Asserts that the specified variable exists. It can be used as a prerequisite
# for running other targets. E.g. adding guard-FOO to a target enforces that
# the variable FOO is defined before running the target.

guard-%:
	@ if [ "${${*}}" = "" ]; then \
		echo "Variable $* not set"; \
		exit 1; \
	fi
