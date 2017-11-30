# setting the range of the plot, auto by default
# set xrange [0:16]
set autoscale
set yrange [8e8:1e10]

# axis settings
set title 'Disk Bandwidth Experiment'
set xlabel 'Write Bandwidth'
set ylabel 'Time (ns)'
set log y
# set log x
# set xtics rotate by 45 offset -4,-2

# set the legend on the top left corner
#set key left top

# style settings
set style line 1 linecolor rgb '#2196f3' linetype 1 linewidth 3 pt 7 ps 2
set style line 2 linecolor rgb '#ff9800' linetype 1 linewidth 3 pt 7 ps 2
set terminal pngcairo size 800,600 enhanced font 'Helvetica,12'
# set terminal svg size 800,600 fname 'Verdana' fsize 10
set grid

set output "plot.png"
plot 'results_1.dat' using 1:2 title 'Write time 1 Disk' with linespoints ls 1, \
     'results_4.dat' using 1:2 title 'Write time 4 Disks' with linespoints ls 1 lc rgb '#1976d2', \
     'results_8.dat' using 1:2 title 'Write time 8 Disks' with linespoints ls 1 lc rgb '#1565c0' ,\
     'results_20.dat' using 1:2 title 'Write time 20 Disks' with linespoints ls 1 lc rgb '#0d47a1' ,\
     'results_1.dat' using 1:3 title 'Read time 1 Disk' with linespoints ls 2, \
     'results_4.dat' using 1:3 title 'Read time 4 Disks' with linespoints ls 2 lc rgb '#fb8c00', \
     'results_8.dat' using 1:3 title 'Read time 8 Disks' with linespoints ls 2 lc rgb '#f57c00', \
     'results_20.dat' using 1:3 title 'Read time 20 Disks' with linespoints ls 2 lc rgb '#ef6c00',


