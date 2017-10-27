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
set style line 1 linecolor rgb '#2196f3' pointtype 20 ps 1
set style line 2 linecolor rgb '#f44336' pointtype 13 pointsize 1
set style line 3 linecolor rgb '#4caf50' linetype 7 linewidth 10
 #set style line 2 linecolor rgb '# 2196F3' pointtype 7 pointsize 2
set terminal svg enhanced size 800,600 fname 'Sans' fsize 16
set grid

#clients_logs = system("ls logs/*client.log")
#plot for [client_log in clients_logs] client_log using 1:xtic(2) ls 1  title 'client profile'
set title 'Client profile'
set output "client.svg"
#plot 'logs/10_1_100M-client.log' using 1:xtic(2) ls 1  title '10\_1\_100M', \
     #'logs/1_1_1G-client.log' using 1:xtic(2) ls 2  title '1\_1\_1G'
plot 'logs/many_small-client.log' using 1:xtic(2) ls 1 title 'small', \
     'logs/many_smaller-client.log' using 1:xtic(2) ls 2  title 'smaller', \
   

set title 'Server profile'
set output "server.svg"
#plot 'logs/10_1_100M-server.log' using 1:xtic(2) ls 1 title '10\_1\_100M', \
     #'logs/1_1_1G-server.log' using 1:xtic(2) ls 2 title '1\_1\_1G'
plot 'logs/many_small-server.log' using 1:xtic(2) ls 1  title 'small', \
     'logs/many_smaller-server.log' using 1:xtic(2) ls 2  title 'smaller'

set title 'Manager profile'
set output "manager.svg"
#plot 'logs/10_1_100M-manager.log' using 1:xtic(2) ls 1 title '10\_1\_100M', \
     #'logs/1_1_1G-manager.log' using 1:xtic(2) ls 2 title '1\_1\_1G'

plot 'logs/many_small-manager.log' using 1:xtic(2) ls 1 title 'small', \
     'logs/many_smaller-manager.log' using 1:xtic(2) ls 2 title 'smaller' 

set title 'Objects count'
set output "objects.svg"
plot 'logs/many_small-objects.log' using 1:xtic(2) ls 1 title 'small', \
     'logs/many_smaller-objects.log' using 1:xtic(2) ls 2 title 'smaller' 
