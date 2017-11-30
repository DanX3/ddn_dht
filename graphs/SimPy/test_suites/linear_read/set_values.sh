i=1
field=M_READ_BLOCK_SIZE
for val in 4 8 16 32 64; do
    sed -i "s/$field.*/$field = $val/g" $i/config
    echo "Set $field = $val to test $i"
    i=`expr $i + 1`
done
