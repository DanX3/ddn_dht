#setting the range of the plot, auto by default
#set xrange [-1:1]
#set yrange [0:16]
set autoscale

#axis settings
set log y
set log x
#set xtics rotate by 45 offset -4,-2
#set format x "%T"

#set the legend on the top left corner
set key left top

#style settings
set style line 1 linecolor rgb '#0060ad' linetype 2 linewidth 3
set style line 2 linecolor rgb '#2196f3' pointtype 7 pointsize 1 linewidth 2
set style line 3 linecolor rgb '#f44336' pointtype 7 pointsize 1 linewidth 2
set style line 4 linecolor rgb '#4caf50' pointtype 7 pointsize 1 linewidth 2
set style line 5 linecolor rgb '#ff9800' pointtype 7 pointsize 1 linewidth 2
#set terminal pngcairo size 800,600 enhanced font 'Helvetica Neue,16'
set terminal svg size 800,600 enhanced font 'Helvetica,20'linewidth 2
set grid

set output "walltime.svg"
set title 'Network write Time'
set xlabel 'Packet Size (MB)'
set ylabel 'Walltime (s)'
plot  "model.dat"  using 1:2 title "Total time" with lines ls 2 ,\
      "model.dat"  using 1:3 title "Overhead" with lines ls 3

set output "efficiency.svg"
set title 'Efficiency'
set yrange [0:1300]
set xlabel 'Packet Size (MB)'
set ylabel 'Efficiency over 1000 (Max bandwidth)'
set key left top
unset log y
f(x) = 1000
plot  "model.dat"  using 1:($1/$2) title "Efficiency" with lines ls 2 ,\
      f(x) title "Bandwidth Limit" with lines ls 3
