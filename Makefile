all: csv web

csv:
	./main.py --path $(dest)/cases.csv --format csv

web:
	cd $(source)/website && hugo
