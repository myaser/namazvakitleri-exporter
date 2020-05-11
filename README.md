# namazvakitleri-exporter

extract prayer times from `namazvakitleri.diyanet.gov.tr` to iCalendar file, so you can integrate it with your favorite Calendar application

it was built very quick and dirty for my own use, so do not expect much of it

## usage

1. go to [namazvakitleri](http://namazvakitleri.diyanet.gov.tr/en-US) website and find the city you need the prayer times for, note the code in the url `http://namazvakitleri.diyanet.gov.tr/en-US/{code}` this is the city code we will use

2. in your favourite calendar application subscripe to the link `https://prayer-times-namazvakitleri.herokuapp.com/{code}?tz={timezone}`

example: `https://prayer-times-namazvakitleri.herokuapp.com/11002?tz=Europe/Berlin` for berlin

## TODO

1. make it more user friendly (automatically figureout the right timezone and city code)

2. namazvakitleri website only displays events for 30 days starting today, so the past is always removed. probably will actively scrap the website and keep a copy of the prayer times to maintain history
