#setting the range of the plot, auto by default
#set xrange [-1:1]
#set yrange [0:16]
set autoscale

#axis settings
set title 'Title'
set xlabel 'X axis'
set ylabel 'Y axis'
#set log y
#set log x
#set xtics rotate by 45 offset -4,-2
#set format x "%T"

#set the legend on the top left corner
set key left top

#style settings
set style line 1 linecolor rgb '#0060ad' linetype 2 linewidth 3
set style line 2 linecolor rgb '#2196f3' pointtype 7 pointsize 1 linewidth 3
set style line 3 linecolor rgb '#f44336' pointtype 7 pointsize 1 linewidth 3
set style line 4 linecolor rgb '#4caf50' pointtype 7 pointsize 1 linewidth 3
set style line 5 linecolor rgb '#ff9800' pointtype 7 pointsize 1 linewidth 3
set terminal pngcairo size 800,600 enhanced font 'Helvetica,12'
set grid

set output "functions.png"
f(x) = sin(x/(2*pi))**2 #*sin(x/(2*pi))
plot f(x) with lines ls 2 ,\
