i=1
field=M_BUCKET_SIZE
for val in `cat dataset`; do
    sed -i "s/$field.*/$field = $val/g" $i/config
    echo "Set $field = $val to test $i"
    i=`expr $i + 1`
done
