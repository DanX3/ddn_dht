i=1
field=S_SERVER_COUNT
for val in 10 50 250 1000 3000; do
    sed -i "s/$field.*/$field = $val/g" $i/config
    echo "Set $field = $val to test $i"
    i=`expr $i + 1`
done
