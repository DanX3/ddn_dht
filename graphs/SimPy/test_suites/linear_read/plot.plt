# setting the range of the plot, auto by default
# set xrange [0:16]
# set yrange [0:16]
set autoscale

# axis settings
set ylabel 'Time (ns)'
set log y
# set log x
set xtics rotate by -45 # offset -4,-2

# set the legend on the top left corner
set key outside box #left top

# style settings
# set palette model RGB defined (0 "#ff9800", 1 "#1976d2")
unset colorbox
# set style fill solid 0.5 border lt -1
# set style data histograms
# set style histogram clustered
set style line 1 linecolor rgb '#2196f3' pointtype 20 pointsize 1
set style line 2 lc rgb '#f44336' pt 13 ps 1
set style line 3 lc rgb '#4caf50' pt 15 ps 1
set style line 4 lc rgb '#673ab7' pt 22 ps 1
set style line 5 lc rgb '#009688' pt 11 ps 1
 #set style line 2 linecolor rgb '# 2196F3' pointtype 7 pointsize 2
set terminal svg enhanced size 800,600 fname 'Sans' fsize 16
set grid

#clients_logs = system("ls logs/*client.log")
#plot for [client_log in clients_logs] client_log using 1:xtic(2) ls 1  title 'client profile'
set title 'Client profile'
set output "client.svg"
plot '1/client.log' using 1:xtic(2) ls 1 title '1', \
     '2/client.log' using 1:xtic(2) ls 2 title '2', \
     '3/client.log' using 1:xtic(2) ls 3 title '3', \
     '4/client.log' using 1:xtic(2) ls 4 title '4', \
     '5/client.log' using 1:xtic(2) ls 5 title '5', \
     '6/client.log' using 1:xtic(2) ls 6 title '6'

set title 'Server profile'
set output "server.svg"
plot '1/server.log' using 1:xtic(2) ls 1 title '1', \
     '2/server.log' using 1:xtic(2) ls 2 title '2', \
     '3/server.log' using 1:xtic(2) ls 3 title '3', \
     '4/server.log' using 1:xtic(2) ls 4 title '4', \
     '5/server.log' using 1:xtic(2) ls 5 title '5', \
     '6/server.log' using 1:xtic(2) ls 6 title '6'

set title 'Manager profile'
set output "manager.svg"
plot '1/manager.log' using 1:xtic(2) ls 1 title '1', \
     '2/manager.log' using 1:xtic(2) ls 2 title '2', \
     '3/manager.log' using 1:xtic(2) ls 3 title '3', \
     '4/manager.log' using 1:xtic(2) ls 4 title '4', \
     '5/manager.log' using 1:xtic(2) ls 5 title '5', \
     '6/manager.log' using 1:xtic(2) ls 6 title '6'

set title 'Objects count'
set output "objects.svg"
set terminal svg enhanced size 1200,600 fname 'Sans' fsize 16
plot '1/objects.log' using 1:xtic(2) ls 1 title '1', \
     '2/objects.log' using 1:xtic(2) ls 2 title '2', \
     '3/objects.log' using 1:xtic(2) ls 3 title '3', \
     '4/objects.log' using 1:xtic(2) ls 4 title '4', \
     '5/objects.log' using 1:xtic(2) ls 5 title '5' , \
     '6/objects.log' using 1:xtic(2) ls 6 title '6' 
