input="$(pwd)/output/code/code.c"
topl="$(pwd)/output/topl/test.topl"

infer --topl --topl-properties  $input_dir/$topl -- gcc -c $input