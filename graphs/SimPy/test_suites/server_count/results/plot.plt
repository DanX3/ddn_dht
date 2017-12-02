# setting the range of the plot, auto by default
# set xrange [0:16]
# set yrange [0:16]
set autoscale

# axis settings
set title 'Server Count Experiment'
set xlabel 'Server Count'
set ylabel 'Time (ns)'
set log y
set log x
# set xtics rotate by 45 offset -4,-2

# set the legend on the top left corner
#set key left top

# style settings
set style line 1 linecolor rgb '#0060ad' linetype 1 linewidth 3 pt 7 ps 2
set style line 2 linecolor rgb '#ff9800' linetype 1 linewidth 3 pt 7 ps 2
set style line 3 linecolor rgb '#4caf50' linetype 1 linewidth 3 pt 7 ps 2
set terminal pngcairo size 800,600 enhanced font 'Helvetica,12'
# set terminal svg size 800,600 fname 'Verdana' fsize 10
set grid

set output "plot.png"
plot 'results.dat' using 1:5 title 'Write 256GB' with linespoints ls 1 pt 13, \
     'results.dat' using 1:6 title 'Read 256GB' with linespoints ls 2 pt 13 ps 4, \
     'results.dat' using 1:7 title 'Recovery 256GB' with linespoints ls 3 pt 13, \
     'results.dat' using 1:2 title 'Write 8GB' with linespoints ls 1, \
     'results.dat' using 1:3 title 'Read 8GB' with linespoints ls 2, \
     'results.dat' using 1:4 title 'Recovery 8GB' with linespoints ls 3, \


