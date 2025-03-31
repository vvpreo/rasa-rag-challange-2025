#! /bin/sh

ooo="$@"

echo "STARTING"
rasa llm finetune prepare-data --num-rephrases 1 --train-frac 0.8 --output-format instruction --out "$ooo/output" $ooo
echo "DONE"
