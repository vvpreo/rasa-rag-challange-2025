#! /bin/sh

ooo="$@"
_type='conversational'
echo "STARTING"
rasa llm finetune prepare-data --num-rephrases 1 --train-frac 0.8 --output-format $_type --out "$ooo/output_$_type" $ooo
echo "DONE"
