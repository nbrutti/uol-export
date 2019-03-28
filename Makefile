all:
	mkdir -p output/
	python3 -b src/main.py

clean:
	rm -rf logs.txt output/*.db output/*.json output/*.db-journal
