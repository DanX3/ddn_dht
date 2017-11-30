i=1
field=S_HDD_DATA_WRITE_MBps
for val in 150 512 1024 2048 4096; do
    sed -i "s/$field.*/$field = $val/g" $i/config
    echo "Set $field = $val to test $i"
    i=`expr $i + 1`
done

i=1
field=S_HDD_DATA_READ_MBps
for val in 300 1024 2048 4096 8192; do
    sed -i "s/$field.*/$field = $val/g" $i/config
    echo "Set $field = $val to test $i"
    i=`expr $i + 1`
done
