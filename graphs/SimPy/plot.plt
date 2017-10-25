# setting the range of the plot, auto by default
# set xrange [0:16]
# set yrange [0:16]
set autoscale

# axis settings
set title 'Client profile'
set ylabel 'Time (us)'
set log y
# set log x
set xtics rotate by -45 # offset -4,-2

# set the legend on the top left corner
set key left top

# style settings
# set palette model RGB defined (0 "#ff9800", 1 "#1976d2")
unset colorbox
# set style fill solid 0.5 border lt -1
# set style data histograms
# set style histogram clustered
set style line 1 linecolor rgb '#0060ad' linetype 7 linewidth 10
# set style line 2 linecolor rgb '# 2196F3' pointtype 7 pointsize 2
set terminal svg size 800,600 fname 'Sans' fsize 16
set grid

clients_logs = system("ls logs/*client.log")
set output "client.svg"
plot for [client_log in clients_logs] client_log using 1:xtic(2) ls 1  title 'client profile'

# set output "server.svg"
# plot 'logs/server*.log' using 1:xtic(2) title 'server profile'

# set output "manager.svg"
# plot 'logs/manager*.log' using 1:xtic(2) title 'manager profile'
