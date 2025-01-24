#!/usr/bin/env sh

# Cleanup any extra BK_ env that would have been set external
for VAR in `env | cut -d '=' -f 1`
do
    case $VAR in BK_*)
        echo "Unsetting external $VAR"
        unset "$VAR"
    esac
done

if [ -f ".env" ]
then
    set -a
    source ".env"

    # Backward compatibility, RANDOM should not be used as an environment variable
    # It is a magic variable maintained by some shells
    if grep -q -i "^RANDOM=" ".env"
    then
        echo "You shouldn't use the RANDOM magic variable in your environment. Exporting BK_RANDOM instead."
        export BK_RANDOM=`grep -m 1 -i "^RANDOM=" ".env" | cut -d "=" -f 2`
    fi
fi

python3 app.py
