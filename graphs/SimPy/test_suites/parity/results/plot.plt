# setting the range of the plot, auto by default
# set xrange [0:16]
# set yrange [0:16]
set autoscale

# axis settings
set title 'Geometry Experiment'
set xlabel 'Geometry Base'
set ylabel 'Time (ns)'
set log y
# set log x
# set xtics rotate by 45 offset -4,-2

# set the legend on the top left corner
#set key left top

# style settings
set style line 1 linecolor rgb '#0060ad' linetype 1 linewidth 3 pt 7 ps 2
set style line 2 linecolor rgb '#ff9800' linetype 1 linewidth 3 pt 7 ps 2
set terminal pngcairo size 800,600 enhanced font 'Helvetica,12'
# set terminal svg size 800,600 fname 'Verdana' fsize 10
set grid

set output "plot.png"
plot 'results.dat' using 1:2 title 'Allocation time' with linespoints ls 1, \
     'results.dat' using 1:3 title 'Restore time' with linespoints ls 2

