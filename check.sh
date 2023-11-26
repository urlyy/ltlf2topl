input_dir="mytest/infer/1"
filename="main_output_infer.c"
toplname="test.topl"

infer --topl --topl-properties  $input_dir/$toplname -- gcc -c $input_dir/$filename