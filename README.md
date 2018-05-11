# Basketball Stats

This project pretends obtain detailed basketball match stats using the `.xml` feeds provided by[My Sports Feeds](https://www.mysportsfeeds.com/).


## Getting Started

### Installing

1. Install prerequisites.
```
conda install --yes --file requirements.txt
```


2. Clone the repository.
```
git clone https://github.com/aleix11alcacer/basketball-data-scrapper.git
```

### Usage


1. Create a database. By default, the database name is `basketball_stats`.
```
python database-creation.py
```

2. Download the `.xml` files that you want introduce to database from My Sports Feeds using his API. Don't change the file name because it's used in `scrapper.py`. The file must be into a folder called `data`.

```
python download-match.py
```

5. Introduce data into database.
```
python scrapper.py file_name season_id
```

6. The file `example.py` contains the basic operations to obtain and plot data from the database. The result will be saved into a folder called `results`.

```
python example.py
```

7. Make your own basketball statistics. ENJOY!

## Notes

### Competitions id

- 1: English Premier League
- 2: Spanish La Liga
- 3: German Bundesliga
- 4: Italian Serie A
- 5: French Ligue 1
- 6: Dutch Eredivisie
- 7: English Championship
- 8: US Major League Soccer