i=1
field=C_GEOMETRY_BASE
for val in 2 4 6 8 10 ; do
    sed -i "s/$field.*/$field = $val/g" $i/config
    echo "Set $field = $val to test $i"
    i=`expr $i + 1`
done
