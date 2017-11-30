i=1
field=S_HDD_DATA_WRITE_MBps
for val in `cat dataset`; do
    sed -i "s/$field.*/$field = $val/g" $i/config
    echo "Set $field = $val to test $i"
    i=`expr $i + 1`
done

i=1
field=S_HDD_DATA_READ_MBps
for val in `cat dataset`; do
    val=`echo "$val * 2" | bc`
    sed -i "s/$field.*/$field = $val/g" $i/config
    echo "Set $field = $val to test $i"
    i=`expr $i + 1`
done
