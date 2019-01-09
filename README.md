# Counting train connections to UK stations

Very rough python module to input station codes into traintimes.org.uk website via URL and scrape the results to get connection details.
Probably shouldn't be used too much as each run requires sending a website query for every single UK rail station.
It also takes forever to run and has a number of issues with the calculations.

## Requirements

Written in python3.7, I haven't checked compatibility with previous versions.
Uses numpy, csv, pickle, selenium and itertools. Also as coded requires PhantomJS webdriver, though should work with Firefox or Chrome if the webdriver variable is changed.

## What does it do?

Using the default set up, creates a URL for the traintimes.org.uk route planner between every UK rail station (using standard 3 letter codes contained in [station_codes.csv](station_codes.csv) ) and London termini, on 12th Feb 2019 (randomly chosen to represent a standard weekday), arriving before 2359. Then opens that URL in a headless browser, runs the javascript on the page, and scrapes the text from that page looking for either the 'direct;' string indicating there is a direct service, or a 'change</a>' string indicating a single change if a direct service isn't found. It's bodged together but it sort of works.

## Issues
I'm pretty confident that the direct services number is near the accurate number, however the one/two stop figures might have some slight issues due to the data I've scraped being optimised for speed of travel and routing guidance as it's a timetabling site.

For example, it shows SEC, Seaton Carew as two stops, as this is the quickest route (going via Thornaby and Darlington/York). However one could go via Newcastle or Hartlepool and do the trip in one stop.

Transferring on foot between stations (e.g. Wigan Wallgate to Wigan North Western) counts as two changes on most ticketing sites, so this also potentially skews some station data depending on how tight your criteria are.

This was just run on one week day in February for services arriving before midnight, so stations requiring sleepers and stations with weekend-only or parliamentary services may also have been mistakenly classified in the 2+ category, e.g. Thurso or Denton.

I've tried to fix some of this by checking 2+ stop/no connection stations with services departing at 0000, and also incrementing the date on error/no connections to possibly catch parliamentary trains.
It's also fantastically slow (took about 2h to run on an old-ish i7 laptopand a decent internet connection) and probably against the website's terms of use.

## Why?

See [this](https://twitter.com/undertheraedar/status/1081979354958172160) tweet.

## Usage

Do what you like with this, feel free to improve and muck about with it. It should be easy to run this for other stations or times, parameters in the URL just require changing. I take no responsibility for people getting banned from the website involved by using this code, it probably violates their terms of use, so don't run it too often.

I've now packed it up into a module ( [connection_count.py](connection_count.py) ) so it can be run with any station/list of termini, and the date/time are easier to change.

For example, to run for london:
    
    import connection_count as cc
    cc.count(destination='london',
          terminals=[
              'BFR', 'CST', 'CHX', 'CTK', 'EUS', 'FST', 'KGX', 'LST', 'LBG',
              'MYB', 'MOG', 'OLD', 'PAD', 'STP', 'SPX', 'VXH', 'VIC', 'WAT',
              'WAE'
          ],
          year=2019,
          month=2,
          day=12,
          hhmm=2359,
          arrdep='a',
          inputpath='/path/to/folder/',
          outputpath='/path/to/folder/',
          repeat_on_error=10
          )

## Author
[Kieran Newman](https://github.com/mm14kwn)

[twitter](https://twitter.com/KW_Newman)

[email](mailto:newman.kieranw@gmail.com)
